class InventoryItem:
    def __init__(self, name, sku, quantity):
        self.name = name
        self.sku = sku
        self.quantity = quantity
    
    def add_stock(self, amount):
        if amount > 0:
            self.quantity += amount
            return True
        return False
    
    def remove_stock(self, amount):
        if 0 < amount <= self.quantity:
            self.quantity -= amount
            return True
        return False
    
    def is_low_stock(self, threshold=5):
        return self.quantity <= threshold

class InventoryManager:
    def __init__(self):
        self.items = {}
    
    def add_item(self, item):
        self.items[item.sku] = item
    
    def get_item(self, sku):
        return self.items.get(sku)
    
    def get_low_stock_items(self, threshold=5):
        return [item for item in self.items.values() if item.is_low_stock(threshold)]