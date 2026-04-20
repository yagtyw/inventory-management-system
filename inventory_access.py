"""Контроль доступа к операциям инвентаризации."""

import auth
from inventory import InventoryItem, InventoryManager

# Общий менеджер склада
manager = InventoryManager()


def add_item(name: str, sku: str, quantity: int,
             category: str = "Без категории", min_stock: int = 5) -> bool:
    """Добавить товар на склад. Только admin и warehouse."""
    if not auth.require_role(auth.ROLE_ADMIN, auth.ROLE_WAREHOUSE):
        return False

    item = InventoryItem(name, sku, quantity, category, min_stock)
    result = manager.add_item(item)
    if result:
        print(f"Товар '{name}' (SKU: {sku}, категория: {category}) добавлен. Кол-во: {quantity}")
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
        print(f"Ошибка: товар {sku} не найден.")
        return False

    result = item.add_stock(amount)
    if result:
        print(f"Приёмка: +{amount} шт. '{item.name}'. Остаток: {item.quantity}")
    return result


def remove_stock(sku: str, amount: int) -> bool:
    """Списание товара. Только admin и warehouse."""
    if not auth.require_role(auth.ROLE_ADMIN, auth.ROLE_WAREHOUSE):
        return False

    item = manager.get_item(sku)
    if not item:
        print(f"Ошибка: товар {sku} не найден.")
        return False

    result = item.remove_stock(amount)
    if result:
        print(f"Списание: -{amount} шт. '{item.name}'. Остаток: {item.quantity}")
    return result


def get_all_items() -> list:
    """Просмотр всех товаров. Доступно всем авторизованным."""
    if not auth.require_auth():
        return []

    items = manager.get_all_items()
    print(f"\nТоваров на складе: {len(items)}")
    print(f"{'SKU':<12} {'Название':<30} {'Категория':<20} {'Кол-во':>7}")
    print("-" * 72)
    for item in items:
        print(f"{item.sku:<12} {item.name:<30} {item.category:<20} {item.quantity:>7}")
    return items


def get_low_stock_items() -> list:
    """Товары с низким остатком. Доступно всем авторизованным."""
    if not auth.require_auth():
        return []

    items = manager.get_low_stock_items()
    print(f"\n[!] Товаров с низким остатком: {len(items)}")
    for item in items:
        print(f"  {item.sku} | {item.name} | остаток: {item.quantity} (мин: {item.min_stock})")
    return items


def search_item(query: str) -> list:
    """Поиск товара по названию. Доступно всем авторизованным."""
    if not auth.require_auth():
        return []

    results = manager.search_by_name(query)
    print(f"\nРезультаты поиска '{query}': {len(results)} шт.")
    for item in results:
        print(f"  {item.get_info()}")
    return results


def show_item_card(sku: str):
    """Карточка товара по артикулу. Доступно всем авторизованным."""
    if not auth.require_auth():
        return

    item = manager.get_item(sku)
    if not item:
        print(f"Товар с артикулом {sku} не найден.")
        return

    print(f"\n{'='*40}")
    print(f"  Карточка товара")
    print(f"{'='*40}")
    print(f"  Название:  {item.name}")
    print(f"  Артикул:   {item.sku}")
    print(f"  Категория: {item.category}")
    print(f"  Остаток:   {item.quantity} шт.")
    print(f"  Мин. остаток: {item.min_stock} шт.")
    status = "МАЛО — нужна закупка" if item.is_low_stock(item.min_stock) else "В норме"
    print(f"  Статус:    {status}")
    print(f"{'='*40}")


def do_inventory(sku: str, actual_quantity: int) -> bool:
    """Инвентаризация: сверка фактического остатка с учётным.
    Только admin и warehouse."""
    if not auth.require_role(auth.ROLE_ADMIN, auth.ROLE_WAREHOUSE):
        return False

    item = manager.get_item(sku)
    if not item:
        print(f"Товар {sku} не найден.")
        return False

    diff = actual_quantity - item.quantity
    print(f"\n-- Инвентаризация: {item.name} --")
    print(f"  По учёту:    {item.quantity} шт.")
    print(f"  Фактически:  {actual_quantity} шт.")
    if diff == 0:
        print("  Расхождений нет.")
    elif diff > 0:
        print(f"  Излишек: +{diff} шт. — обновляем остаток.")
        item.quantity = actual_quantity
    else:
        print(f"  Недостача: {diff} шт. — обновляем остаток.")
        item.quantity = actual_quantity
    return True


def show_report():
    """Сводный отчёт по складу. Доступно всем авторизованным."""
    if not auth.require_auth():
        return

    report = manager.get_report()
    print(f"\n{'='*40}")
    print(f"  Отчёт по складу")
    print(f"{'='*40}")
    print(f"  Позиций на складе:  {report['total_items']}")
    print(f"  Всего единиц:       {report['total_units']}")
    print(f"  Мало на складе:     {report['low_stock_count']}")
    print(f"\n  По категориям:")
    for cat, count in report["categories"].items():
        print(f"    {cat}: {count} позиций")
    print(f"{'='*40}")
