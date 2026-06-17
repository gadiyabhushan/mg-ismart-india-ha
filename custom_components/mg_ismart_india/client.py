"""MG iSmart India cloud client."""

from __future__ import annotations

from binascii import unhexlify
from dataclasses import dataclass
import hashlib
import hmac
import json
import re
import time
from typing import Any
from urllib.parse import urlencode

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import httpx

from .bitcodec import BitReader, read_fixed_7bit_string, set_bits, set_fixed_7bit_string
from .const import GATEWAY_BASE_URL, TAP_LOGIN_URL, USER_AGENT

LOGIN_DISPATCHER_TEMPLATE_HEX = (
    "11005600882c60c183060c183060c183060c183060c183060c183060c183060c183060c183"
    "060c183060c183060c183060c1ab06200000000020200468acf134468acf1342468acf134"
    "2468acf1342000000000100a0"
)


class MgIndiaApiError(Exception):
    """Raised when the MG India API returns an error."""


@dataclass(frozen=True)
class MgIndiaVehicle:
    """Vehicle metadata returned by the India gateway."""

    vin: str
    brand_name: str | None = None
    model_name: str | None = None
    model_year: str | int | None = None
    series: str | None = None
    is_active: bool | None = None
    raw: dict[str, Any] | None = None


@dataclass(frozen=True)
class MgIndiaSnapshot:
    """Read-only data used by Home Assistant entities."""

    vehicle: MgIndiaVehicle
    user_language: str | None
    platform: str | None
    features: list[dict[str, Any]]
    service_subscription: dict[str, Any] | None
    co2_info: dict[str, Any] | None
    co2_supplement: dict[str, Any] | None
    last_update: float


