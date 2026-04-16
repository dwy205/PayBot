import hashlib
import hmac
import time
from dataclasses import dataclass
from random import randint
from typing import Any

import requests


@dataclass(frozen=True)
class PaymentInfo:
    order_code: int
    checkout_url: str
    qr_code_text: str


class PayOSService:
    def __init__(
        self,
        client_id: str,
        api_key: str,
        checksum_key: str,
        return_url: str,
        cancel_url: str,
    ) -> None:
        self.client_id = client_id
        self.api_key = api_key
        self.checksum_key = checksum_key
        self.return_url = return_url
        self.cancel_url = cancel_url
        self.base_url = "https://api-merchant.payos.vn"

    def _headers(self) -> dict[str, str]:
        return {
            "x-client-id": self.client_id,
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
        }

    def _signature_data(self, amount: int, description: str, order_code: int) -> str:
        return (
            f"amount={amount}"
            f"&cancelUrl={self.cancel_url}"
            f"&description={description}"
            f"&orderCode={order_code}"
            f"&returnUrl={self.return_url}"
        )

    def _sign(self, text: str) -> str:
        return hmac.new(
            self.checksum_key.encode("utf-8"),
            text.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def new_order_code(self) -> int:
        return int(time.time()) + randint(1000, 9999)

    def create_payment(self, amount: int, description: str) -> PaymentInfo:
        order_code = self.new_order_code()
        signature_data = self._signature_data(amount=amount, description=description, order_code=order_code)
        body = {
            "orderCode": order_code,
            "amount": amount,
            "description": description,
            "returnUrl": self.return_url,
            "cancelUrl": self.cancel_url,
            "signature": self._sign(signature_data),
        }
        response = requests.post(
            f"{self.base_url}/v2/payment-requests",
            json=body,
            headers=self._headers(),
            timeout=20,
        )
        response.raise_for_status()
        payload: dict[str, Any] = response.json()
        data = payload.get("data", {})
        return PaymentInfo(
            order_code=order_code,
            checkout_url=str(data.get("checkoutUrl", "")),
            qr_code_text=str(data.get("qrCode", "")),
        )

    def is_paid(self, order_code: int) -> bool:
        response = requests.get(
            f"{self.base_url}/v2/payment-requests/{order_code}",
            headers=self._headers(),
            timeout=20,
        )
        response.raise_for_status()
        payload: dict[str, Any] = response.json()
        data = payload.get("data", {})
        status = str(data.get("status", "")).upper()
        return status == "PAID"
