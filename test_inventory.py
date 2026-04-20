"""Тесты для проверки рефакторинга."""

import unittest
from inventory import InventoryItem, InventoryManager


class TestInventoryItem(unittest.TestCase):
    """Тесты для класса InventoryItem."""

    def test_add_stock_increases_quantity(self):
        """Тест: добавление товара увеличивает количество."""
        item = InventoryItem("Laptop", "SKU123", 10)
        result = item.add_stock(5)
        self.assertTrue(result)
        self.assertEqual(item.quantity, 15)

    def test_add_stock_negative_does_nothing(self):
        """Тест: отрицательное количество не изменяет остаток."""
        item = InventoryItem("Laptop", "SKU123", 10)
        result = item.add_stock(-5)
        self.assertFalse(result)
        self.assertEqual(item.quantity, 10)

    def test_remove_stock_decreases_quantity(self):
        """Тест: списание товара уменьшает количество."""
        item = InventoryItem("Laptop", "SKU123", 10)
        result = item.remove_stock(3)
        self.assertTrue(result)
        self.assertEqual(item.quantity, 7)

    def test_remove_stock_too_much_fails(self):
        """Тест: списание больше, чем есть - не изменяет остаток."""
        item = InventoryItem("Laptop", "SKU123", 10)
        result = item.remove_stock(20)
        self.assertFalse(result)
        self.assertEqual(item.quantity, 10)

    def test_is_low_stock(self):
        """Тест: проверка низкого остатка."""
        item = InventoryItem("Laptop", "SKU123", 3)
        self.assertTrue(item.is_low_stock(5))
        self.assertFalse(item.is_low_stock(2))


class TestInventoryManager(unittest.TestCase):
    """Тесты для класса InventoryManager."""

    def test_add_and_get_item(self):
        """Тест: добавление и получение товара."""
        manager = InventoryManager()
        item = InventoryItem("Тест", "001", 10)
        manager.add_item(item)
        self.assertEqual(manager.get_item("001"), item)

    def test_add_duplicate_fails(self):
        """Тест: добавление дубликата не должно работать."""
        manager = InventoryManager()
        item1 = InventoryItem("Тест", "001", 10)
        item2 = InventoryItem("Тест2", "001", 20)
        manager.add_item(item1)
        result = manager.add_item(item2)
        self.assertFalse(result)

    def test_remove_item(self):
        """Тест: удаление товара."""
        manager = InventoryManager()
        item = InventoryItem("Тест", "001", 10)
        manager.add_item(item)
        self.assertEqual(manager.get_total_count(), 1)
        manager.remove_item("001")
        self.assertEqual(manager.get_total_count(), 0)

    def test_get_low_stock_items(self):
        """Тест: получение списка товаров с низким остатком."""
        manager = InventoryManager()
        manager.add_item(InventoryItem("A", "001", 3))
        manager.add_item(InventoryItem("B", "002", 10))
        manager.add_item(InventoryItem("C", "003", 2))
        low_stock = manager.get_low_stock_items(5)
        self.assertEqual(len(low_stock), 2)

    def test_get_all_items(self):
        """Тест: получение всех товаров."""
        manager = InventoryManager()
        manager.add_item(InventoryItem("A", "001", 3))
        manager.add_item(InventoryItem("B", "002", 10))
        all_items = manager.get_all_items()
        self.assertEqual(len(all_items), 2)

    def test_get_total_count(self):
        """Тест: получение общего количества товаров."""
        manager = InventoryManager()
        self.assertEqual(manager.get_total_count(), 0)
        manager.add_item(InventoryItem("A", "001", 3))
        manager.add_item(InventoryItem("B", "002", 10))
        self.assertEqual(manager.get_total_count(), 2)


if __name__ == "__main__":
    unittest.main()