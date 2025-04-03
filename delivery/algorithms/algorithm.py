import random
import math
import copy
from collections import defaultdict
from typing import List
from models.model import *



class AntColonyOpt:
    def __init__(self, grid, drones, warehouses, orders, products, num_ants, num_iterations=100, alpha=1.0, beta=2.0, evaporation_rate=0.5, q=100):
        self.grid = grid
        self.drones = drones
        self.warehouses = warehouses
        self.orders = orders
        self.products = products
        self.num_iterations = num_iterations
        self.alpha = alpha
        self.beta = beta
        self.evaporation_rate = evaporation_rate
        self.num_ants = num_ants
        self.q = q
        self.pheromone = {(w.warehouse_id, o.order_id): 1.0 for w in self.warehouses for o in self.orders}
        self.best_path = []
        self.best_path_distance = math.inf

    def heuristic(self, warehouse, order):
        return 1 / (1 + warehouse.location.euclidean_distance(order.location))

    def select_path(self, warehouse, order):
        pheromone_value = self.pheromone[(warehouse.warehouse_id, order.order_id)] ** self.alpha
        heuristic_value = self.heuristic(warehouse, order) ** self.beta
        return pheromone_value * heuristic_value

    def run(self):
        for iteration in range(self.num_iterations):
            solutions = []
            for ant in range(self.num_ants):
                solution, cost = self.construct_solution()
                solutions.append((solution, cost))
                if cost < self.best_path_distance:
                    self.best_path = solution
                    self.best_path_distance = cost
            self.update_pheromone(solutions)
        return self.best_path

    def construct_solution(self):
        solution = []
        cost = 0

        new_warehouses = copy.deepcopy(self.warehouses)
        new_orders = copy.deepcopy(self.orders)
        new_drones = copy.deepcopy(self.drones)
        """"
        print("\n### Estoque Inicial dos Armazéns ###")
        for warehouse in new_warehouses:
            print(f"Armazém {warehouse.warehouse_id} (Posição: {warehouse.location.x}, {warehouse.location.y})")
            for product_id, quantity in warehouse.stock.items():
                print(f"  Produto {product_id}: {quantity} unidades")

        print("\n### Lista de Pedidos ###")
        for order in new_orders:
            print(f"Pedido {order.order_id} -> Destino: ({order.location.x}, {order.location.y})")
            for product_id, quantity in order.items.items():
                print(f"  Produto {product_id}: {quantity} unidades")
        """
        for order in new_orders:
           # print(f"\n🔍 Verificando Pedido {order.order_id} (Destino: {order.location.x}, {order.location.y})")
           # print(f"Produtos Necessários: {order.items}")

            order_solution = []  # Solução específica para esta ordem
            warehouses_visited = []  # Lista de armazéns visitados
            commands = []  # Sequência de comandos

            for product_id, quantity in list(order.items.items()):  # Iterar sobre os produtos necessários para a ordem
                remaining_quantity = quantity  # Quantidade restante a ser carregada

                while remaining_quantity > 0:
                    # Filtrar armazéns que têm o produto necessário em quantidade suficiente
                    valid_warehouses_with_stock = [
                        w for w in new_warehouses if w.stock.get(product_id, 0) > 0
                    ]

                    if not valid_warehouses_with_stock:
                        raise Exception(f"Nenhum armazém tem estoque suficiente do produto {product_id} para atender ao pedido {order.order_id}")

                    # Escolher o melhor armazém com base na heurística
                    best_warehouse = min(valid_warehouses_with_stock, key=lambda w: self.select_path(w, order))

                    # Determinar a quantidade a ser carregada deste armazém
                    load_quantity = min(remaining_quantity, best_warehouse.stock[product_id])

                    #print(f"Produto {product_id}: Melhor armazém selecionado -> {best_warehouse.warehouse_id} (Carregando {load_quantity} unidades)")

                    # Escolher o melhor drone com base na distância ao armazém
                    best_drone = min(new_drones, key=lambda d: d.location.euclidean_distance(best_warehouse.location))

                    #print(f"Pedido {order.order_id}: Drone {best_drone.drone_id} -> Warehouse {best_warehouse.warehouse_id}")

                    # Movimentação e custo
                    travel_time = best_drone.move_to(best_warehouse.location) + best_drone.move_to(order.location)
                    cost += travel_time

                    #print(f"Carregando produto {product_id} do armazém {best_warehouse.warehouse_id} para o drone {best_drone.drone_id}")
                    if not best_drone.load(best_warehouse, self.products[product_id], load_quantity):
                        raise Exception(f"Erro ao carregar produto {product_id} no drone {best_drone.drone_id}")

                    commands.append(f"Load {product_id} from Warehouse {best_warehouse.warehouse_id}")

                    if not best_drone.deliver(order, self.products[product_id], load_quantity):
                        raise Exception(f"Erro ao entregar produto {product_id} do pedido {order.order_id}")

                    commands.append(f"Deliver {product_id} to Order {order.order_id}")

                    # Atualizar a quantidade restante e o estoque do armazém
                    remaining_quantity -= load_quantity
                    best_warehouse.stock[product_id] -= load_quantity

                    # Adicionar o armazém visitado à lista
                    if best_warehouse.warehouse_id not in warehouses_visited:
                        warehouses_visited.append(best_warehouse.warehouse_id)

            # Adicionar a solução para esta ordem
            order_solution = [best_drone.drone_id, warehouses_visited, order.order_id, commands]
            solution.append(order_solution)

        return solution, cost

    def update_pheromone(self, solutions):
        # Evaporate pheromone
        for key in self.pheromone:
            self.pheromone[key] *= (1 - self.evaporation_rate)

        # Add pheromone based on solutions
        for solution, cost in solutions:
            pheromone_amount = self.q / cost
            for best_drone_id, warehouses_visited, order_id, commands in solution:
                for warehouse_id in warehouses_visited:
                    self.pheromone[(warehouse_id, order_id)] += pheromone_amount

    def print_solution(self):
        print("Ant Colony Optimization Solution:")
        print("=" * 40)
        for order_solution in self.best_path:
            best_drone_id, warehouses_visited, order_id, commands = order_solution
            print(f"Order ID: {order_id}")
            print(f"  Drone ID: {best_drone_id}")
            print(f"  Warehouses Visited: {', '.join(map(str, warehouses_visited))}")
            print(f"  Commands:")
            for command in commands:
                print(f"    - {command}")
        print("-" * 40)

