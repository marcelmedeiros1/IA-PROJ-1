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
                        execute_load_action(drone, action, current_turn, drone_logs)
                        load = Action('load', product.product_id, quantity, warehouse)
                        drones_actions[drone.drone_id][order.order_id].append(load)
                        # print(f"Drone {drone.drone_id} loaded {quantity} of product {product.product_id} from warehouse {warehouse.warehouse_id} in turn {completed_load}")

                    if action[0] == 'deliver':
                        execute_deliver_action(drone, action, current_turn, drone_logs, order_completion_turn, pending_orders, max_turns)
                        delivery = Action('deliver', product.product_id, quantity, warehouse)
                        drones_actions[drone.drone_id][order.order_id].append(delivery)
                                        
        current_turn += 1

    return drones_actions

def simulated_annealing(drones, warehouses, orders, products, max_turns, initial_temperature, cooling_rate, min_temperature, max_iterations):
    # Inicializar a solução atual usando o algoritmo guloso
    current_orders = {o.order_id: o for o in orders}
    current_orders = dict(sorted(current_orders.items(), key=lambda item: len(item[1].items))) # Greedy Strategy: Inspiration - https://github.com/msagi/hash-code-2016-qualification/blob/master/README.md
    drones_actions = simulate(copy.deepcopy(drones), copy.deepcopy(warehouses), copy.deepcopy(current_orders), products, max_turns)
    current_score = calculate_score(drones_actions, copy.deepcopy(current_orders), max_turns)

    best_score = current_score
    temperature = initial_temperature
    iteration = 0

    while temperature > min_temperature and iteration < max_iterations:
        print(f"\nIniciando iteração {iteration} com temperatura {temperature:.2f}")

        # Gerar uma solução vizinha
        operator = random.choice([
            move_order_to_another_drone,
            reorder_drone_actions,
            swap_action_pairs_between_drones  
        ])

        new_drones_actions = operator(copy.deepcopy(drones_actions))
        new_score = calculate_score(new_drones_actions, copy.deepcopy(current_orders), max_turns)
        print(f"[Iter {iteration}] Score atual: {current_score:.2f} | Novo: {new_score:.2f}")
            # Calcular a diferença de score
        delta = new_score - current_score
        
        # Decidir se aceita a nova solução
        if delta > 0 or random.random() < math.exp(delta / temperature):
            current_score = new_score
        
        # Atualizar a melhor solução encontrada
        if current_score > best_score:
            print(f"[Iter {iteration}] Score atual: {current_score:.2f} | Melhor: {best_score:.2f} | Temp: {temperature:.4f}")
            best_score = current_score
            best_orders = copy.deepcopy(current_orders)
        
        # Resfriar a temperatura
        temperature *= cooling_rate

        iteration += 1
    
    return best_orders, best_score


def move_order_to_another_drone(drones_actions):
    """Move um pedido inteiro de um drone para outro."""
    drone_ids = list(drones_actions.keys())
    if len(drone_ids) < 2:
        return drones_actions

    drone_from, drone_to = random.sample(drone_ids, 2)
    orders_from = drones_actions[drone_from]
    if not orders_from:
        return drones_actions

    order_id = random.choice(list(orders_from.keys()))
    actions = orders_from.pop(order_id)

    if order_id not in drones_actions[drone_to]:
        drones_actions[drone_to][order_id] = []

    drones_actions[drone_to][order_id].extend(actions)
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

def swap_action_pairs_between_drones(drones_actions):
    """Troca um par (load + deliver) entre dois drones."""
    drone_ids = list(drones_actions.keys())
    if len(drone_ids) < 2:
        return drones_actions

    drone1, drone2 = random.sample(drone_ids, 2)
    orders1 = drones_actions[drone1]
    orders2 = drones_actions[drone2]

    if not orders1 or not orders2:
        return drones_actions

    order1_id = random.choice(list(orders1.keys()))
    order2_id = random.choice(list(orders2.keys()))
    actions1 = orders1[order1_id]
    actions2 = orders2[order2_id]

    if len(actions1) < 2 or len(actions2) < 2:
        return drones_actions

    # Troca os dois primeiros pares de ação
    actions1[:2], actions2[:2] = actions2[:2], actions1[:2]
    drones_actions[drone1][order1_id] = actions1
    drones_actions[drone2][order2_id] = actions2

    return drones_actions


def calculate_score(drones_actions, orders, max_turns):
    """Calcula o score total de todas as ações dos drones."""
    total_score = 0
    order_completion_turn = {}
    order_remaining_items = {order_id: copy.deepcopy(orders[order_id].items) for order_id in orders}
    drone_states = {}
    
    for drone_id in drones_actions:
        drone_states[drone_id] = {
            "location": None,  # Inicialize se quiser com localização do drone
            "turn": 0
        }

    for drone_id, orders_actions in drones_actions.items():
        state = drone_states[drone_id]

        for order_id, actions in orders_actions.items():
            for action in actions:
                # Calcular o tempo até o local (simplificado)
                target_location = None
                if action.type == 'load':
                    target_location = action.warehouse.location
                elif action.type == 'deliver':
                    target_location = orders[order_id].location

                if state["location"] is not None:
                    dist = state["location"].euclidean_distance(target_location)
                else:
                    dist = 0  # Se a localização não for conhecida, assume que começa lá

                # Move e atualiza tempo
                state["turn"] += math.ceil(dist)
                state["location"] = target_location

                # Tempo da ação (load/deliver)
                state["turn"] += 1

                if action.type == 'deliver':
                    # Atualiza o pedido
                    remaining = order_remaining_items[order_id]
                    if(action.product_id in remaining):
                        remaining[action.product_id] -= action.quantity
                        if remaining[action.product_id] <= 0:
                            remaining[action.product_id] = 0

                    # Verifica se o pedido foi concluído
                    if all(qty == 0 for qty in remaining.values()):
                        if order_id not in order_completion_turn:
                            order_completion_turn[order_id] = state["turn"]

    # Agora calcula o score
    for order_id, completion_turn in order_completion_turn.items():
        score = ((max_turns - completion_turn) / max_turns) * 100
        total_score += score

    return total_score