# Техническая документация — Система управления инвентаризацией автозапчастей

Документ предназначен для разработчиков, работающих с проектом.

---

## 1. Общая архитектура проекта

Проект построен по упрощённой трёхслойной архитектуре:

```
┌─────────────────────────────┐
│       Слой интерфейса       │  main.py
│  (консольный ввод/вывод)    │
└────────────┬────────────────┘
             │
┌────────────▼────────────────┐
│       Слой логики           │  inventory_access.py, auth.py
│  (контроль доступа, бизнес- │
│   правила, операции)        │
└────────────┬────────────────┘
             │
┌────────────▼────────────────┐
│       Слой данных           │  inventory.py, notifications.py
│  (модели, хранилище         │
│   в памяти)                 │
└─────────────────────────────┘
```

Данные хранятся в памяти (словари Python). Персистентность не реализована — при перезапуске данные сбрасываются.

---

## 2. Компоненты приложения

### Структура каталогов

```
project/
├── main.py              # Точка входа, консольный интерфейс
├── auth.py              # Аутентификация и авторизация
├── inventory.py         # Модели данных: InventoryItem, InventoryManager
├── inventory_access.py  # Бизнес-операции с проверкой прав
├── notifications.py     # Модуль уведомлений
├── test_security.py     # Тесты безопасности
├── requirements.txt     # Зависимости
├── README.md            # Руководство пользователя
└── TECHNICAL_DOCS.md    # Этот файл
```

### Модуль аутентификации — `auth.py`

Отвечает за регистрацию, вход, выход и проверку прав.

Глобальное состояние:
- `users: dict` — словарь всех пользователей, ключ — username
- `current_user: dict | None` — текущий авторизованный пользователь

Роли:
```python
ROLE_ADMIN     = "admin"      # полный доступ
ROLE_WAREHOUSE = "warehouse"  # приёмка, списание, инвентаризация
ROLE_VIEWER    = "viewer"     # только чтение
```

Ключевые функции:

| Функция | Описание |
|---|---|
| `register(username, password, role)` | Создаёт пользователя, хеширует пароль |
| `login(username, password)` | Проверяет пароль, устанавливает `current_user` |
| `logout()` | Сбрасывает `current_user = None` |
| `require_auth()` | Возвращает `False` если не авторизован |
| `require_role(*roles)` | Возвращает `False` если роль не подходит |

### Модуль данных — `inventory.py`

Содержит две модели.

**`InventoryItem`** — одна позиция товара:

| Поле | Тип | Описание |
|---|---|---|
| `name` | str | Название запчасти |
| `sku` | str | Артикул (уникальный ключ) |
| `quantity` | int | Текущий остаток |
| `category` | str | Категория (Двигатель, Тормоза и т.д.) |
| `min_stock` | int | Минимальный остаток для предупреждения |

Методы: `add_stock(amount)`, `remove_stock(amount)`, `is_low_stock(threshold)`, `get_info()`

**`InventoryManager`** — реестр всех товаров, хранит `_items: dict[sku -> InventoryItem]`:

| Метод | Описание |
|---|---|
| `add_item(item)` | Добавить позицию, проверяет дубликат SKU |
| `remove_item(sku)` | Удалить позицию |
| `get_item(sku)` | Получить по артикулу |
| `get_all_items()` | Список всех позиций |
| `get_low_stock_items()` | Позиции ниже порога |
| `search_by_name(query)` | Поиск по подстроке в названии |
| `get_by_category(category)` | Фильтр по категории |
| `get_report()` | Сводная статистика (dict) |

### Модуль контроля доступа — `inventory_access.py`

Обёртка над `InventoryManager`. Каждая функция сначала вызывает `require_auth()` или `require_role()`, и только потом выполняет операцию. Содержит единственный глобальный экземпляр `manager = InventoryManager()`.

Матрица доступа:

| Операция | admin | warehouse | viewer |
|---|:---:|:---:|:---:|
| Просмотр товаров | ✓ | ✓ | ✓ |
| Поиск / карточка / отчёт | ✓ | ✓ | ✓ |
| Добавить товар | ✓ | ✓ | ✗ |
| Приёмка / списание | ✓ | ✓ | ✗ |
| Инвентаризация | ✓ | ✓ | ✗ |
| Удалить товар | ✓ | ✗ | ✗ |

