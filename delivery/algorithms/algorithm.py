import random
import math
import copy
from collections import defaultdict
from typing import List
from models.model import *



class AntColonyOpt:
    def __init__(self, grid, drones, warehouses, orders, products, num_ants, num_turns,num_iterations=10, alpha=1.0, beta=2.0, evaporation_rate=0.5, q=100):
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
        self.num_turns = num_turns
        self.aux_turns = num_turns
        self.q = q
        self.pheromone = {(w.warehouse_id, o.order_id): 1.0 for w in self.warehouses for o in self.orders}
        self.best_path = []
        self.score = 0
        self.in_turns = 0
        self.completed_turns = 0
        self.best_path_distance = 0
    
    def construct_score(self):
        score = ((self.num_turns - self.in_turns) / self.num_turns) * 100
        self.in_turns = 0
        return score

    def heuristic(self, warehouse, order):
        return 1 / (1 + warehouse.location.euclidean_distance(order.location))

    def select_path(self, warehouse, order):
        pheromone_value = self.pheromone[(warehouse.warehouse_id, order.order_id)] ** self.alpha
        heuristic_value = self.heuristic(warehouse, order) ** self.beta
        return pheromone_value * heuristic_value

    def run(self, progress_callback=None):
        for iteration in range(self.num_iterations):
            solutions = []
            for ant in range(self.num_ants):
                solution, score, completed_turns = self.construct_solution()
                solutions.append((solution, score, completed_turns))
                if score > self.best_path_distance:
                    self.best_path = solution
                    self.best_path_distance = score
                    self.completed_turns = completed_turns
                    if progress_callback:
                        progress_callback(iteration, score)
                        print(f"🌟 New Best Score: {score:.2f}")
            self.update_pheromone(solutions)
        self.score = self.best_path_distance
        return self.best_path, self.score

    def construct_solution(self):
        solution = []

        new_warehouses = copy.deepcopy(self.warehouses)
        new_orders = copy.deepcopy(self.orders)
        new_drones = copy.deepcopy(self.drones)
        completed_turns = 0
        score = 0

        for order in new_orders:
            order_solution = []  # Solution specific to this order
            warehouses_visited = []  # List of warehouses visited
            commands = []  # Sequence of commands
            drones_used = []  # List of drones used for this order

            for product_id, quantity in list(order.items.items()):  # Iterate over the products required for the order
                remaining_quantity = quantity  # Quantity left to be delivered

                while remaining_quantity > 0:
                    # Filter warehouses that have the required product in stock
                    valid_warehouses_with_stock = [
                        w for w in new_warehouses if w.stock.get(product_id, 0) > 0
                    ]

                    if not valid_warehouses_with_stock:
                        raise Exception(f"Nenhum armazém tem estoque suficiente do produto {product_id} para atender ao pedido {order.order_id}")

                    # Choose the best warehouse based on the heuristic
                    best_warehouse = min(valid_warehouses_with_stock, key=lambda w: self.select_path(w, order))

                    # Determine the maximum quantity that can be loaded by a single drone
                    load_quantity = min(
                        remaining_quantity,
                        best_warehouse.stock[product_id],
                        max(d.max_payload for d in new_drones) // self.products[product_id].weight
                    )

                    if load_quantity == 0:
                        raise Exception(f"Produto {product_id} não pode ser carregado por nenhum drone devido ao peso.")

                    # Check if the drone can carry the load
                    count = new_drones.__len__()
                    aux = copy.deepcopy(new_drones)
                    while count > 0:
                        # Choose the best drone based on the distance to the warehouse
                        best_drone_aux = min(aux, key=lambda d: d.location.euclidean_distance(best_warehouse.location))
                        if (best_drone_aux.payload + self.products[product_id].weight * load_quantity) > best_drone_aux.max_payload:
                            # If the drone cannot carry the load, try another drone
                            aux.remove(best_drone_aux)
                        else:
                            for drone in new_drones:
                                if drone.drone_id == best_drone_aux.drone_id:
                                    best_drone = drone
                            break
                        count -= 1

                    # Add the drone to the list of drones used for this order
                    if best_drone.drone_id not in drones_used:
                        drones_used.append(best_drone.drone_id)

                    self.in_turns += best_drone.move_to(best_warehouse.location)
                    # Load the product onto the drone
                    if not best_drone.load(best_warehouse, self.products[product_id], load_quantity):
                        raise Exception(f"Erro ao carregar produto {product_id} no drone {best_drone.drone_id}")

                    commands.append(f"Load {product_id} from Warehouse {best_warehouse.warehouse_id}")
                    self.in_turns += 1

                    self.in_turns += best_drone.move_to(order.location)
                    # Deliver the product to the order location
                    if not best_drone.deliver(order, self.products[product_id], load_quantity):
                        raise Exception(f"Erro ao entregar produto {product_id} do pedido {order.order_id}")

                    commands.append(f"Deliver {product_id} to Order {order.order_id}")
                    self.in_turns += 1

                    # Update the remaining quantity and warehouse stock
                    remaining_quantity -= load_quantity

                    # Add the warehouse to the list of visited warehouses
                    if best_warehouse.warehouse_id not in warehouses_visited:
                        warehouses_visited.append(best_warehouse.warehouse_id)

            # Add the solution for this order
            order_solution = [drones_used, warehouses_visited, order.order_id, commands]
            solution.append(order_solution)
            completed_turns += self.in_turns
            score += self.construct_score()

        return solution, score, completed_turns

    def update_pheromone(self, solutions):
        # Evaporate pheromone
        for key in self.pheromone:
            self.pheromone[key] *= (1 - self.evaporation_rate)

        # Add pheromone based on solutions
        for solution, cost, completed_turns in solutions:
            pheromone_amount = self.q / cost
            for drones_used, warehouses_visited, order_id, commands in solution:
                for warehouse_id in warehouses_visited:
                    self.pheromone[(warehouse_id, order_id)] += pheromone_amount

    def print_solution(self):
        print("Ant Colony Optimization Solution:")
        print("=" * 40)
        for order_solution in self.best_path:
            drones_used, warehouses_visited, order_id, commands = order_solution
            print(f"Order ID: {order_id}")
            print(f"  Drones Used: {', '.join(map(str, drones_used))}")
            print(f"  Warehouses Visited: {', '.join(map(str, warehouses_visited))}")
            print(f"  Commands:")
            for command in commands:
                print(f"    - {command}")
        print("-" * 40)
        print("Ant Colony Optimization Solution:")
        print("=" * 40)
        print(f"Completed in {round(self.completed_turns)} turns")
        print(f"Score: {self.score:.2f}")
        print("-" * 40)

