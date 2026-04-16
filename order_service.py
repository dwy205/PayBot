from dataclasses import dataclass, field
from typing import Dict, List

from menu_service import MenuItem


@dataclass
class OrderLine:
    item_id: str
    name: str
    size: str
    quantity: int
    unit_price: int
    toppings: List[str] = field(default_factory=list)

    @property
    def subtotal(self) -> int:
        return self.quantity * self.unit_price


class OrderService:
    def __init__(self) -> None:
        self._orders: Dict[int, List[OrderLine]] = {}

    def add_item(
        self,
        user_id: int,
        item: MenuItem,
        size: str = "M",
        quantity: int = 1,
        topping_names: List[str] | None = None,
        topping_total: int = 0,
    ) -> OrderLine:
        normalized_size = size.upper()
        if normalized_size not in ("M", "L"):
            normalized_size = "M"

        base_price = item.price_l if normalized_size == "L" else item.price_m
        unit_price = base_price + topping_total
        line = OrderLine(
            item_id=item.item_id,
            name=item.name,
            size=normalized_size,
            quantity=max(1, quantity),
            unit_price=unit_price,
            toppings=topping_names or [],
        )
        self._orders.setdefault(user_id, []).append(line)
        return line

    def get_order(self, user_id: int) -> List[OrderLine]:
        return self._orders.get(user_id, [])

    def clear_order(self, user_id: int) -> None:
        self._orders.pop(user_id, None)

    def total(self, user_id: int) -> int:
        return sum(line.subtotal for line in self.get_order(user_id))

    def summary(self, user_id: int) -> str:
        lines = self.get_order(user_id)
        if not lines:
            return "Giỏ hàng đang trống."

        chunks = ["Đơn hàng của bạn:"]
        for idx, line in enumerate(lines, start=1):
            topping_text = f" | topping: {', '.join(line.toppings)}" if line.toppings else ""
            chunks.append(
                f"{idx}. {line.name} size {line.size} x{line.quantity} - "
                f"{line.subtotal:,}đ{topping_text}"
            )
        chunks.append(f"Tổng tạm tính: {self.total(user_id):,}đ")
        return "\n".join(chunks)

    def prep_note(self, user_id: int, customer_name: str, address: str, phone: str) -> str:
        lines = self.get_order(user_id)
        if not lines:
            return "Không có đơn để xác nhận."

        note = [
            "=== DON CHUAN BI ===",
            f"Khach hang: {customer_name}",
            f"So dien thoai: {phone}",
            f"Dia chi giao hang: {address}",
            "",
        ]
        for idx, line in enumerate(lines, start=1):
            topping_text = f" | topping: {', '.join(line.toppings)}" if line.toppings else ""
            note.append(
                f"{idx}. {line.name} size {line.size} x{line.quantity} - "
                f"{line.subtotal:,} VND{topping_text}"
            )
        note.append("")
        note.append(f"TONG THANH TOAN: {self.total(user_id):,} VND")
        return "\n".join(note)
