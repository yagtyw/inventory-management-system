"""Консольный интерфейс системы управления инвентаризацией."""

import auth
import inventory_access


def menu_guest():
    print("\n=== Система инвентаризации автозапчастей ===")
    print("1. Войти")
    print("2. Зарегистрироваться")
    print("0. Выход")
    return input("Выберите: ").strip()


def menu_main():
    user = auth.current_user
    print(f"\n=== Меню [{user['username']} | {user['role']}] ===")
    print("1. Все товары")
    print("2. Товары с низким остатком")
    print("3. Поиск по названию")
    print("4. Карточка товара")
    print("5. Отчёт по складу")
    if user["role"] in (auth.ROLE_ADMIN, auth.ROLE_WAREHOUSE):
        print("6. Добавить товар")
        print("7. Приёмка (добавить остаток)")
        print("8. Списание (убрать остаток)")
        print("9. Инвентаризация (сверка остатка)")
    if user["role"] == auth.ROLE_ADMIN:
        print("10. Удалить товар")
    print("0. Выйти из аккаунта")
    return input("Выберите: ").strip()


def do_register():
    print("\n-- Регистрация --")
    username = input("Логин: ").strip()
    password = input("Пароль: ").strip()
    print(f"Роли: {auth.ROLE_ADMIN}, {auth.ROLE_WAREHOUSE}, {auth.ROLE_VIEWER}")
    role = input("Роль: ").strip()
    auth.register(username, password, role)


def do_login():
    print("\n-- Вход --")
    username = input("Логин: ").strip()
    password = input("Пароль: ").strip()
    auth.login(username, password)


def do_add_item():
    print("\n-- Добавить товар --")
    name = input("Название: ").strip()
    sku = input("Артикул (SKU): ").strip()
    category = input("Категория (напр. Двигатель, Тормоза, Фильтры): ").strip() or "Без категории"
    try:
        qty = int(input("Количество: ").strip())
        min_stock = int(input("Минимальный остаток (по умолчанию 5): ").strip() or "5")
    except ValueError:
        print("Ошибка: введите число.")
        return
    inventory_access.add_item(name, sku, qty, category, min_stock)


def do_add_stock():
    print("\n-- Приёмка товара --")
    sku = input("Артикул (SKU): ").strip()
    try:
        amount = int(input("Количество: ").strip())
    except ValueError:
        print("Ошибка: введите число.")
        return
    inventory_access.add_stock(sku, amount)


def do_remove_stock():
    print("\n-- Списание товара --")
    sku = input("Артикул (SKU): ").strip()
    try:
        amount = int(input("Количество: ").strip())
    except ValueError:
        print("Ошибка: введите число.")
        return
    inventory_access.remove_stock(sku, amount)


def do_remove_item():
    print("\n-- Удалить товар --")
    sku = input("Артикул (SKU): ").strip()
    inventory_access.remove_item(sku)


def do_inventory():
    print("\n-- Инвентаризация --")
    sku = input("Артикул (SKU): ").strip()
    try:
        actual = int(input("Фактическое количество: ").strip())
    except ValueError:
        print("Ошибка: введите число.")
        return
    inventory_access.do_inventory(sku, actual)


def run():
    print("Добро пожаловать в систему управления инвентаризацией!")

    while True:
        if auth.current_user is None:
            choice = menu_guest()
            if choice == "1":
                do_login()
            elif choice == "2":
                do_register()
            elif choice == "0":
                print("До свидания!")
                break
            else:
                print("Неверный выбор.")
        else:
            choice = menu_main()
            if choice == "1":
                inventory_access.get_all_items()
            elif choice == "2":
                inventory_access.get_low_stock_items()
            elif choice == "3":
                query = input("Введите название для поиска: ").strip()
                inventory_access.search_item(query)
            elif choice == "4":
                sku = input("Введите артикул (SKU): ").strip()
                inventory_access.show_item_card(sku)
            elif choice == "5":
                inventory_access.show_report()
            elif choice == "6":
                do_add_item()
            elif choice == "7":
                do_add_stock()
            elif choice == "8":
                do_remove_stock()
            elif choice == "9":
                do_inventory()
            elif choice == "10":
                do_remove_item()
            elif choice == "0":
                auth.logout()
            else:
                print("Неверный выбор.")


if __name__ == "__main__":
    run()
