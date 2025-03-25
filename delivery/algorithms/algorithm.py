import random
import math
import copy

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
        self.in_turns = 0
        self.out_turns = 0
        self.score = 0
        self.best_path_distance = math.inf
    
    def evaluate_turns(self):
        self.aux_turns -= 1
        if(self.aux_turns < 0):
            self.out_turns += 1
        else:
            self.in_turns += 1
    
    def construct_score(self):
        score = ((self.in_turns - self.out_turns) / self.in_turns) * 100
        self.aux_turns = self.num_turns
        self.in_turns = 0
        self.out_turns = 0
        return score

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
        self.score = self.best_path_distance
        return self.best_path

    def construct_solution(self):
        solution = []

        new_warehouses = copy.deepcopy(self.warehouses)
        new_orders = copy.deepcopy(self.orders)
        new_drones = copy.deepcopy(self.drones)

        for order in new_orders:
            order_solution = []  # Solution specific to this order
            warehouses_visited = []  # List of warehouses visited
            commands = []  # Sequence of commands

            for product_id, quantity in list(order.items.items()):  # Iterate over the products required for the order
                remaining_quantity = quantity  # Quantity left to be delivered

                while remaining_quantity > 0:
                    # Filter warehouses that have the required product in stock
                    valid_warehouses_with_stock = [
                        w for w in new_warehouses if w.stock.get(product_id, 0) > 0
                    ]

                    if not valid_warehouses_with_stock:
                        for warehouse in new_warehouses:
                            for product in warehouse.stock:
                                if(product == product_id):
                                    print(f"product_id: {product_id} - warehouse_id: {warehouse.warehouse_id} - stock: {warehouse.stock[product]}")
                        
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
                    while(count > 0):
                        # Choose the best drone based on the distance to the warehouse
                        best_drone = min(aux, key=lambda d: d.location.euclidean_distance(best_warehouse.location))
                        if (best_drone.payload + self.products[product_id].weight * load_quantity) > best_drone.max_payload:
                            # If the drone cannot carry the load, try another drone
                            aux.remove(best_drone)
                        else:
                            break
                        count -= 1

                    # Move the drone to the warehouse and then to the order location
                    travel_time = best_drone.move_to(best_warehouse.location) + best_drone.move_to(order.location)

                    # Load the product onto the drone
                    if not best_drone.load(best_warehouse, self.products[product_id], load_quantity):
                        raise Exception(f"Erro ao carregar produto {product_id} no drone {best_drone.drone_id}")

                    commands.append(f"Load {product_id} from Warehouse {best_warehouse.warehouse_id}")
                    self.evaluate_turns()

                    # Deliver the product to the order location
                    if not best_drone.deliver(order, self.products[product_id], load_quantity):
                        raise Exception(f"Erro ao entregar produto {product_id} do pedido {order.order_id}")

                    commands.append(f"Deliver {product_id} to Order {order.order_id}")
                    self.evaluate_turns()


                    # Update the remaining quantity and warehouse stock
                    remaining_quantity -= load_quantity

                    # Add the warehouse to the list of visited warehouses
                    if best_warehouse.warehouse_id not in warehouses_visited:
                        warehouses_visited.append(best_warehouse.warehouse_id)

            # Add the solution for this order
            
            order_solution = [best_drone.drone_id, warehouses_visited, order.order_id, commands]
            solution.append(order_solution)
            score = self.construct_score()
        return solution, score

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
        print("Ant Colony Optimization Solution:")
        print("=" * 40)
        print(f"Completed in {self.in_turns + self.out_turns} turns")
        print(f"Score: {self.score:.2f}%")
        print("-" * 40)