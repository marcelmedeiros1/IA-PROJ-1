import random
import math

class AntColonyOpt:
    def __init__(self, grid, drones, warehouses, orders, products,num_ants,num_iterations=100,alpha=1.0,beta=2.0,evaporation_rate=0.5,q=100):
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
    
    def select_path(self,warehouse,order):
        pheromone_value = self.pheromone[(warehouse.warehouse_id,order.order_id)] ** self.alpha
        heuristic_value = self.heuristic(warehouse,order) ** self.beta
        return pheromone_value * heuristic_value
    
    def run(self):
        for iteration in range(self.num_iterations):
            solutions = []
            for ant in range(self.num_ants):
                solution, cost = self.construct_solution()
                solutions.append((solution,cost))
                if cost < self.best_path_distance:
                    self.best_path = solution
                    self.best_path_distance = cost
            self.update_pheromone(solutions)
        return self.best_path
    
    def construct_solution(self):
        solution = []
        cost = 0

        for order in self.orders:
            # Filtrar apenas os armazéns que possuem os produtos necessários
            valid_warehouses = [
                w for w in self.warehouses if all(
                    w.stock.get(pid, 0) >= qty for pid, qty in order.items.items()
                )
            ]

            if not valid_warehouses:
                raise Exception(f"Nenhum armazém tem estoque suficiente para atender ao pedido {order.order_id}")

            # Escolher o melhor armazém com base na heurística
            best_warehouse = min(valid_warehouses, key=lambda w: self.select_path(w, order))

            # Escolher o melhor drone com base na distância ao armazém
            best_drone = min(self.drones, key=lambda d: d.location.distance_to(best_warehouse.location))

            print(f"Pedido {order.order_id}: Drone {best_drone.drone_id} -> Warehouse {best_warehouse.warehouse_id}")

            # Movimentação e custo
            travel_time = best_drone.move_to(best_warehouse.location) + best_drone.move_to(order.location)
            cost += travel_time

            for product_id, quantity in order.items.items():
                if not best_drone.load(best_warehouse, self.products[product_id], quantity):
                    raise Exception(f"Erro ao carregar produto {product_id} no drone {best_drone.drone_id}")

                if not best_drone.deliver(order, self.products[product_id], quantity):
                    raise Exception(f"Erro ao entregar produto {product_id} do pedido {order.order_id}")

            solution.append((best_drone.drone_id, best_warehouse.warehouse_id, order.order_id))

        return solution, cost

    
    def update_pheromone(self,solutions):
        for key in self.pheromone:
            self.pheromone[key] *= (1 - self.evaporation_rate)
        for solution, cost in solutions:
            pheromone_amount = self.q / cost
            for drone_id, warehouse_id, order_id in solution:
                self.pheromone[(warehouse_id,order_id)] += pheromone_amount