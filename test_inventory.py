import unittest
from inventory import InventoryItem 

class TestInventoryItem(unittest.TestCase):
    
    def test_add_stock_increases_quantity(self):
       
        item = InventoryItem("Laptop", "SKU123", 10)
       
        result = item.add_stock(5)
        
        self.assertTrue(result)
      
        self.assertEqual(item.quantity, 15)


if __name__ == "__main__":
    unittest.main()