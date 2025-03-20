from models.model import *
from itertools import permutations
from typing import List, Optional

def get_x_from_location(location: Location):
    print(location.x)
    return location.x

def generate__all_orders_sequences(orders):
    # Generate all combinations of order
    return list(permutations(orders))

def find_warehouse_with_product(warehouses: List[Warehouse], product_id, quantity):
    for warehouse in warehouses:
        if product_id in warehouse.stock and warehouse.stock[product_id] >= quantity:
            return warehouse
    return None


def simulate(sequence, drones, warehouses, orders, products, max_turns):
    current_time = 0
    total_score = 0
    
    for order in sequence:
        for product_id in list(order.items.keys()):
            product = products[product_id]
            quantity = order.items[product_id]
            # Find the nearest warehouse with the product in stock
            warehouse = find_warehouse_with_product(warehouses, product_id, quantity)
            if warehouse:
                # Calculate the distance from the drone to the warehouse
                distance_to_warehouse = drones[0].move_to(warehouse.location)
                current_time += distance_to_warehouse
                if current_time > max_turns:
                    return 0  # If the turn limit is exceeded, return a score of zero
                
                # Load the product onto the drone
                drones[0].load(warehouse, product, quantity)
                
                # Calculate the distance from the warehouse to the customer
                distance_to_customer = drones[0].move_to(order.location)
                current_time += distance_to_customer
                if current_time > max_turns:
                    return 0
                
                # Deliver the product
                drones[0].deliver(order, product, quantity)
                
                # Calculate the score based on the completion turn
                order_score = (1 - (current_time / max_turns)) * 100
                total_score += order_score
                
                # Return to the initial warehouse
                distance_back = drones[0].move_to(warehouse.location)
                current_time += distance_back
                if current_time > max_turns:
                    return 0
    
    return total_score