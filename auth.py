"""Модуль аутентификации для системы управления инвентаризацией."""

from werkzeug.security import generate_password_hash, check_password_hash

# Роли пользователей
ROLE_ADMIN = "admin"       
ROLE_WAREHOUSE = "warehouse"  
ROLE_VIEWER = "viewer"    


users = {}


current_user = None


def register(username: str, password: str, role: str = ROLE_VIEWER) -> bool:
    if username in users:
        print(f"Ошибка: пользователь '{username}' уже существует.")
        return False

    if role not in (ROLE_ADMIN, ROLE_WAREHOUSE, ROLE_VIEWER):
        print(f"Ошибка: неизвестная роль '{role}'.")
        return False

    users[username] = {
        "id": len(users) + 1,
        "username": username,
        "password": generate_password_hash(password, method="pbkdf2:sha256"),
        "role": role
    }
    print(f"Пользователь '{username}' зарегистрирован с ролью '{role}'.")
    return True


def login(username: str, password: str) -> bool:
    """Вход в систему по логину и паролю."""
    global current_user

    user = users.get(username)
    if not user:
        print("Ошибка: пользователь не найден.")
        return False

    if not check_password_hash(user["password"], password):
        print("Ошибка: неверный пароль.")
        return False

    current_user = user
    print(f"Добро пожаловать, {username}! Роль: {user['role']}")
    return True


def logout():
    """Выход из системы."""
    global current_user
    if current_user:
        print(f"Пользователь '{current_user['username']}' вышел из системы.")
    current_user = None


def require_auth() -> bool:
    """Проверка: авторизован ли пользователь."""
    if current_user is None:
        print("Ошибка: необходима авторизация.")
        return False
    return True


def require_role(*roles) -> bool:
    """Проверка роли. Пример: require_role(ROLE_ADMIN, ROLE_WAREHOUSE)"""
    if not require_auth():
        return False
    if current_user["role"] not in roles:
        print(f"Ошибка 403: недостаточно прав. Требуется роль: {' или '.join(roles)}.")
        return False
    return True
