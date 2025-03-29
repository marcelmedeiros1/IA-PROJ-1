from models.model import *
from itertools import permutations
from typing import List, Optional
from collections import defaultdict
from itertools import product
import random
import math
import copy

def find_warehouse_with_product(warehouses: List[Warehouse], product_id, quantity):
    for warehouse in warehouses:
        if product_id in warehouse.stock and warehouse.stock[product_id] >= quantity:
            return warehouse
    return None

def execute_load_action(drone, action, current_turn, drone_logs):
    if action[0] == 'load':
        _, order, product, quantity, warehouse = action
        if drone.location != warehouse.location:
            dist = drone.location.euclidean_distance(warehouse.location)
            start = current_turn
            end = current_turn + dist
            drone.move_to(warehouse.location)
            drone_logs[drone.drone_id].append(f"● flies to warehouse {warehouse.warehouse_id} in turns {start} to {end}")
            drone.busy_until = end + 1
        
        drone.load(warehouse, product, quantity)
        drone_logs[drone.drone_id].append(f"● loads item {product.product_id} from warehouse {warehouse.warehouse_id} in turn {drone.busy_until}")
        drone.busy_until += 1
    
    return drone.busy_until - 1

def execute_deliver_action(drone, action, current_turn, drone_logs, order_completion_turn, pending_orders, max_turns):
    _, order, product, quantity, warehouse = action
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
        drone_logs[drone.drone_id].append(f"● Order {order.order_id} has been fulfilled in turn {drone.busy_until}, scoring {score:.0f} points")

    drone.busy_until += 1

    return drone.busy_until - 1

def assign_task_to_drone(drone, pending_orders, reserved_items, warehouses, products):
    found = False
    for order in list(pending_orders.values()):
        for product_id, quantity in list(order.items.items()):
            product = products[product_id]
            warehouse = find_warehouse_with_product(warehouses, product_id, quantity)
            if warehouse:
                available_to_reserve = order.items[product_id] - reserved_items[order.order_id][product_id]
                if available_to_reserve > 0:
                    max_loadable_quantity = (drone.max_payload - drone.payload) // product.weight
                    quantity_to_reserve = min(quantity, available_to_reserve)
                    quantity_to_reserve = min(quantity_to_reserve, max_loadable_quantity)
                    if (quantity_to_reserve * product.weight) <= (drone.max_payload - drone.payload):
                        found = True
                        reserved_items[order.order_id][product_id] += quantity_to_reserve
                        drone.queue.append(('load', order, product, quantity_to_reserve, warehouse))
                        drone.queue.append(('deliver', order, product, quantity_to_reserve, warehouse))
                        break
        if found:
            return f"Drone {drone.drone_id} is assigned to order {order.order_id} for product {product_id} with quantity {quantity}"
    if not found:
        return "No available orders to pick up"


def score_and_logs(order_completion_turn, max_turns, drone_logs):
    total_score = 0
    for order_id, turn in order_completion_turn.items():
        score = ((max_turns - turn) / max_turns) * 100
        total_score += score

    # Print Sequence of Actions
    print("\n=== DRONE LOGS ===")
    for drone_id in sorted(drone_logs.keys()):
        print(f"\nDrone {drone_id}:")
        for log in drone_logs[drone_id]:
            print(log)
    print(total_score)
    return total_score

def simulate(drones, warehouses, orders, products, max_turns): #Greedy Algorithm To Get Initial Solution
    drones_actions = defaultdict(lambda: defaultdict(list))
    current_turn = 0
    reserved_items = defaultdict(lambda: defaultdict(int))
    pending_orders = orders
    order_completion_turn = {}
    drone_logs = defaultdict(list)
    while pending_orders:
        for drone in drones:
            if drone.busy_until <= current_turn:
                if not drone.queue:
                    assign_task_to_drone(drone, pending_orders, reserved_items, warehouses, products)
                if drone.queue: 
                    action = drone.queue.pop(0)
                    _, order, product, quantity, warehouse = action
                    if action[0] == 'load':
                        completed_load = execute_load_action(drone, action, current_turn, drone_logs)
                        load = Action('load', product.product_id, quantity, warehouse, completed_load)
                        drones_actions[drone.drone_id][order.order_id].append(load)
                        # print(f"Drone {drone.drone_id} loaded {quantity} of product {product.product_id} from warehouse {warehouse.warehouse_id} in turn {completed_load}")

                    if action[0] == 'deliver':
                        completed_delivery = execute_deliver_action(drone, action, current_turn, drone_logs, order_completion_turn, pending_orders, max_turns)
                        delivery = Action('deliver', product.product_id, quantity, warehouse, completed_delivery)
                        drones_actions[drone.drone_id][order.order_id].append(delivery)
                                        
        current_turn += 1

    return score_and_logs(order_completion_turn, max_turns, drone_logs)