class SimulatedAnnealingOptimizer:
    def __init__(self, drones, warehouses, orders, products, max_turns):
        self.drones = drones
        self.warehouses = warehouses
        self.orders = {o.order_id: o for o in orders}
        self.products = products
        self.max_turns = max_turns

    def find_warehouse_with_product(self, warehouses, product_id, quantity):
        for warehouse in warehouses:
            if product_id in warehouse.stock and warehouse.stock[product_id] >= quantity:
                return warehouse
        return None

    def assign_task_to_drone(self, drone, pending_orders, reserved_items, warehouses):
        for order in list(pending_orders.values()):
            for product_id, quantity in list(order.items.items()):
                product = self.products[product_id]
                warehouse = self.find_warehouse_with_product(warehouses, product_id, quantity)
                if warehouse:
                    available = order.items[product_id] - reserved_items[order.order_id][product_id]
                    if available > 0:
                        max_qty = (drone.max_payload - drone.payload) // product.weight
                        qty = min(quantity, available, max_qty)
                        if qty * product.weight <= (drone.max_payload - drone.payload):
                            reserved_items[order.order_id][product_id] += qty
                            drone.queue.append(('load', order, product, qty, warehouse))
                            drone.queue.append(('deliver', order, product, qty, warehouse))
                            return

    def execute_load_action(self, drone, action, current_turn, drone_logs):
        _, order, product, quantity, warehouse = action
        if drone.location != warehouse.location:
            dist = drone.location.euclidean_distance(warehouse.location)
            start, end = current_turn, current_turn + dist
            drone.move_to(warehouse.location)
            drone_logs[drone.drone_id].append(f"● flies to warehouse {warehouse.warehouse_id} in turns {start} to {end}")
            drone.busy_until = end + 1

        drone.load(warehouse, product, quantity)
        drone_logs[drone.drone_id].append(f"● loads item {product.product_id} from warehouse {warehouse.warehouse_id} in turn {drone.busy_until}")
        drone.busy_until += 1
        return drone.busy_until - 1

    def execute_deliver_action(self, drone, action, current_turn, drone_logs, order_completion_turn, pending_orders):
        _, order, product, quantity, warehouse = action
        if drone.location != order.location:
            dist = drone.location.euclidean_distance(order.location)
            start, end = current_turn, current_turn + dist
            drone.move_to(order.location)
            drone_logs[drone.drone_id].append(f"● flies to order {order.order_id} in turns {start} to {end}")
            drone.busy_until = end + 1

        drone.deliver(order, product, quantity)
        drone_logs[drone.drone_id].append(f"● delivers item {product.product_id} to order {order.order_id} in turn {drone.busy_until}")

        if all(qty == 0 for qty in order.items.values()):
            order_completion_turn[order.order_id] = drone.busy_until
            pending_orders.pop(order.order_id)
            score = ((self.max_turns - drone.busy_until) / self.max_turns) * 100
            drone_logs[drone.drone_id].append(f"● Order {order.order_id} fulfilled in turn {drone.busy_until}, score {score:.0f}")
        drone.busy_until += 1
        return drone.busy_until - 1

    def simulate(self, drones, warehouses, orders):
        drones_actions = defaultdict(lambda: defaultdict(list))
        current_turn = 0
        reserved_items = defaultdict(lambda: defaultdict(int))
        pending_orders = copy.deepcopy(orders)
        order_completion_turn = {}
        drone_logs = defaultdict(list)

        while pending_orders:
            for drone in drones:
                if drone.busy_until <= current_turn:
                    if not drone.queue:
                        self.assign_task_to_drone(drone, pending_orders, reserved_items, warehouses)
                    if drone.queue:
                        action = drone.queue.pop(0)
                        _, order, product, quantity, warehouse = action
                        if action[0] == 'load':
                            self.execute_load_action(drone, action, current_turn, drone_logs)
                            load = Action('load', product.product_id, quantity, warehouse)
                            drones_actions[drone.drone_id][order.order_id].append(load)
                        if action[0] == 'deliver':
                            self.execute_deliver_action(drone, action, current_turn, drone_logs, order_completion_turn, pending_orders)
                            delivery = Action('deliver', product.product_id, quantity, warehouse)
                            drones_actions[drone.drone_id][order.order_id].append(delivery)
            current_turn += 1

        return drones_actions

    def calculate_score(self, drones_actions, orders):
        total_score = 0
        order_completion_turn = {}
        order_remaining_items = {order_id: copy.deepcopy(orders[order_id].items) for order_id in orders}
        drone_states = {drone_id: {"location": Location(0,0), "turn": 0} for drone_id in drones_actions}

        for drone_id, orders_actions in drones_actions.items():
            state = drone_states[drone_id]
            for order_id, actions in orders_actions.items():
                for action in actions:
                    if action.type == 'load':
                        loc = action.warehouse.location
                        if state["location"].euclidean_distance(loc) > 0:
                            dist = state["location"].euclidean_distance(loc)
                            start, end = state["turn"], state["turn"] + math.ceil(dist)
                            state["turn"] = end + 1
                        state["location"] = loc
                        state["turn"] += 1
                    elif action.type == 'deliver':
                        loc = orders[order_id].location
                        remaining = order_remaining_items[order_id]
                        if state["location"].euclidean_distance(loc) > 0:
                            dist = state["location"].euclidean_distance(loc)
                            start, end = state["turn"], state["turn"] + math.ceil(dist)
                            state["turn"] = end + 1
                        state["location"] = loc
                        delivery_turn = state["turn"]
                        state["turn"] += 1
                        if action.product_id in remaining:
                            remaining[action.product_id] -= action.quantity
                            if remaining[action.product_id] <= 0:
                                remaining[action.product_id] = 0
                        if all(qty == 0 for qty in remaining.values()) and order_id not in order_completion_turn:
                            order_completion_turn[order_id] = delivery_turn

        total_score = sum(((self.max_turns - t) / self.max_turns) * 100 for t in order_completion_turn.values())

        return total_score

    # === OPERADORES ===
    def move_order_to_another_drone(self, drones_actions):
        drone_ids = list(drones_actions.keys())
        if len(drone_ids) < 2:
            return drones_actions
        drone_from, drone_to = random.sample(drone_ids, 2)
        orders_from = drones_actions[drone_from]
        if not orders_from:
            return drones_actions
        order_id = random.choice(list(orders_from.keys()))
        actions = orders_from.pop(order_id)
        drones_actions[drone_to].setdefault(order_id, []).extend(actions)
        return drones_actions

    def swap_entire_orders_between_drones(self, drones_actions):
        drone_ids = list(drones_actions.keys())
        if len(drone_ids) < 2:
            return drones_actions
        d1, d2 = random.sample(drone_ids, 2)
        orders1 = list(drones_actions[d1].keys())
        orders2 = list(drones_actions[d2].keys())
        if not orders1 or not orders2:
            return drones_actions

        o1 = random.choice(orders1)
        o2 = random.choice(orders2)

        drones_actions[d1][o1], drones_actions[d2][o2] = drones_actions[d2][o2], drones_actions[d1][o1]
        return drones_actions

    def run(self, initial_temperature, cooling_rate, min_temperature, max_iterations):
        current_orders = dict(sorted(self.orders.items(), key=lambda item: len(item[1].items)))
        drones_actions = self.simulate(copy.deepcopy(self.drones), copy.deepcopy(self.warehouses), current_orders)
        current_score = self.calculate_score(drones_actions, current_orders)

        best_score = current_score
        best_drones_actions = copy.deepcopy(drones_actions)
        temperature = initial_temperature
        iteration = 0

        while iteration < max_iterations and temperature > min_temperature:
            print(f"\n[Iter {iteration}] Temp: {temperature:.2f}")
            operator = random.choice([
                self.move_order_to_another_drone,
                # self.swap_entire_orders_between_drones
            ])
            new_drones_actions = operator(copy.deepcopy(drones_actions))
            new_score = self.calculate_score(new_drones_actions, copy.deepcopy(current_orders))
            delta = new_score - current_score

            if delta > 0 or (delta < 0 and random.random() < math.exp(delta / temperature)):
                drones_actions = new_drones_actions
                current_score = new_score
                print(f"✔️  Accepted Δ={delta:.2f}")

            if current_score > best_score:
                best_score = current_score
                best_drones_actions = copy.deepcopy(drones_actions)
                print(f"🌟 New Best Score: {best_score:.2f}")

            temperature *= cooling_rate
            iteration += 1

        save_drone_logs_to_file(self, best_drones_actions)
        print(f"✅ Final Best Score: {best_score:.2f}")
        
        return best_drones_actions, best_score
    

