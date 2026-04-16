import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass(frozen=True)
class MenuItem:
    category: str
    item_id: str
    name: str
    description: str
    price_m: int
    price_l: int
    available: bool


class MenuService:
    def __init__(self, csv_path: str = "Menu.csv") -> None:
        self.csv_path = Path(csv_path)
        self.items: Dict[str, MenuItem] = {}
        self._name_index: Dict[str, str] = {}
        self._load()

    def _load(self) -> None:
        with self.csv_path.open(mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                item = MenuItem(
                    category=row["category"],
                    item_id=row["item_id"],
                    name=row["name"],
                    description=row["description"],
                    price_m=int(row["price_m"]),
                    price_l=int(row["price_l"]),
                    available=row["available"].lower() == "true",
                )
                self.items[item.item_id] = item
                self._name_index[item.name.lower()] = item.item_id

    def find_item(self, text: str) -> Optional[MenuItem]:
        normalized = text.strip().lower()
        if normalized in self.items:
            return self.items[normalized]
        if normalized in self._name_index:
            return self.items[self._name_index[normalized]]

        for item in self.items.values():
            if normalized in item.name.lower():
                return item
        return None

    def all_items(self) -> List[MenuItem]:
        return list(self.items.values())

    def menu_for_prompt(self) -> str:
        lines = []
        for item in self.items.values():
            if not item.available:
                continue
            lines.append(
                f"- {item.item_id} | {item.name} ({item.category}) | "
                f"M: {item.price_m} VND, L: {item.price_l} VND | {item.description}"
            )
        return "\n".join(lines)

    def format_menu_text(self) -> str:
        grouped: Dict[str, List[MenuItem]] = {}
        for item in self.items.values():
            if item.available:
                grouped.setdefault(item.category, []).append(item)

        chunks: List[str] = []
        for category, items in grouped.items():
            chunks.append(f"*{category}*")
            for item in items:
                chunks.append(
                    f"- {item.item_id}: {item.name} (M {item.price_m:,}đ / L {item.price_l:,}đ)"
                )
            chunks.append("")
        return "\n".join(chunks).strip()
