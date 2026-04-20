# Модуль уведомлений

class Notification:
    def __init__(self, message, type):
        self.message = message
        self.type = type

    def send(self):
        print(f"Уведомление: {self.message}")