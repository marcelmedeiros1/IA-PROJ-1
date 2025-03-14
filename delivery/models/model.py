class Location:
    def __init__(self, x: int, y: int): 
        self.x = x # Position in X-axis
        self.y = y # Position in Y-axis

class Grid: 
    def __init__(self, rows: int, cols: int): 
        self.rows = rows # Number of            rows in the grid 
        self.cols = cols # Number of columns in the grid
    
    def is_valid_location(self, location: Location) -> bool:
        return 0 <= location.x < self.rows and 0 <= location.y < self.cols

class Product:
    def __init__(self, product_id: int, weight: int):
        self.product_id = product_id  # Unique product identifier
        self.weight = weight  # Weight of a single unit of this product

class Warehouse:
    def __init__(self, warehouse_id: int, location: tuple, stock: dict):
        self.warehouse_id = warehouse_id  # Warehouse identifier
        self.location = location  # Tuple (row, col) on the grid
        self.stock = stock  # Dictionary {product_id: quantity}

class Order:
    def __init__(self, order_id: int, location: tuple, items: dict):
        self.order_id = order_id  # Unique order identifier
        self.location = location  # Tuple (row, col) on the grid
        self.items = items  # Dictionary {product_id: quantity}
        self.completed = False  # Whether the order has been fulfilled
