import math
from utils import utils

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

class Drone:
    def __init__(self, drone_id: int, location: Location, max_payload: int):
        self.drone_id = drone_id  # Unique drone identifier
        self.location = location  # Tuple (row, col) on the grid
        self.max_payload = max_payload
        self.payload = 0
        self.inventory = {} # Dictionary {product_id: quantity}
        self.busy = False

    def move_to(self, location: Location) -> int:
        distance = utils.euclidean_distance(self.location, location)
        self.location = location
        return distance
    
    def load(self, warehouse: Warehouse ,product: Product, quantity: int) -> bool:
        if product.product_id in warehouse.stock and warehouse.stock[product.product_id] >= quantity:
            totalWeight = sum(self.inventory.get(product.product_id, 0) * product.weight for product_id in self.inventory)
            if totalWeight + product.weight * quantity <= self.max_payload:
                self.inventory[product.product_id] = self.inventory.get(product.product_id, 0) + quantity
                self.payload += product.weight * quantity
                warehouse.stock[product.product_id] -= quantity
                return True
        return False
    
    def deliver(self, order: Order, product: Product, quantity: int) -> bool:
        if product.product_id in self.inventory and self.inventory[product.product_id] >= quantity:
            self.inventory[product.product_id] -= quantity
            self.payload -= product.weight * quantity
            order.items[product.product_id] -= quantity
            if(order.items[product.product_id] == 0):
                order.items.pop(product.product_id)
            if not order.items:
                order.completed = True
            return True
        return False
    
class Simulation:
    def __init__(self, grid: Grid, products: list ,drones: list, warehouses: list, orders: list):
        self.grid = grid
        self.drones = drones
        self.products = products
        self.warehouses = warehouses
        self.orders = orders
        self.time = 0

    def run(self):
        """
        Run the simulation
        """
        pass # Implement algorithms and call them here
        