class MgIndiaClient:
    """Client for MG iSmart India TAP login and gateway APIs."""

    def __init__(
        self,
        phone: str,
        password: str,
        *,
        vin: str | None = None,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self._phone = normalize_phone(phone)
        self._password = password
        self._vin = vin
        self._http = http_client or httpx.AsyncClient(timeout=30)
        self._owns_http = http_client is None
        self._token: str | None = None
        self._user_id: str | None = None
        self._device_id = make_device_id(self._phone)

    @property
    def vin(self) -> str | None:
        return self._vin

    async def close(self) -> None:
        if self._owns_http:
            await self._http.aclose()

    async def login(self) -> None:
        """Authenticate and store a fresh gateway token/user id."""

        body = self._build_login_body()
        headers = {
            "User-Agent": USER_AGENT,
            "Content-Type": "text/plain",
            "Accept": "*/*",
            "Accept-Language": "en-US;q=1",
            "APP-SIGNATURE": tap_signature(body),
            "SIGNATURE": "1",
        }
        response = await self._http.post(TAP_LOGIN_URL, content=body, headers=headers)
        response.raise_for_status()
        dispatcher, app = decode_tap_response(response.text)
        if not app:
            raise MgIndiaApiError("Login did not return a token payload")
        self._token = decode_login_token(app)
        user_id = read_fixed_7bit_string(dispatcher, bit_offset=300, char_count=14)
        self._user_id = user_id.rjust(50, "0")

    async def vehicles(self) -> list[MgIndiaVehicle]:
        await self._ensure_login()
        payload = await self.gateway_get("/vehicle/userVinList")
        vin_list = payload.get("data", {}).get("vinList", [])
        vehicles = [parse_vehicle(item) for item in vin_list if isinstance(item, dict)]
        if self._vin is None and vehicles:
            self._vin = vehicles[0].vin
        return vehicles

    async def snapshot(self) -> MgIndiaSnapshot:
        await self._ensure_login()
        vehicles = await self.vehicles()
        vehicle = self._select_vehicle(vehicles)
        user_info = await self.gateway_get("/user/account/userInfo")
        feature_resp = await self.gateway_get(
            "/vehicle/feature/list",
            {"vin": hashlib.sha256(vehicle.vin.encode()).hexdigest()},
        )
        service_subscription = await self._gateway_get_optional(
            "/vehicle/service/subscription", {"vin": vehicle.vin}
        )
        co2_info = await self._gateway_get_optional(
            "/navi/vehicle/co2info", {"vin": vehicle.vin}
        )
        co2_supplement = await self._gateway_get_optional(
            "/navi/vehicle/co2info/supplementInfo", {"vin": vehicle.vin}
        )
        data = feature_resp.get("data", {})
        return MgIndiaSnapshot(
            vehicle=vehicle,
            user_language=user_info.get("data", {}).get("userLanguageType"),
            platform=data.get("platform"),
            features=data.get("featureList", []) if isinstance(data, dict) else [],
            service_subscription=service_subscription,
            co2_info=co2_info,
            co2_supplement=co2_supplement,
            last_update=time.time(),
        )

    async def gateway_get(
        self, path: str, params: dict[str, str] | None = None
    ) -> dict[str, Any]:
        await self._ensure_login()
        response = await self._gateway_get_raw(path, params or {})
        parsed = json.loads(decrypt_gateway_body(response.text, response.headers))
        code = parsed.get("code")
        if code == 7:
            await self.login()
            response = await self._gateway_get_raw(path, params or {})
            parsed = json.loads(decrypt_gateway_body(response.text, response.headers))
            code = parsed.get("code")
        if code != 0:
            raise MgIndiaApiError(parsed.get("message", f"Gateway error code {code}"))
        return parsed

    async def _gateway_get_optional(
        self, path: str, params: dict[str, str] | None = None
    ) -> dict[str, Any] | None:
        try:
            return await self.gateway_get(path, params)
        except MgIndiaApiError:
            return None

    async def _gateway_get_raw(
        self, path: str, params: dict[str, str]
    ) -> httpx.Response:
        if self._token is None or self._user_id is None:
            raise MgIndiaApiError("Not logged in")
        clean_path = "/" + path.lstrip("/")
        query = urlencode(params)
        signing_path = clean_path + (f"?{query}" if query else "")
        timestamp = str(int(time.time() * 1000))
        content_type = "application/json"
        headers = {
            "User-Agent": USER_AGENT,
            "Content-Type": content_type,
            "APP-CONTENT-ENCRYPTED": "1",
            "APP-LANGUAGE-TYPE": "en-us",
            "APP-LOGIN-TOKEN": self._token,
            "APP-USER-ID": self._user_id,
            "APP-SEND-DATE": timestamp,
            "APP-VERIFICATION-STRING": gateway_signature(
                signing_path, timestamp, content_type
            ),
            "ORIGINAL-CONTENT-TYPE": content_type,
        }
        response = await self._http.get(
            f"{GATEWAY_BASE_URL}{clean_path}", params=params, headers=headers
        )
        response.raise_for_status()
        return response

    async def _ensure_login(self) -> None:
        if self._token is None or self._user_id is None:
            await self.login()

    def _build_login_body(self) -> str:
        dispatcher = bytearray.fromhex(LOGIN_DISPATCHER_TEMPLATE_HEX)
        app = encode_login_app(self._password, self._device_id)
        set_fixed_7bit_string(dispatcher, 48, self._phone.rjust(50, "0"))
        set_bits(dispatcher, 419, 32, int(time.time()))
        dispatcher[-7:-3] = (len(app) * 2).to_bytes(4, "big")
        dispatcher[-3] = 1
        dispatcher[-2:] = (160).to_bytes(2, "big")
        payload = bytes(dispatcher) + app
        raw_without_prefix = "1" + payload.hex().upper()
        return f"{len(raw_without_prefix) + 4:04X}{raw_without_prefix}"

    def _select_vehicle(self, vehicles: list[MgIndiaVehicle]) -> MgIndiaVehicle:
        if not vehicles:
            raise MgIndiaApiError("No vehicles returned by account")
        if self._vin is None:
            self._vin = vehicles[0].vin
            return vehicles[0]
        for vehicle in vehicles:
            if vehicle.vin == self._vin:
                return vehicle
        raise MgIndiaApiError("Configured VIN was not returned by account")


def normalize_phone(phone: str) -> str:
    digits = re.sub(r"\D+", "", phone)
    if len(digits) > 10:
        digits = digits[-10:]
    if len(digits) != 10:
        raise MgIndiaApiError("Phone must contain a 10-digit India mobile number")
    return digits


def make_device_id(phone: str) -> str:
    seed = hashlib.sha256(f"mg-ismart-india:{phone}".encode()).hexdigest()
    return (f"haos-mg-ismart-india-{seed}" + "0" * 120)[:103]


def encode_login_app(password: str, device_id: str) -> bytes:
    from .bitcodec import BitWriter

    writer = BitWriter()
    writer.write_bits(1, 1)
    writer.write_7bit_string(password, 6, 30)
    writer.write_7bit_string(device_id, 1, 200)
    return writer.to_bytes()


def decode_tap_response(raw: str) -> tuple[bytes, bytes]:
    if len(raw) < 5 or raw[4] != "1":
        raise MgIndiaApiError("Unexpected TAP response framing")
    payload = bytes.fromhex(raw[5:])
    if len(payload) < 4:
        raise MgIndiaApiError("TAP response payload is too short")
    dispatcher_len = payload[2] + (payload[3] << 8)
    return payload[:dispatcher_len], payload[dispatcher_len:]


def decode_login_token(app: bytes) -> str:
    reader = BitReader(app)
    reader.read_bits(6)
    token = reader.read_7bit_string(40, 40)
    refresh = reader.read_7bit_string(40, 40)
    if token != refresh:
        raise MgIndiaApiError("Login token and refresh token differ")
    return token


def tap_signature(body: str) -> str:
    key_material = body[1 : len(body) // 2]
    hmac_key = hashlib.md5(key_material.encode()).hexdigest()
    return hmac.new(hmac_key.encode(), body.encode(), hashlib.sha256).hexdigest()


def gateway_signature(signing_path: str, current_ts: str, content_type: str) -> str:
    key_part_one = md5_hex_digest(signing_path)
    encrypt_key = md5_hex_digest(key_part_one + current_ts + "1" + content_type)
    hmac_value = signing_path + current_ts + "1" + content_type
    hmac_key = md5_hex_digest(encrypt_key + current_ts)
    return hmac.new(
        hmac_key.encode(), msg=hmac_value.encode(), digestmod=hashlib.sha256
    ).hexdigest()


def decrypt_gateway_body(encrypted: str, headers: httpx.Headers) -> str:
    key = md5_hex_digest(headers["APP-SEND-DATE"] + "1" + headers["ORIGINAL-CONTENT-TYPE"])
    iv = md5_hex_digest(headers["APP-SEND-DATE"])
    cipher = AES.new(unhexlify(key), AES.MODE_CBC, unhexlify(iv))
    return unpad(cipher.decrypt(unhexlify(encrypted)), AES.block_size).decode("utf-8")


def md5_hex_digest(content: str) -> str:
    return hashlib.md5(content.encode()).hexdigest()


def parse_vehicle(raw: dict[str, Any]) -> MgIndiaVehicle:
    return MgIndiaVehicle(
        vin=raw["vin"],
        brand_name=raw.get("brandName"),
        model_name=raw.get("modelName"),
        model_year=raw.get("modelYear"),
        series=raw.get("series"),
        is_active=raw.get("isActivate"),
        raw=raw,
    )
