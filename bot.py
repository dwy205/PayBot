import io

import qrcode
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from config import get_settings
from llm_service import LLMService
from menu_service import MenuItem, MenuService
from order_service import OrderService
from payos_service import PayOSService


settings = get_settings()
menu_service = MenuService("Menu.csv")
order_service = OrderService()
llm_service = LLMService(
    provider=settings.llm_provider,
    model=settings.gemini_model if settings.llm_provider == "gemini" else settings.openai_model,
    openai_api_key=settings.openai_api_key,
    gemini_api_key=settings.gemini_api_key,
)
payos_service = PayOSService(
    client_id=settings.payos_client_id,
    api_key=settings.payos_api_key,
    checksum_key=settings.payos_checksum_key,
    return_url=settings.payos_return_url,
    cancel_url=settings.payos_cancel_url,
)


def _match_toppings(raw_toppings: list[str]) -> tuple[list[str], int]:
    matched: list[str] = []
    total_price = 0
    for top in raw_toppings:
        item = menu_service.find_item(top)
        if item and item.category.lower() == "topping":
            matched.append(item.name)
            total_price += item.price_m
    return matched, total_price


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_name = update.effective_user.first_name if update.effective_user else "ban"
    text = (
        f"Xin chao {user_name}! Minh la bot dat do uong cua {settings.store_name}.\n\n"
        "Lenh nhanh:\n"
        "/menu - Dat mon bang nut bam\n"
        "/cart - Xem gio hang\n"
        "/checkout - Tao QR thanh toan\n"
        "/clear - Xoa gio hang\n\n"
        "Ban co the nhan tin tu nhien, vi du:\n"
        "- Toi muon tra sua it ngot\n"
        "- Dat 2 tra chanh leo size L them tran chau den"
    )
    await update.message.reply_text(text)


def _drink_categories() -> list[str]:
    categories: list[str] = []
    for item in menu_service.all_items():
        if item.available and item.category.lower() != "topping" and item.category not in categories:
            categories.append(item.category)
    return categories


def _topping_items() -> list[MenuItem]:
    return [
        item
        for item in menu_service.all_items()
        if item.available and item.category.lower() == "topping"
    ]


def _menu_keyboard() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(category, callback_data=f"cat|{category}")]
        for category in _drink_categories()
    ]
    return InlineKeyboardMarkup(rows)


def _items_keyboard(category: str) -> InlineKeyboardMarkup:
    rows = []
    for item in menu_service.all_items():
        if item.available and item.category == category:
            rows.append([InlineKeyboardButton(item.name, callback_data=f"item|{item.item_id}")])
    rows.append([InlineKeyboardButton("<< Quay lai danh muc", callback_data="back|root")])
    return InlineKeyboardMarkup(rows)


def _size_keyboard(item: MenuItem) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(f"Size M - {item.price_m:,}đ", callback_data="size|M"),
                InlineKeyboardButton(f"Size L - {item.price_l:,}đ", callback_data="size|L"),
            ],
            [InlineKeyboardButton("<< Chon mon khac", callback_data="back|root")],
        ]
    )


def _topping_keyboard(selected: set[str]) -> InlineKeyboardMarkup:
    rows = []
    for top in _topping_items():
        checked = "✅ " if top.item_id in selected else ""
        rows.append(
            [InlineKeyboardButton(f"{checked}{top.name} (+{top.price_m:,}đ)", callback_data=f"top|{top.item_id}")]
        )
    rows.append([InlineKeyboardButton("Xong topping", callback_data="top_done")])
    return InlineKeyboardMarkup(rows)


def _after_add_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Them mon nua", callback_data="back|root")],
            [InlineKeyboardButton("Thanh toan bang QR", callback_data="pay|qr")],
        ]
    )


def _payment_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Toi da thanh toan", callback_data="pay|check")],
            [InlineKeyboardButton("Nhap thong tin giao hang", callback_data="pay|shipping")],
        ]
    )


async def _send_payment_qr(target_message, total: int, qr_text: str, checkout_url: str) -> None:
    qr = qrcode.QRCode(version=1, box_size=8, border=2)
    qr.add_data(qr_text)
    qr.make(fit=True)
    image = qr.make_image(fill_color="black", back_color="white")

    stream = io.BytesIO()
    image.save(stream, format="PNG")
    stream.seek(0)
    stream.name = "payment_qr.png"

    await target_message.reply_photo(
        photo=stream,
        caption=(
            f"Tong tien can thanh toan: {total:,}đ\n"
            f"Link thanh toan: {checkout_url}"
        ),
        reply_markup=_payment_keyboard(),
    )