def save_drone_logs_to_file(self, drones_actions, filename="drone_logs.txt"):
    drone_logs = defaultdict(list)
    drone_states = {drone_id: {"location": Location(0,0), "turn": 0} for drone_id in drones_actions}
    orders_copy = copy.deepcopy(self.orders)
    order_completion_turn = {}

    for drone_id, orders in drones_actions.items():
        state = drone_states[drone_id]
        for order_id, actions in orders.items():
            for action in actions:
                order = orders_copy[order_id]
                if action.type == 'load':
                    loc = action.warehouse.location
                    if state["location"].euclidean_distance(loc) > 0:
                        dist = state["location"].euclidean_distance(loc)
                        start, end = state["turn"], state["turn"] + math.ceil(dist)
                        drone_logs[drone_id].append(f"● flies to warehouse {action.warehouse.warehouse_id} in turns {start} to {end}")
                        state["turn"] = end + 1
                    state["location"] = loc
                    drone_logs[drone_id].append(f"● loads item {action.product_id} from warehouse {action.warehouse.warehouse_id} in turn {state['turn']}")
                    state["turn"] += 1

                elif action.type == 'deliver':
                    loc = order.location
                    if state["location"].euclidean_distance(loc) > 0:
                        dist = state["location"].euclidean_distance(loc)
                        start, end = state["turn"], state["turn"] + math.ceil(dist)
                        drone_logs[drone_id].append(f"● flies to order {order.order_id} in turns {start} to {end}")
                        state["turn"] = end + 1
                    state["location"] = loc
                    delivery_turn = state["turn"]
                    drone_logs[drone_id].append(f"● delivers item {action.product_id} to order {order.order_id} in turn {delivery_turn}")
                    state["turn"] += 1
                    if action.product_id in order.items:
                        order.items[action.product_id] -= action.quantity
                        if order.items[action.product_id] <= 0:
                            order.items[action.product_id] = 0
                    if all(qty == 0 for qty in order.items.values()) and order_id not in order_completion_turn:
                        order_completion_turn[order_id] = delivery_turn
                        score = ((self.max_turns - state["turn"]) / self.max_turns) * 100
                        drone_logs[drone_id].append(f"● Order {order_id} has been fulfilled in turn {delivery_turn}, scoring {score:.0f} points")

    total_score = sum(((self.max_turns - t) / self.max_turns) * 100 for t in order_completion_turn.values())

    # Salva tudo no arquivo
    with open(filename, "w") as f:
        f.write("=== DRONE LOGS ===\n")
        for drone_id in sorted(drone_logs.keys()):
            f.write(f"\nDrone {drone_id}:\n")
            for log in drone_logs[drone_id]:
                f.write(log + "\n")
        f.write(f"\n✅ Total Score: {total_score:.2f}\n")

    print(f"📝 Logs salvos em '{filename}'")

    return total_score