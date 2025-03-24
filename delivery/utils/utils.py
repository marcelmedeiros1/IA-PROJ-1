from models.model import *
from itertools import permutations
from typing import List, Optional
from collections import defaultdict
import copy

def generate__all_orders_sequences(orders):
    # Generate all combinations of order
    return list(permutations(orders))

def find_warehouse_with_product(warehouses: List[Warehouse], product_id, quantity):
    for warehouse in warehouses:
        if product_id in warehouse.stock and warehouse.stock[product_id] >= quantity:
            return warehouse
    return None

def get_best_drone(drones, target_location):
    best_drone = None
    min_distance = float('inf')
    
    for drone in drones:
        distance = drone.location.euclidean_distance(target_location)
        if distance < min_distance:
            best_drone = drone
            min_distance = distance

    return best_drone

def simulate_turns(drones, warehouses, orders, products, max_turns):
    current_turn = 0
    total_score = 0

    reserved_items = defaultdict(lambda: defaultdict(int))
    pending_orders = {o.order_id: o for o in orders}
    order_completion_turn = {}
    drone_logs = defaultdict(list)

    while current_turn <= max_turns and pending_orders:
        for drone in drones:
            if drone.busy_until <= current_turn:
                if not drone.queue:
                    for order in list(pending_orders.values()):
                        for product_id, quantity in list(order.items.items()):
                            product = products[product_id]
                            warehouse = find_warehouse_with_product(warehouses, product_id, quantity)
                            if warehouse:
                                available_to_reserve = order.items[product_id] - reserved_items[order.order_id][product_id]
                                if available_to_reserve > 0:
                                    quantity_to_reserve = min(quantity, available_to_reserve)
                                    reserved_items[order.order_id][product_id] += quantity_to_reserve
                                    drone.queue.append(('load', warehouse, product, quantity_to_reserve, order))
                                    drone.queue.append(('deliver', order, product, quantity_to_reserve))
                                break
                        break

                if drone.queue:
                    action = drone.queue.pop(0)

                    if action[0] == 'load':
                        _, warehouse, product, quantity, order = action
                        if drone.location != warehouse.location:
                            dist = drone.location.euclidean_distance(warehouse.location)
                            start = current_turn
                            end = current_turn + dist
                            drone.move_to(warehouse.location)
                            drone_logs[drone.drone_id].append(f"● flies to warehouse {warehouse.warehouse_id} in turns {start} to {end}")
                            drone.busy_until = end + 1
                        drone.load(warehouse, product, quantity)
                        drone_logs[drone.drone_id].append(f"● loads item {product.product_id} from warehouse {warehouse.warehouse_id} in turn {drone.busy_until}")

                    elif action[0] == 'deliver':
                        _, order, product, quantity = action
                        if drone.location != order.location:
                            dist = drone.location.euclidean_distance(order.location)
                            start = current_turn
                            end = current_turn + dist
                            drone.move_to(order.location)
                            drone_logs[drone.drone_id].append(f"● flies to order {order.order_id} in turns {start} to {end}")
                            drone.busy_until = end + 1
                        drone.deliver(order, product, quantity)
                        drone_logs[drone.drone_id].append(f"● delivers item {product.product_id} to order {order.order_id} in turn {drone.busy_until}")

                        if all(qty == 0 for qty in order.items.values()):
                            order_completion_turn[order.order_id] = drone.busy_until
                            del pending_orders[order.order_id]
                            score = ((max_turns - drone.busy_until) / max_turns) * 100
                            drone_logs[drone.drone_id].append(f"● Order {order.order_id} is now fulfilled, scoring {score:.0f} points")

        current_turn += 1

    # Score total
    for order_id, turn in order_completion_turn.items():
        score = ((max_turns - turn) / max_turns) * 100
        total_score += score

    # Imprimir logs organizados por drone
    print("\n=== DRONE LOGS ===")
    for drone_id in sorted(drone_logs.keys()):
        print(f"\nDrone {drone_id}:")
        for log in drone_logs[drone_id]:
            print(log)

    return total_score
