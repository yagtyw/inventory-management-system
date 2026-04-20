"""Тесты безопасности системы управления инвентаризацией."""

import unittest
import auth
import inventory_access


def reset():
    """Сброс состояния перед каждым тестом."""
    auth.users.clear()
    auth.current_user = None
    inventory_access.manager._items.clear()


class TestAuth(unittest.TestCase):

    def setUp(self):
        reset()

    def test_register_and_login(self):
        """Регистрация и успешный вход."""
        auth.register("ivanov", "pass123", auth.ROLE_WAREHOUSE)
        result = auth.login("ivanov", "pass123")
        self.assertTrue(result)
        self.assertIsNotNone(auth.current_user)

    def test_password_is_hashed(self):
        """Пароль хранится в хешированном виде."""
        auth.register("ivanov", "pass123", auth.ROLE_WAREHOUSE)
        stored = auth.users["ivanov"]["password"]
        self.assertNotEqual(stored, "pass123")

    def test_wrong_password_fails(self):
        """Неверный пароль — вход запрещён."""
        auth.register("ivanov", "pass123", auth.ROLE_WAREHOUSE)
        result = auth.login("ivanov", "wrongpass")
        self.assertFalse(result)
        self.assertIsNone(auth.current_user)

    def test_unknown_user_fails(self):
        """Несуществующий пользователь — вход запрещён."""
        result = auth.login("ghost", "pass123")
        self.assertFalse(result)

    def test_duplicate_register_fails(self):
        """Нельзя зарегистрировать двух пользователей с одним именем."""
        auth.register("ivanov", "pass123", auth.ROLE_WAREHOUSE)
        result = auth.register("ivanov", "other", auth.ROLE_VIEWER)
        self.assertFalse(result)

    def test_logout(self):
        """После выхода current_user = None."""
        auth.register("ivanov", "pass123", auth.ROLE_WAREHOUSE)
        auth.login("ivanov", "pass123")
        auth.logout()
        self.assertIsNone(auth.current_user)

    def test_invalid_role_fails(self):
        """Нельзя зарегистрировать с несуществующей ролью."""
        result = auth.register("ivanov", "pass123", "superuser")
        self.assertFalse(result)


class TestAccessControl(unittest.TestCase):

    def setUp(self):
        reset()

    def test_add_item_requires_auth(self):
        """Без авторизации нельзя добавить товар."""
        result = inventory_access.add_item("Фильтр масляный", "SKU001", 10)
        self.assertFalse(result)

    def test_get_items_requires_auth(self):
        """Без авторизации нельзя просматривать товары."""
        result = inventory_access.get_all_items()
        self.assertEqual(result, [])

    def test_warehouse_can_add_item(self):
        """Кладовщик может добавлять товары."""
        auth.register("petrov", "pass1", auth.ROLE_WAREHOUSE)
        auth.login("petrov", "pass1")
        result = inventory_access.add_item("Фильтр масляный", "SKU001", 10)
        self.assertTrue(result)

    def test_viewer_cannot_add_item(self):
        """Наблюдатель не может добавлять товары."""
        auth.register("sidorov", "pass2", auth.ROLE_VIEWER)
        auth.login("sidorov", "pass2")
        result = inventory_access.add_item("Фильтр масляный", "SKU001", 10)
        self.assertFalse(result)

    def test_viewer_cannot_remove_item(self):
        """Наблюдатель не может удалять товары."""
        auth.register("admin", "adminpass", auth.ROLE_ADMIN)
        auth.login("admin", "adminpass")
        inventory_access.add_item("Фильтр масляный", "SKU001", 10)
        auth.logout()

        auth.register("sidorov", "pass2", auth.ROLE_VIEWER)
        auth.login("sidorov", "pass2")
        result = inventory_access.remove_item("SKU001")
        self.assertFalse(result)

    def test_viewer_can_view_items(self):
        """Наблюдатель может просматривать товары."""
        auth.register("admin", "adminpass", auth.ROLE_ADMIN)
        auth.login("admin", "adminpass")
        inventory_access.add_item("Фильтр масляный", "SKU001", 10)
        auth.logout()

        auth.register("sidorov", "pass2", auth.ROLE_VIEWER)
        auth.login("sidorov", "pass2")
        items = inventory_access.get_all_items()
        self.assertEqual(len(items), 1)

    def test_warehouse_can_add_and_remove_stock(self):
        """Кладовщик может принимать и списывать товар."""
        auth.register("petrov", "pass1", auth.ROLE_WAREHOUSE)
        auth.login("petrov", "pass1")
        inventory_access.add_item("Тормозные колодки", "SKU002", 20)
        self.assertTrue(inventory_access.add_stock("SKU002", 5))
        self.assertTrue(inventory_access.remove_stock("SKU002", 3))

    def test_only_admin_can_delete_item(self):
        """Только admin может удалить товар из системы."""
        auth.register("admin", "adminpass", auth.ROLE_ADMIN)
        auth.login("admin", "adminpass")
        inventory_access.add_item("Свеча зажигания", "SKU003", 50)
        result = inventory_access.remove_item("SKU003")
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
