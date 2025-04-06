import math

class Location:
    def __init__(self, x: int, y: int): 
        self.x = x # Position in X-axis
        self.y = y # Position in Y-axis
    def euclidean_distance(self, other: "Location") -> int:
        distance = math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)
        return math.ceil(distance)
    def __eq__(self, other):
        if isinstance(other, Location):
            return self.x == other.x and self.y == other.y
        return NotImplemented
    def __ne__(self, other):
        return not self == other
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
        self.busy_until = 0
        self.current_task = None
        self.queue = []

    def move_to(self, location: Location) -> int:
        distance = self.location.euclidean_distance(location)
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
            else:
                print("Drone overloaded")
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
    def __init__(self, simulation_data: dict):
        self.grid = Grid(simulation_data["simulation"]["rows"], simulation_data["simulation"]["cols"])

        self.drones = []
        for drone_id in range(simulation_data["simulation"]["drones"]):
            drones_initial_location = Location(*simulation_data["warehouses"][0]["location"])
            self.drones.append(Drone(drone_id, drones_initial_location, simulation_data["simulation"]["max_load"]))

        self.products = []
        for product_id, weight in enumerate(simulation_data["product_weights"]):
            self.products.append(Product(product_id, weight))
        
        self.warehouses = []
        for warehouse_id, warehouse_data in enumerate(simulation_data["warehouses"]):
            self.warehouses.append(Warehouse(warehouse_id, Location(*warehouse_data["location"]), {product_id: quantity for product_id, quantity in enumerate(warehouse_data["stock"])}))

        self.orders = []
        for order_id, order_data in enumerate(simulation_data["orders"]):
            product_counts = {}
            for product_type in order_data["product_types"]:
                if product_type in product_counts:
                    product_counts[product_type] += 1
                else:
                    product_counts[product_type] = 1
            self.orders.append(Order(order_id, Location(*order_data["destination"]), product_counts))

        self.time = 0
        self.deadline = simulation_data["simulation"]["deadline"]

    def testing_parse(self):
        # Printing simulation grid
        print(f"Grid: {self.grid.rows} rows x {self.grid.cols} columns")

        # Printing deadline = Max Turns
        print(f"\nDeadline: {self.deadline} turns")
        
        # Printing drones
        print(f"\nDrones (Total: {len(self.drones)}):")
        for drone in self.drones:
            print(f"  Drone ID: {drone.drone_id}, Initial Location: {drone.location.x}, {drone.location.y}, Max Load: {drone.max_payload}")
        
        # Printing products
        print(f"\nProducts (Total: {len(self.products)}):")
        for product in self.products:
            print(f"  Product ID: {product.product_id}, Weight: {product.weight} units")
        
        # Printing warehouses
        print(f"\nWarehouses (Total: {len(self.warehouses)}):")
        for warehouse in self.warehouses:
            print(f"  Warehouse ID: {warehouse.warehouse_id}, Location: ({warehouse.location.x}, {warehouse.location.y})")
            print("    Stock:")
            for product_id, quantity in warehouse.stock.items():
                print(f"      Product {product_id}: {quantity} items")
        
        # Printing orders
        print(f"\nOrders (Total: {len(self.orders)}):")
        for order in self.orders:
            print(f"  Order ID: {order.order_id}, Destination: ({order.location.x}, {order.location.y})")
            print(f"    Products Ordered:")
            for product_id, quantity in order.items.items():
                print(f"      Product {product_id}: {quantity} items")
    
    def list_orders(self):
        orders_set = []
        for orders in self.orders:
            orders_set.append(orders.order_id)
        return orders_set
    def list_warehouses(self):
        warehouses_set = []
        for warehouse in self.warehouses:
            warehouses_set.append(warehouse.warehouse_id)
        return warehouses_set
    
    def list_drones(self):
        drones_set = []
        for drone in self.drones:
            drones_set.append(drone.drone_id)
        return drones_set

    def run(self):
        """
        Run the simulation
        """
        pass # Implement algorithms and call them here

class Action:
    def __init__(self, type, product_id, quantity, warehouse):
        self.type = type
        self.product_id = product_id
        self.quantity = quantity
        self.warehouse = warehouse
    