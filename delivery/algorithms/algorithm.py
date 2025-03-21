import random
import math
import copy

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