class SimulatedAnnealingOptimizer:
    def __init__(self, drones, warehouses, orders, products, max_turns):
        self.drones = drones
        self.warehouses = warehouses
        self.orders = {o.order_id: o for o in orders}
        self.products = products
        self.max_turns = max_turns
        self.score = 0
        self.completed_turns = 0
        self.best_path = []
        self.best_path_distance = math.inf

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
        
        self.completed_turns = current_turn

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

    def invert_order_sequence(self, drones_actions):
        drone_id = random.choice(list(drones_actions.keys()))
        orders = list(drones_actions[drone_id].keys())
        if len(orders) < 2:
            return drones_actions
        i, j = sorted(random.sample(range(len(orders)), 2))
        orders[i:j+1] = reversed(orders[i:j+1])
        new_actions = {order: drones_actions[drone_id][order] for order in orders}
        drones_actions[drone_id] = new_actions
        return drones_actions
    
    def insert_order_at_new_position(self, drones_actions):
        drone_id = random.choice(list(drones_actions.keys()))
        orders = list(drones_actions[drone_id].keys())
        if len(orders) < 2:
            return drones_actions
        order = orders.pop(random.randint(0, len(orders) - 1))
        new_position = random.randint(0, len(orders))
        orders.insert(new_position, order)
        new_actions = {order: drones_actions[drone_id][order] for order in orders}
        drones_actions[drone_id] = new_actions
        return drones_actions


    def run(self, initial_temperature, cooling_rate, min_temperature, max_iterations, progress_callback=None):
        current_orders = dict(sorted(self.orders.items(), key=lambda item: len(item[1].items)))
        drones_actions = self.simulate(copy.deepcopy(self.drones), copy.deepcopy(self.warehouses), current_orders)
        current_score = self.calculate_score(drones_actions, current_orders)

        best_score = current_score
        best_drones_actions = copy.deepcopy(drones_actions)
        temperature = initial_temperature
        iteration = 0

        while iteration < max_iterations and temperature > min_temperature:
            operator = random.choice([
                self.move_order_to_another_drone,
                self.invert_order_sequence,
                self.insert_order_at_new_position
            ])
            new_drones_actions = operator(copy.deepcopy(drones_actions))
            new_score = self.calculate_score(new_drones_actions, copy.deepcopy(current_orders))
            delta = new_score - current_score

            if delta > 0 or (delta < 0 and random.random() < math.exp(delta / temperature)):
                drones_actions = new_drones_actions
                current_score = new_score

            if current_score > best_score:
                best_score = current_score
                best_drones_actions = copy.deepcopy(drones_actions)
                self.best_path = self.extract_best_path(best_drones_actions)
                if(progress_callback):
                    progress_callback(iteration, best_score)
                    print(f"🌟 New Best Score: {best_score:.2f}")

            temperature *= cooling_rate
            iteration += 1

        self.score = best_score
        self.save_solution_to_file()
        print(f"✅ Final Best Score: {best_score:.2f}")
        
        return best_drones_actions, best_score
    
    def extract_best_path(self, drones_actions):
        best_path = []
        for drone_id, orders in drones_actions.items():
            for order_id, actions in orders.items():
                warehouses = []
                commands = []
                for action in actions:
                    if action.type == 'load':
                        cmd = f"Load {action.product_id} from Warehouse {action.warehouse.warehouse_id}"
                        if action.warehouse.warehouse_id not in warehouses:
                            warehouses.append(action.warehouse.warehouse_id)
                    elif action.type == 'deliver':
                        cmd = f"Deliver {action.product_id} to Order {order_id}"
                    commands.append(cmd)
                best_path.append(([drone_id], warehouses, order_id, commands))
        return best_path
    
    def save_solution_to_file(self, filename="solution_output.txt"):
        with open(filename, "w") as f:
            f.write("Ant Colony Optimization Solution:\n" if hasattr(self, "evaporation_rate") else "Simulated Annealing Solution:\n")
            f.write("=" * 40 + "\n")
            
            for order_solution in self.best_path:
                drones_used, warehouses_visited, order_id, commands = order_solution

                f.write(f"Order ID: {order_id}\n")
                f.write(f"  Drones Used: {', '.join(map(str, drones_used))}\n")
                f.write(f"  Warehouses Visited: {', '.join(map(str, warehouses_visited))}\n")
                f.write(f"  Commands:\n")
                for cmd in commands:
                    f.write(f"    - {cmd}\n")

            f.write("-" * 40 + "\n")
            f.write("Ant Colony Optimization Solution:\n" if hasattr(self, "evaporation_rate") else "Simulated Annealing Solution:\n")
            f.write("=" * 40 + "\n")
            f.write(f"Completed in {self.completed_turns} turns\n")
            f.write(f"Score: {self.score:.2f}\n")
            f.write("-" * 40 + "\n")

        print(f"✅ Solution saved to {filename}")