async def menu_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data["flow"] = {}
    await update.message.reply_text(
        "Chon danh muc do uong:",
        reply_markup=_menu_keyboard(),
    )


async def cart_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    await update.message.reply_text(order_service.summary(user_id))


async def clear_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    order_service.clear_order(user_id)
    await update.message.reply_text("Da xoa gio hang.")


async def checkout_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if not order_service.get_order(user_id):
        await update.message.reply_text("Ban chua co mon nao trong gio.")
        return

    total = order_service.total(user_id)
    try:
        payment = payos_service.create_payment(
            amount=total,
            description=f"{settings.store_name[:15]}-{user_id}",
        )
    except Exception as exc:
        await update.message.reply_text(f"Khong tao duoc QR payOS: {str(exc)[:300]}")
        return

    context.user_data["pending_payment_order_code"] = payment.order_code
    context.user_data["payment_verified"] = False
    await _send_payment_qr(update.message, total, payment.qr_code_text, payment.checkout_url)


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not update.effective_user:
        return

    await query.answer()
    user_id = update.effective_user.id
    data = query.data or ""
    flow = context.user_data.setdefault("flow", {})

    if data.startswith("cat|"):
        category = data.split("|", maxsplit=1)[1]
        await query.edit_message_text(
            f"Chon mon trong danh muc {category}:",
            reply_markup=_items_keyboard(category),
        )
        return

    if data.startswith("item|"):
        item_id = data.split("|", maxsplit=1)[1]
        item = menu_service.items.get(item_id)
        if not item:
            await query.edit_message_text("Mon khong ton tai, vui long chon lai.", reply_markup=_menu_keyboard())
            return
        flow["item_id"] = item.item_id
        flow["size"] = "M"
        flow["toppings"] = []
        await query.edit_message_text(
            f"Ban dang chon: {item.name}\nHay chon size:",
            reply_markup=_size_keyboard(item),
        )
        return

    if data.startswith("size|"):
        size = data.split("|", maxsplit=1)[1]
        flow["size"] = size
        selected_ids = set(flow.get("toppings", []))
        await query.edit_message_text(
            "Chon topping (co the chon nhieu):",
            reply_markup=_topping_keyboard(selected_ids),
        )
        return

    if data.startswith("top|"):
        top_id = data.split("|", maxsplit=1)[1]
        selected_ids = set(flow.get("toppings", []))
        if top_id in selected_ids:
            selected_ids.remove(top_id)
        else:
            selected_ids.add(top_id)
        flow["toppings"] = list(selected_ids)
        await query.edit_message_reply_markup(reply_markup=_topping_keyboard(selected_ids))
        return

    if data == "top_done":
        item_id = flow.get("item_id")
        if not item_id:
            await query.edit_message_text("Phien dat mon het han. Vui long bam /menu de chon lai.")
            return

        item = menu_service.items.get(item_id)
        if not item:
            await query.edit_message_text("Mon khong ton tai. Vui long bam /menu.")
            return

        topping_names: list[str] = []
        topping_total = 0
        for top_id in flow.get("toppings", []):
            top_item = menu_service.items.get(top_id)
            if top_item and top_item.category.lower() == "topping":
                topping_names.append(top_item.name)
                topping_total += top_item.price_m

        line = order_service.add_item(
            user_id=user_id,
            item=item,
            size=flow.get("size", "M"),
            quantity=1,
            topping_names=topping_names,
            topping_total=topping_total,
        )
        flow.clear()
        await query.edit_message_text(
            "Da them vao gio:\n"
            f"- {line.name} size {line.size}\n"
            f"- Topping: {', '.join(line.toppings) if line.toppings else 'Khong'}\n"
            f"- Tam tinh dong nay: {line.subtotal:,}đ\n\n"
            f"{order_service.summary(user_id)}",
            reply_markup=_after_add_keyboard(),
        )
        return

    if data == "pay|qr":
        lines = order_service.get_order(user_id)
        if not lines:
            await query.edit_message_text("Gio hang trong. Bam /menu de dat mon.")
            return
        total = order_service.total(user_id)
        try:
            payment = payos_service.create_payment(
                amount=total,
                description=f"{settings.store_name[:15]}-{user_id}",
            )
        except Exception as exc:
            await query.message.reply_text(f"Khong tao duoc QR payOS: {str(exc)[:300]}")
            return
        context.user_data["pending_payment_order_code"] = payment.order_code
        context.user_data["payment_verified"] = False
        await _send_payment_qr(query.message, total, payment.qr_code_text, payment.checkout_url)
        return

    if data == "pay|check":
        order_code = context.user_data.get("pending_payment_order_code")
        if not order_code:
            await query.message.reply_text("Chua co don thanh toan nao. Bam /checkout de tao QR.")
            return
        try:
            paid = payos_service.is_paid(int(order_code))
        except Exception:
            await query.message.reply_text("Khong kiem tra duoc giao dich luc nay. Thu lai sau.")
            return
        if not paid:
            await query.message.reply_text("He thong chua ghi nhan thanh toan. Vui long thu lai sau 5-10 giay.")
            return
        context.user_data["payment_verified"] = True
        context.user_data["awaiting_checkout_info"] = True
        await query.message.reply_text(
            "Da xac nhan thanh toan thanh cong.\n"
            "Vui long gui thong tin giao hang: Ten | So dien thoai | Dia chi"
        )
        return

    if data == "pay|shipping":
        if not context.user_data.get("payment_verified"):
            await query.message.reply_text("Ban can thanh toan va bam 'Toi da thanh toan' truoc.")
            return
        context.user_data["awaiting_checkout_info"] = True
        await query.message.reply_text("Gui: Ten | So dien thoai | Dia chi")
        return

    if data == "back|root":
        await query.edit_message_text("Chon danh muc do uong:", reply_markup=_menu_keyboard())
        return


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.effective_user:
        return

    user_id = update.effective_user.id
    text = update.message.text.strip()

    if context.user_data.get("awaiting_checkout_info"):
        if not context.user_data.get("payment_verified"):
            await update.message.reply_text("He thong chua xac nhan thanh toan. Bam /checkout de tao QR.")
            return
        parts = [p.strip() for p in text.split("|")]
        if len(parts) != 3:
            await update.message.reply_text("Sai dinh dang. Vui long gui: Ten | So dien thoai | Dia chi")
            return

        customer_name, phone, address = parts
        prep = order_service.prep_note(user_id, customer_name=customer_name, address=address, phone=phone)
        total = order_service.total(user_id)
        context.user_data["awaiting_checkout_info"] = False
        context.user_data["payment_verified"] = False
        context.user_data["pending_payment_order_code"] = None
        order_service.clear_order(user_id)

        await update.message.reply_text(
            f"Don cua ban da duoc xac nhan.\nTong thanh toan: {total:,}đ\n\n{prep}"
        )
        return

    menu_text = menu_service.menu_for_prompt()
    parsed = llm_service.parse_order(text, menu_text)

    if parsed["action"] == "add":
        item = menu_service.find_item(parsed["item"])
        if item is None:
            await update.message.reply_text(
                "Minh chua tim thay mon ban muon dat. Hay dung /menu de xem danh sach mon."
            )
            return
        if item.category.lower() == "topping":
            await update.message.reply_text("Topping khong the dat rieng. Ban hay chon kem 1 mon chinh.")
            return

        toppings, topping_total = _match_toppings(parsed.get("toppings", []))
        line = order_service.add_item(
            user_id=user_id,
            item=item,
            size=parsed.get("size", "M"),
            quantity=parsed.get("quantity", 1),
            topping_names=toppings,
            topping_total=topping_total,
        )
        await update.message.reply_text(
            "Da them mon:\n"
            f"- {line.name} size {line.size} x{line.quantity}\n"
            f"- Tam tinh dong nay: {line.subtotal:,}đ\n\n"
            "Gui /cart de xem tong don, /checkout de chot don."
        )
        return

    if parsed["action"] == "ask":
        await update.message.reply_text(
            "Minh chua chac mon ban muon dat. Ban thu ghi ro ten mon + size + so luong nhe.\n"
            "Vi du: Dat 1 tra sua truyen thong size L."
        )
        return

    recommendation = llm_service.recommend(text, menu_text)
    await update.message.reply_text(recommendation)


def main() -> None:
    import os
    import threading
    from http.server import BaseHTTPRequestHandler, HTTPServer

    def run_dummy_server():
        port = int(os.environ.get("PORT", 10000))
        server_address = ("0.0.0.0", port)
        class DummyHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"Bot is alive!")
            def do_HEAD(self):
                self.send_response(200)
                self.end_headers()
            def log_message(self, format, *args):
                return
        httpd = HTTPServer(server_address, DummyHandler)
        httpd.serve_forever()

    threading.Thread(target=run_dummy_server, daemon=True).start()

    import asyncio
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())

    app = Application.builder().token(settings.telegram_bot_token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu_cmd))
    app.add_handler(CommandHandler("cart", cart_cmd))
    app.add_handler(CommandHandler("checkout", checkout_cmd))
    app.add_handler(CommandHandler("clear", clear_cmd))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.run_polling()


if __name__ == "__main__":
    main()
