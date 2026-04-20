"""Модуль для управления инвентаризацией товаров на складе."""

# Константы
DEFAULT_LOW_STOCK_THRESHOLD = 5
MAX_QUANTITY = 999999


class InventoryItem:
    """Класс, представляющий отдельную позицию товара на складе."""

    def __init__(self, name: str, sku: str, quantity: int,
                 category: str = "Без категории", min_stock: int = DEFAULT_LOW_STOCK_THRESHOLD):
        """Инициализация товара.

        Args:
            name: Название товара
            sku: Артикул (уникальный идентификатор)
            quantity: Начальное количество на складе
            category: Категория запчасти (двигатель, тормоза и т.д.)
            min_stock: Минимальный остаток для уведомления
        """
        self.name = name
        self.sku = sku
        self.quantity = quantity
        self.category = category
        self.min_stock = min_stock

    def _validate_amount(self, amount) -> bool:
        """Вспомогательный метод для проверки количества."""
        if not isinstance(amount, (int, float)):
            print("Ошибка: amount должен быть числом.")
            return False
        return True

    def add_stock(self, amount: int) -> bool:
        """Увеличить количество товара на складе.

        Args:
            amount: Положительное число - количество для добавления.

        Returns:
            bool: True если добавление успешно, False если amount <= 0.
        """
        if not self._validate_amount(amount):
            return False

        if amount > 0:
            if self.quantity + amount > MAX_QUANTITY:
                print(f"Ошибка: превышен максимальный лимит склада "
                      f"({MAX_QUANTITY}).")
                return False
            self.quantity += amount
            return True
        return False

    def remove_stock(self, amount: int) -> bool:
        """Уменьшить количество товара на складе.

        Args:
            amount: Положительное число - количество для списания.

        Returns:
            bool: True если списание успешно, False если amount <= 0
                  или amount больше текущего остатка.
        """
        if not self._validate_amount(amount):
            return False

        if 0 < amount <= self.quantity:
            self.quantity -= amount
            return True
        return False

    def is_low_stock(
        self, threshold: int = DEFAULT_LOW_STOCK_THRESHOLD
    ) -> bool:
        """Проверить, не ниже ли остаток порогового значения.

        Args:
            threshold: Пороговое значение (по умолчанию 5).

        Returns:
            bool: True если остаток <= порога, False в противном случае.
        """
        return self.quantity <= threshold

    def get_info(self) -> str:
        """Вернуть строку с информацией о товаре."""
        status = "[!] МАЛО" if self.is_low_stock(self.min_stock) else "OK"
        return (f"SKU: {self.sku} | {self.name} | "
                f"Категория: {self.category} | "
                f"Остаток: {self.quantity} | Статус: {status}")


class InventoryManager:
    """Класс для управления множеством товаров."""

    def __init__(self):
        """Инициализация менеджера с пустым словарем товаров."""
        self._items = {}

    def add_item(self, item: InventoryItem) -> bool:
        """Добавить товар в систему.

        Args:
            item: Объект InventoryItem для добавления.

        Returns:
            bool: True если добавление успешно, False если ошибка.
        """
        if not isinstance(item, InventoryItem):
            print("Ошибка: item должен быть экземпляром InventoryItem")
            return False
        if item.sku in self._items:
            print(f"Ошибка: товар с артикулом {item.sku} уже существует")
            return False
        self._items[item.sku] = item
        return True

    def get_item(self, sku: str):
        """Получить товар по артикулу.

        Args:
            sku: Артикул товара.

        Returns:
            InventoryItem или None, если товар не найден.
        """
        return self._items.get(sku)

    def remove_item(self, sku: str) -> bool:
        """Удалить товар из системы по артикулу.

        Args:
            sku: Артикул товара для удаления.

        Returns:
            bool: True если товар удален, False если не найден.
        """
        if sku in self._items:
            del self._items[sku]
            print(f"Товар {sku} удален из системы.")
            return True
        print(f"Ошибка: товар с артикулом {sku} не найден.")
        return False

    def get_low_stock_items(
            self, threshold: int = DEFAULT_LOW_STOCK_THRESHOLD
    ) -> list:
        """Получить список товаров с низким остатком.

        Args:
            threshold: Пороговое значение (по умолчанию 5).

        Returns:
            list: Список товаров с остатком <= threshold.
        """
        return [
            item for item in self._items.values()
            if item.is_low_stock(threshold)
        ]

    def get_all_items(self) -> list:
        """Получить список всех товаров.

        Returns:
            list: Список всех товаров в системе.
        """
        return list(self._items.values())

    def get_total_count(self) -> int:
        """Получить общее количество товаров в системе.

        Returns:
            int: Количество уникальных товаров.
        """
        return len(self._items)

    def search_by_name(self, query: str) -> list:
        """Поиск товаров по названию (без учёта регистра).

        Args:
            query: Строка поиска.

        Returns:
            list: Список подходящих товаров.
        """
        query = query.lower()
        return [
            item for item in self._items.values()
            if query in item.name.lower()
        ]

    def get_by_category(self, category: str) -> list:
        """Получить все товары по категории.

        Args:
            category: Название категории.

        Returns:
            list: Список товаров в категории.
        """
        return [
            item for item in self._items.values()
            if item.category.lower() == category.lower()
        ]

    def get_report(self) -> dict:
        """Сводный отчёт по складу.

        Returns:
            dict: Статистика склада.
        """
        items = list(self._items.values())
        total_units = sum(i.quantity for i in items)
        low_stock = [i for i in items if i.is_low_stock(i.min_stock)]
        categories = {}
        for item in items:
            categories[item.category] = categories.get(item.category, 0) + 1
        return {
            "total_items": len(items),
            "total_units": total_units,
            "low_stock_count": len(low_stock),
            "categories": categories
        }