import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str
    llm_provider: str
    openai_api_key: str
    openai_model: str
    gemini_api_key: str
    gemini_model: str
    store_name: str
    payos_client_id: str
    payos_api_key: str
    payos_checksum_key: str
    payos_return_url: str
    payos_cancel_url: str


def get_settings() -> Settings:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    llm_provider = os.getenv("LLM_PROVIDER", "gemini").strip().lower()
    openai_key = os.getenv("OPENAI_API_KEY", "").strip()
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    gemini_model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash").strip()
    store_name = os.getenv("STORE_NAME", "Milk Tea by Mom").strip()
    payos_client_id = os.getenv("PAYOS_CLIENT_ID", "").strip()
    payos_api_key = os.getenv("PAYOS_API_KEY", "").strip()
    payos_checksum_key = os.getenv("PAYOS_CHECKSUM_KEY", "").strip()
    payos_return_url = os.getenv("PAYOS_RETURN_URL", "https://example.com/payment/success").strip()
    payos_cancel_url = os.getenv("PAYOS_CANCEL_URL", "https://example.com/payment/cancel").strip()

    if not token:
        raise ValueError("Missing TELEGRAM_BOT_TOKEN in environment variables.")
    if llm_provider == "openai" and not openai_key:
        raise ValueError("Missing OPENAI_API_KEY when LLM_PROVIDER=openai.")
    if llm_provider == "gemini" and not gemini_key:
        raise ValueError("Missing GEMINI_API_KEY when LLM_PROVIDER=gemini.")
    
    # Bỏ qua lỗi PayOS nếu chưa tới giai đoạn này
    # if not payos_client_id or not payos_api_key or not payos_checksum_key:
    #     raise ValueError("Missing PAYOS credentials in environment variables.")

    return Settings(
        telegram_bot_token=token,
        llm_provider=llm_provider,
        openai_api_key=openai_key,
        openai_model=model,
        gemini_api_key=gemini_key,
        gemini_model=gemini_model,
        store_name=store_name,
        payos_client_id=payos_client_id,
        payos_api_key=payos_api_key,
        payos_checksum_key=payos_checksum_key,
        payos_return_url=payos_return_url,
        payos_cancel_url=payos_cancel_url,
    )
