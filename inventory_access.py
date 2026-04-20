"""Контроль доступа к операциям инвентаризации."""

import auth
from inventory import InventoryItem, InventoryManager

# Общий менеджер склада
manager = InventoryManager()


def add_item(name: str, sku: str, quantity: int) -> bool:
    """Добавить товар на склад. Только admin и warehouse."""
    if not auth.require_role(auth.ROLE_ADMIN, auth.ROLE_WAREHOUSE):
        return False

    item = InventoryItem(name, sku, quantity)
    result = manager.add_item(item)
    if result:
        print(f"Товар '{name}' (SKU: {sku}) добавлен на склад. Кол-во: {quantity}")
    return result


def remove_item(sku: str) -> bool:
    """Удалить товар со склада. Только admin."""
    if not auth.require_role(auth.ROLE_ADMIN):
        return False

    return manager.remove_item(sku)


def add_stock(sku: str, amount: int) -> bool:
    """Приёмка товара. Только admin и warehouse."""
    if not auth.require_role(auth.ROLE_ADMIN, auth.ROLE_WAREHOUSE):
        return False

    item = manager.get_item(sku)
    if not item:
        print(f"Ошибка: товар с артикулом {sku} не найден.")
        return False

    result = item.add_stock(amount)
    if result:
        print(f"Приёмка: +{amount} единиц товара '{item.name}'. Остаток: {item.quantity}")
    return result


def remove_stock(sku: str, amount: int) -> bool:
    """Списание товара. Только admin и warehouse."""
    if not auth.require_role(auth.ROLE_ADMIN, auth.ROLE_WAREHOUSE):
        return False

    item = manager.get_item(sku)
    if not item:
        print(f"Ошибка: товар с артикулом {sku} не найден.")
        return False

    result = item.remove_stock(amount)
    if result:
        print(f"Списание: -{amount} единиц товара '{item.name}'. Остаток: {item.quantity}")
    return result


def get_all_items() -> list:
    """Просмотр всех товаров. Доступно всем авторизованным."""
    if not auth.require_auth():
        return []

    items = manager.get_all_items()
    print(f"Товаров на складе: {len(items)}")
    for item in items:
        print(f"  {item.sku} | {item.name} | кол-во: {item.quantity}")
    return items


def get_low_stock_items() -> list:
    """Товары с низким остатком. Доступно всем авторизованным."""
    if not auth.require_auth():
        return []

    items = manager.get_low_stock_items()
    print(f"Товаров с низким остатком: {len(items)}")
    for item in items:
        print(f"  [!] {item.sku} | {item.name} | остаток: {item.quantity}")
    return items
