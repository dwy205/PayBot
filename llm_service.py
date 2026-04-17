import json
import re
from typing import Any, Dict

import google.generativeai as genai
from openai import OpenAI


class LLMService:
    def __init__(
        self,
        provider: str,
        model: str,
        openai_api_key: str = "",
        gemini_api_key: str = "",
    ) -> None:
        self.provider = provider.lower().strip()
        self.model = model
        self.openai_client = (
            OpenAI(api_key=openai_api_key)
            if self.provider == "openai" and openai_api_key
            else None
        )
        if self.provider == "gemini" and gemini_api_key:
            genai.configure(api_key=gemini_api_key)

    def recommend(self, message: str, menu_text: str) -> str:
        system_prompt = (
            "Ban la nhan vien tu van cua quan tra sua, noi tieng Viet than thien, ngan gon. "
            "Duoc phep goi y theo menu cho san, khong tu y che mon ngoai menu."
        )
        user_prompt = (
            f"Menu hien co:\n{menu_text}\n\n"
            f"Khach nhan: {message}\n"
            "Hay tu van 2-3 lua chon phu hop, co giai thich ngan gon."
        )
        if self.provider == "gemini":
            model = genai.GenerativeModel(self.model)
            response = model.generate_content(
                f"{system_prompt}\n\n{user_prompt}",
                generation_config={"temperature": 0.6},
            )
            return response.text or "Minh chua tu van duoc luc nay."

        if not self.openai_client:
            return "Chua cau hinh OpenAI API key."
        response = self.openai_client.chat.completions.create(
            model=self.model,
            temperature=0.6,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.choices[0].message.content or "Minh chua tu van duoc luc nay."

    def _extract_json(self, raw_text: str) -> str:
        text = raw_text.strip()
        if text.startswith("{") and text.endswith("}"):
            return text
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        return match.group(0) if match else "{}"

    def parse_order(self, message: str, menu_text: str) -> Dict[str, Any]:
        system_prompt = (
            "Trich xuat thong tin dat mon tu cau tieng Viet. "
            "Tra ve JSON hop le voi schema: "
            '{"action":"add|ask|other","item":"string","size":"M|L","quantity":number,'
            '"toppings":["string"],"note":"string"}. '
            "Neu khong chac chan item thi dat action=ask. "
            "Chi tra ve JSON, khong noi them."
        )
        user_prompt = f"Menu:\n{menu_text}\n\nTin nhan khach:\n{message}"

        if self.provider == "gemini":
            model = genai.GenerativeModel(self.model)
            response = model.generate_content(
                f"{system_prompt}\n\n{user_prompt}",
                generation_config={"temperature": 0},
            )
            content = self._extract_json(response.text or "{}")
        else:
            if not self.openai_client:
                content = "{}"
            else:
                response = self.openai_client.chat.completions.create(
                    model=self.model,
                    temperature=0,
                    response_format={"type": "json_object"},
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                )
                content = response.choices[0].message.content or "{}"

        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            return {
                "action": "other",
                "item": "",
                "size": "M",
                "quantity": 1,
                "toppings": [],
                "note": "Khong doc duoc du lieu",
            }

        return {
            "action": data.get("action", "other"),
            "item": str(data.get("item", "")).strip(),
            "size": str(data.get("size", "M")).upper(),
            "quantity": int(data.get("quantity", 1) or 1),
            "toppings": data.get("toppings", []) if isinstance(data.get("toppings", []), list) else [],
            "note": str(data.get("note", "")),
        }