def swap_two_orders(pending_orders):
    """Gera uma nova ordem de atendimento trocando dois pedidos."""
    keys = list(pending_orders.keys())
    if len(keys) < 2:
        return pending_orders  # Nada para trocar
    i, j = random.sample(range(len(keys)), 2)
    keys[i], keys[j] = keys[j], keys[i]
    return {k: pending_orders[k] for k in keys}

def simulated_annealing(drones, warehouses, orders, products, max_turns, initial_temperature, cooling_rate, min_temperature, max_iterations):
    # Inicializar a solução atual usando o algoritmo guloso
    current_orders = {o.order_id: o for o in orders}
    current_orders = dict(sorted(current_orders.items(), key=lambda item: len(item[1].items)))
    current_score = simulate(copy.deepcopy(drones), copy.deepcopy(warehouses), copy.deepcopy(current_orders), products, max_turns)
    best_score = current_score
    best_orders = copy.deepcopy(current_orders)
    max_iterations= 20
    temperature = initial_temperature
    no_improvement_counter = 0
    iteration = 0

    orders_history = set()
    orders_history.add(tuple(current_orders.keys()))

    while temperature > min_temperature and iteration < max_iterations:
        # Gerar uma solução vizinha
        operator = random.choice([
            swap_actions_between_drones,
            reorder_drone_actions,
            modify_product_quantity,
        ])

        new_drones_actions = operator(copy.deepcopy(drones_actions), max_payload)
        new_orders_sequence = tuple(new_orders.keys())
        if(new_orders_sequence not in orders_history):
            orders_history.add(new_orders_sequence)
            print(f"Iniciando iteração {iteration}")
            new_score = simulate(copy.deepcopy(drones), copy.deepcopy(warehouses), copy.deepcopy(new_orders), products, max_turns)
            print("Terminei")
            
            # Calcular a diferença de score
            delta = new_score - current_score
            
            # Decidir se aceita a nova solução
            if delta > 0 or random.random() < math.exp(delta / temperature):
                current_orders = new_orders
                current_score = new_score
                no_improvement_counter = 0
            
            # Atualizar a melhor solução encontrada
            if current_score > best_score:
                print(f"[Iter {iteration}] Score atual: {current_score:.2f} | Melhor: {best_score:.2f} | Temp: {temperature:.4f}")
                best_score = current_score
                best_orders = copy.deepcopy(current_orders)
            
            # Resfriar a temperatura
            temperature *= cooling_rate

        iteration += 1
    
    return best_orders, best_score


def swap_actions_between_drones(drones_actions):
    """Troca uma sequência de ações entre dois drones."""
    drone_ids = list(drones_actions.keys())
    if len(drone_ids) < 2:
        return drones_actions  # Nada para trocar

    drone1, drone2 = random.sample(drone_ids, 2)
    order_ids1 = list(drones_actions[drone1].keys())
    order_ids2 = list(drones_actions[drone2].keys())

    if not order_ids1 or not order_ids2:
        return drones_actions  # Um dos drones não tem ações

    order1 = random.choice(order_ids1)
    order2 = random.choice(order_ids2)

    # Troca as ações entre os drones
    drones_actions[drone1][order1], drones_actions[drone2][order2] = (
        drones_actions[drone2][order2],
        drones_actions[drone1][order1],
    )

    return drones_actions

def reorder_drone_actions(drones_actions):
    """Reordena as ações de um drone específico."""
    drone_id = random.choice(list(drones_actions.keys()))
    order_ids = list(drones_actions[drone_id].keys())

    if not order_ids:
        return drones_actions  # Drone não tem ações

    order_id = random.choice(order_ids)
    actions = drones_actions[drone_id][order_id]

    if len(actions) < 2:
        return drones_actions  # Não há ações suficientes para reordenar

    # Reordena as ações aleatoriamente
    random.shuffle(actions)
    drones_actions[drone_id][order_id] = actions

    return drones_actions

def modify_product_quantity(drones_actions, max_payload):
    """Modifica a quantidade de um produto a ser carregado ou entregue."""
    drone_id = random.choice(list(drones_actions.keys()))
    order_ids = list(drones_actions[drone_id].keys())

    if not order_ids:
        return drones_actions  # Drone não tem ações

    order_id = random.choice(order_ids)
    actions = drones_actions[drone_id][order_id]

    if not actions:
        return drones_actions  # Não há ações para modificar

    action_index = random.randint(0, len(actions) - 1)
    action = actions[action_index]

    # Supondo que a ação seja uma tupla ('load'/'deliver', product_id, quantity, warehouse, turn)
    action_type, product_id, quantity, warehouse, turn = action

    # Modifica a quantidade respeitando a capacidade máxima de carga
    new_quantity = min(quantity + random.randint(-2, 2), max_payload)
    new_quantity = max(new_quantity, 1)  # Garante que seja pelo menos 1

    new_action = (action_type, product_id, new_quantity, warehouse, turn)
    actions[action_index] = new_action
    drones_actions[drone_id][order_id] = actions

    return drones_actions