### Модуль интерфейса — `main.py`

Реализует консольный цикл `while True`. Логика:
- если `current_user is None` — показывает гостевое меню
- после входа — показывает меню с пунктами, отфильтрованными по роли
- каждый пункт вызывает соответствующую функцию из `inventory_access` или `auth`

### Модуль уведомлений — `notifications.py`

Базовый класс `Notification(message, type)` с методом `send()`. В текущей версии выводит сообщение в консоль. Предназначен для расширения (email, SMS, push).

---

## 3. Работа с данными

### Структура объекта пользователя

```python
users["ivanov"] = {
    "id": 1,
    "username": "ivanov",
    "password": "pbkdf2:sha256:...",  # хеш, не открытый текст
    "role": "warehouse"
}
```

### Структура объекта товара

```python
# InventoryItem хранится в InventoryManager._items по ключу SKU
{
    "MANN-W712": InventoryItem(
        name="Фильтр масляный Mann W712",
        sku="MANN-W712",
        quantity=42,
        category="Фильтры",
        min_stock=5
    )
}
```

### Формат отчёта `get_report()`

```python
{
    "total_items": 15,       # количество уникальных позиций
    "total_units": 430,      # сумма всех остатков
    "low_stock_count": 3,    # позиций ниже min_stock
    "categories": {
        "Фильтры": 5,
        "Тормоза": 4,
        "Двигатель": 6
    }
}
```

### База данных

В текущей версии БД не используется. Все данные живут в памяти процесса. Для подключения реальной БД достаточно заменить словари `users` и `manager._items` на вызовы ORM (например, SQLAlchemy), не меняя остальной код.

Предполагаемая схема таблиц при переходе на SQL:

```
users
  id          INTEGER PRIMARY KEY
  username    TEXT UNIQUE NOT NULL
  password    TEXT NOT NULL          -- pbkdf2 хеш
  role        TEXT NOT NULL

inventory_items
  sku         TEXT PRIMARY KEY
  name        TEXT NOT NULL
  quantity    INTEGER NOT NULL
  category    TEXT
  min_stock   INTEGER DEFAULT 5
```

---

## 4. Валидация и обработка ошибок

Все функции возвращают `bool` — `True` при успехе, `False` при ошибке. Исключения не бросаются, ошибки выводятся через `print()`.

| Ситуация | Поведение |
|---|---|
| Вход без авторизации | `require_auth()` → `print` + `return False/[]` |
| Недостаточно прав | `require_role()` → `print "Ошибка 403"` + `return False` |
| Товар не найден по SKU | `print` + `return False` |
| Дубликат SKU при добавлении | `print` + `return False` |
| Списание больше остатка | `remove_stock()` → `return False` без изменений |
| Превышение MAX_QUANTITY (999999) | `add_stock()` → `print` + `return False` |
| Неверный тип amount | `_validate_amount()` → `print` + `return False` |
| Неверный тип при вводе в консоли | `try/except ValueError` в `main.py` → `print` + `return` |
| Неизвестная роль при регистрации | `register()` → `print` + `return False` |

---

## 5. Используемые технологии и библиотеки

| Технология | Версия | Назначение |
|---|---|---|
| Python | 3.9+ | Язык программирования |
| werkzeug | актуальная | Хеширование паролей (`pbkdf2:sha256`) |
| pytest | 7.4.0+ | Тестирование |
| flake8 | 6.1.0+ | Линтер, проверка стиля кода |

Внешние сервисы не используются. Фреймворки не используются — приложение консольное, без веб-слоя.

### Алгоритм хеширования паролей

Используется `werkzeug.security.generate_password_hash` с методом `pbkdf2:sha256`. Метод указывается явно, так как Python 3.9 не поддерживает `scrypt` (используемый по умолчанию в новых версиях werkzeug).

```python
# Регистрация
generate_password_hash(password, method="pbkdf2:sha256")

# Проверка при входе
check_password_hash(stored_hash, input_password)
```
