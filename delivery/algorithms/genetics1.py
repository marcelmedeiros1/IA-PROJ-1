import copy
import math
import random
from typing import List, NamedTuple, Union
from parsers.parsing import *
from models.model import *

class PayloadItem:
    def __init__(self,warehouse_id:int , product_id: int, quantity: int):
        self.warehouse_id = warehouse_id
        self.product_id = product_id
        self.quantity = quantity

class Payload:
    def __init__(self,order_id:int):
        self.order_id = order_id
        self.items = []
        self.total_weight = 0
    def add_item(self, warehouse_id, product, quantity):
        self.items.append(PayloadItem(warehouse_id, product.product_id, quantity))
        self.total_weight += product.weight * quantity
    def __str__(self):
        lines = [f"Payload for Order {self.order_id}", f"Total Weight: {self.total_weight}"]
        for it in self.items:
            lines.append(f"   Warehouse {it.warehouse_id} -> Product {it.product_id} x {it.quantity}")
        return "\n".join(lines)
   

class CommandBlock(NamedTuple):
    warehouse_id: int
    product_id: int
    quantity: int
    order_id: int

class WaitBlock(NamedTuple):
    time: int

Block = Union[CommandBlock, WaitBlock]

def build_heavy_lifting_payloads(simulation: Simulation):
    payloads = []

    orders_sorted = sorted(
        simulation.orders,
        key=lambda o: sum(o.items.values())  
    )

    warehouse_stock_copy = []
    for w in simulation.warehouses:
        warehouse_stock_copy.append(dict(w.stock))  

    order_needs = {}
    for o in orders_sorted:
        order_needs[o.order_id] = dict(o.items)

    max_drone_load = simulation.drones[0].max_payload  

    for order in orders_sorted:
        o_id = order.order_id
        current_payload = None
        remaining_capacity = 0
        droneLocation = order.location  

        for p_id, needed_qty in order_needs[o_id].items():
            if needed_qty <= 0:
                continue

            product_obj = simulation.products[p_id]
            weight = product_obj.weight

            while needed_qty > 0:
                if (remaining_capacity < weight):
                    if current_payload and current_payload.items:
                        payloads.append(current_payload)
                    current_payload = Payload(o_id)
                    remaining_capacity = max_drone_load
                    droneLocation = order.location 
                candidates = []
                for w_idx, wh in enumerate(simulation.warehouses):
                    avail = warehouse_stock_copy[w_idx].get(p_id, 0)
                    if avail > 0:
                        dist = simulation.drones[0].location.euclidean_distance(wh.location)

                        candidates.append((dist, w_idx))
                if not candidates:
                    break


                dist, best_w_idx = min(candidates, key=lambda x: x[0])
                wh_avail = warehouse_stock_copy[best_w_idx][p_id]

                can_load_by_capacity = remaining_capacity // weight
                load_qty = min(needed_qty, wh_avail, can_load_by_capacity)
                if load_qty <= 0:
                    break

                warehouse_stock_copy[best_w_idx][p_id] = wh_avail - load_qty
                needed_qty -= load_qty
                remaining_capacity -= load_qty * weight

                w_obj = simulation.warehouses[best_w_idx]
                current_payload.add_item(best_w_idx, product_obj, load_qty)
                droneLocation = w_obj.location

        if current_payload and current_payload.items:
            payloads.append(current_payload)

    return payloads

def build_small_orders_payloads(simulation):
    payloads = []
    
    warehouse_stocks = [dict(wh.stock) for wh in simulation.warehouses]
    
    orders_sorted = sorted(
        simulation.orders,
        key=lambda o: sum(o.items.values())
    )

    chunk_size = 3 

    for order in orders_sorted:
        for (p_id, needed_qty) in order.items.items():
            if needed_qty <= 0:
                continue
            while needed_qty > 0:
                best_wh_idx = None
                for w_idx, wh in enumerate(simulation.warehouses):
                    avail = warehouse_stocks[w_idx].get(p_id, 0)
                    if avail > 0:
                        best_wh_idx = w_idx
                        break
                if best_wh_idx is None:
                    break

                wh_avail = warehouse_stocks[best_wh_idx][p_id]
                load_qty = min(wh_avail, needed_qty, chunk_size)

                if load_qty <= 0:
                    break

                warehouse_stocks[best_wh_idx][p_id] = wh_avail - load_qty
                needed_qty -= load_qty

                payload = Payload(order.order_id)
                product_obj = simulation.products[p_id]
                payload.add_item(best_wh_idx, product_obj, load_qty)
                payloads.append(payload)

    return payloads

def build_distance_priority_payloads(simulation):
    payloads = []
   
    warehouse_stocks = [dict(wh.stock) for wh in simulation.warehouses]
    
    orders_sorted = simulation.orders

    chunk_size = 5

    for order in orders_sorted:
        for (p_id, needed_qty) in order.items.items():
            if needed_qty <= 0:
                continue

            product_obj = simulation.products[p_id]

            while needed_qty > 0:
                best_w_idx = None
                best_dist = float('inf')
                for w_idx, wh in enumerate(simulation.warehouses):
                    avail = warehouse_stocks[w_idx].get(p_id, 0)
                    if avail > 0:
                        dist_order = wh.location.euclidean_distance(order.location)
                        if dist_order < best_dist:
                            best_dist = dist_order
                            best_w_idx = w_idx
                if best_w_idx is None:
                    break

                wh_avail = warehouse_stocks[best_w_idx][p_id]
                load_qty = min(wh_avail, needed_qty, chunk_size)
                if load_qty <= 0:
                    break

                warehouse_stocks[best_w_idx][p_id] = wh_avail - load_qty
                needed_qty -= load_qty

                payload = Payload(order.order_id)
                payload.add_item(best_w_idx, product_obj, load_qty)
                payloads.append(payload)

    return payloads



def payloads_to_command_blocks(payloads):

    command_blocks = []
    for payload in payloads:
        for item in payload.items:
            cmd_block = CommandBlock(
                warehouse_id=item.warehouse_id,
                product_id=item.product_id,
                quantity=item.quantity,
                order_id=payload.order_id
            )
            command_blocks.append(cmd_block)
    return command_blocks

def build_greedy_chromosome(simulation, strategy="heavy"):

    if strategy == "heavy":
        payloads = build_heavy_lifting_payloads(simulation)
    elif strategy == "small_first":
        payloads = build_small_orders_payloads(simulation)
    elif strategy == "distance_first":
        payloads = build_distance_priority_payloads(simulation)
  
    all_cmd_blocks = payloads_to_command_blocks(payloads)

    num_drones = len(simulation.drones)
    chromosome = [[] for _ in range(num_drones)]
    for i, blk in enumerate(all_cmd_blocks):
        d_idx = i % num_drones
        chromosome[d_idx].append(blk)
    return chromosome



class GeneticAlgorithm:
    def __init__(self, simulation, population_size=5, num_generations=1, crossover_rate=0.7, mutation_rate=0.1):
        self.grid = simulation.grid
        self.drones = simulation.drones
        self.warehouses = simulation.warehouses
        self.orders = simulation.orders
        self.products = simulation.products
        self.deadline = simulation.deadline
        self.population_size = population_size
        self.num_generations = num_generations
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate

        self.population = []
        self.best_chromosome = None
        self.best_fitness = float('-inf')
        self.product_ids = [p.product_id for p in self.products]
        pass

    @staticmethod
    def create_blocks(simulation):
        blocks = []
        max_load = simulation.drones[0].max_payload
        products_map = {product.product_id: product for product in simulation.products}
        for warehouse in simulation.warehouses:
            for product_id, stock in warehouse.stock.items():
                if stock <= 0:
                    continue
                product_weight = products_map[product_id].weight
                max_quantity = max_load // product_weight
                for order in simulation.orders:
                    if product_id in order.items:
                        actual_quantity = min(order.items[product_id], stock)
                        blocks_needed = actual_quantity // max_quantity
                        remaining_quantity = actual_quantity % max_quantity
                        for _ in range(blocks_needed):
                            blocks.append(CommandBlock(warehouse.warehouse_id, product_id, max_quantity, order.order_id))
                        if remaining_quantity > 0:
                            blocks.append(CommandBlock(warehouse.warehouse_id, product_id, remaining_quantity, order.order_id))
        return blocks
    
    @staticmethod
    def create_random_chromosome(all_blocks, num_drones):
        chromosome = [[] for _ in range(num_drones)]
        shuffle_blocks = copy.deepcopy(all_blocks)
        random.shuffle(shuffle_blocks)
        for block in shuffle_blocks:
            drone = random.randint(0, num_drones - 1)
            chromosome[drone].append(block)
        return chromosome
    
    def crossover(self, chromosome_parent1, chromosome_parent2):
        chromosome_child1 = []
        chromosome_child2 = []

        for d in range(len(self.drones)):
            if random.random() < self.crossover_rate:
                if len(chromosome_parent1[d]) > 1 and len(chromosome_parent2[d]) > 1:
                    cut = random.randint(
                        1, 
                        min(len(chromosome_parent1[d]), len(chromosome_parent2[d])) - 1
                    )
                    child1_drone = chromosome_parent1[d][:cut] + chromosome_parent2[d][cut:]
                    child2_drone = chromosome_parent2[d][:cut] + chromosome_parent1[d][cut:]
                    chromosome_child1.append(child1_drone)
                    chromosome_child2.append(child2_drone)
                else:
                    chromosome_child1.append(chromosome_parent1[d])
                    chromosome_child2.append(chromosome_parent2[d])
            else:
                chromosome_child1.append(chromosome_parent1[d])
                chromosome_child2.append(chromosome_parent2[d])
        return chromosome_child1, chromosome_child2
    
    def swap_orders_from_drones(self,chromosome):
        num_drones = len(chromosome)
        if num_drones < 2:
            return chromosome
        drone1 = random.randint(0, num_drones - 1)
        drone2 = random.randint(0, num_drones - 1)
        while drone1 == drone2:
            drone2 = random.randint(0, num_drones - 1)
        block1 = random.choice(chromosome[drone1])
        block2 = random.choice(chromosome[drone2])
        chromosome[drone1].remove(block1)
        chromosome[drone2].remove(block2)
        chromosome[drone1].append(block2)
        chromosome[drone2].append(block1)
        return chromosome
    
    def reorder_blocks(self,chromosome):
        drone = random.randint(0, len(chromosome) - 1)
        if len(chromosome[drone]) < 2:
            return chromosome
        block1 = random.choice(chromosome[drone])
        block2 = random.choice(chromosome[drone])
        while block1 == block2:
            block2 = random.choice(chromosome[drone])
        index1 = chromosome[drone].index(block1)
        index2 = chromosome[drone].index(block2)
        chromosome[drone][index1] = block2
        chromosome[drone][index2] = block1
        return chromosome
    
    def insert_wait(self,chromosome):
        drone = random.randint(0, len(chromosome) - 1)
        time = random.randint(1, self.deadline-1)
        chromosome[drone].append(WaitBlock(time))
        return chromosome
    
    def mutate(self, chromosome):
        if random.random() < self.mutation_rate:
            num_mutations = random.randint(1, 3)
            operations = [self.swap_orders_from_drones, self.reorder_blocks, self.insert_wait]
            for _ in range(num_mutations):
                operation = random.choice(operations)
                chromosome = operation(chromosome)
        return chromosome
    
    def local_search(self, chromosome, simulation):
        for d_idx in range(len(chromosome)):
                plan = chromosome[d_idx]
                length = len(plan)
                if length < 2:
                    continue

                old_cost = self.simulate_drone_plan(d_idx, plan, simulation)

                attempts = min(10, length - 1)
                for _ in range(attempts):
                    i = random.randint(0, length - 2) 
                    plan[i], plan[i+1] = plan[i+1], plan[i]
                    new_cost = self.simulate_drone_plan(d_idx, plan, simulation)

                    if new_cost < old_cost:
                        old_cost = new_cost
                    else:
                        plan[i], plan[i+1] = plan[i+1], plan[i]
        return chromosome

    def simulate_drone_plan(self, d_idx, blocks, simulation):
        sim_copy = copy.deepcopy(simulation)
        drone = sim_copy.drones[d_idx]
        t = 0
        for blk in blocks:
            if isinstance(blk, WaitBlock):
                t += blk.time
            elif isinstance(blk, CommandBlock):
                warehouse = sim_copy.warehouses[blk.warehouse_id]
                product = sim_copy.products[blk.product_id]
                order = sim_copy.orders[blk.order_id]

                dist_wh = drone.location.euclidean_distance(warehouse.location)
                t += dist_wh
                drone.move_to(warehouse.location)
                t += 1
                loaded = min(warehouse.stock[product.product_id], blk.quantity)
                warehouse.stock[product.product_id] -= loaded
                drone.inventory[product.product_id] = \
                    drone.inventory.get(product.product_id, 0) + loaded

                dist_o = drone.location.euclidean_distance(order.location)
                t += dist_o
                drone.move_to(order.location)
                t += 1
                have = drone.inventory.get(product.product_id, 0)
                delivered = min(have, loaded)
                drone.inventory[product.product_id] = have - delivered
        return t
    
    @staticmethod
    def fitness(chromosome, simulation):
        sim_copy = copy.deepcopy(simulation)
        drones = sim_copy.drones
        orders = sim_copy.orders
        products = sim_copy.products
        warehouses = sim_copy.warehouses
        grid = sim_copy.grid
        deadline = sim_copy.deadline

        warehouses_stock = {
            wh.warehouse_id: copy.deepcopy(wh.stock) for wh in warehouses
        }
        drone_time = [0] * len(drones)
        drone_complete_time = [-1] * len(orders)

        for drone_index, blocks in enumerate(chromosome):
            drone = drones[drone_index]
            for block in blocks:
                current_time = drone_time[drone_index]

                if isinstance(block, WaitBlock):
                    new_time = current_time + block.time
                    drone_time[drone_index] = new_time
                    continue

                if isinstance(block, CommandBlock):
                    warehouse = warehouses[block.warehouse_id]
                    product = products[block.product_id]
                    order = orders[block.order_id]

                    fly_to_warehouse = drone.location.euclidean_distance(warehouse.location)
                    drone_time[drone_index] += fly_to_warehouse
                    drone.move_to(warehouse.location)
                    current_time = drone_time[drone_index]

                    product_weight = product.weight
                    if warehouse.stock[block.product_id] < block.quantity:
                        product_quantity = warehouse.stock[block.product_id]
                    else:
                        product_quantity = block.quantity
                    can_carry = drone.max_payload // product_weight
                    product_quantity = min(product_quantity, can_carry)

                    if product_quantity <= 0:
                        continue

                    drone_time[drone_index] += 1
                    current_time = drone_time[drone_index]

                    load_ok = drone.load(warehouse, product, product_quantity)
                    if not load_ok:
                        continue
                    warehouse.stock[block.product_id] -= product_quantity

                    fly_to_order = drone.location.euclidean_distance(order.location)
                    drone_time[drone_index] += fly_to_order
                    drone.move_to(order.location)
                    current_time = drone_time[drone_index]

                    if product.product_id not in order.items or order.items[product.product_id] <= 0:
                        if product.product_id in drone.inventory:
                            qty_in_inv = drone.inventory[product.product_id]
                            drone.payload -= product.weight * qty_in_inv
                            drone.inventory[product.product_id] = 0
                        continue

                    drone_time[drone_index] += 1
                    current_time = drone_time[drone_index]

                    delivery_ok = drone.deliver(order, product, product_quantity)
                    if delivery_ok and order.completed and drone_complete_time[order.order_id] == -1:
                        drone_complete_time[order.order_id] = current_time

        T = deadline
        score = 0
        for o_id, complete_time in enumerate(drone_complete_time):
            if 0 <= complete_time <= T:
                portion = (T - complete_time) / T
                score += math.ceil(portion * 100)

        return score
      

    def print_solution(self):
        print("Genetic Algorithm Solution:")
        print("=" * 40)
        for d_idx, plan in enumerate(self.best_chromosome):
            print(f"Drone #{d_idx}:")
            warehouses_visited = []
            commands = []
            for block in plan:
                if isinstance(block, CommandBlock):
                    commands.append(f"LOAD from Warehouse {block.warehouse_id} product {block.product_id} x {block.quantity}, then DELIVER to Order {block.order_id}")
                    warehouses_visited.append(block.warehouse_id)
                else:  #
                    commands.append(f"WAIT for {block.time} turns")

            warehouses_str = ", ".join(map(str, set(warehouses_visited))) if warehouses_visited else "None"

            print(f"  Warehouses Visited: {warehouses_str}")
            print(f"  Commands:")
            for cmd in commands:
                print(f"    - {cmd}")

        print("-" * 40)
        print("Genetic Algorithm Solution:")
        print("=" * 40)
        print(f"Score: {self.best_fitness:.2f}")
        print("-" * 40)


    def run(self, simulation, progress_callback=None):
        all_blocks = GeneticAlgorithm.create_blocks(simulation)
        population = []
        chrom_heavy = build_greedy_chromosome(simulation, strategy="heavy")
        chrom_small = build_greedy_chromosome(simulation, strategy="small_first")
        chrom_dist = build_greedy_chromosome(simulation, strategy="distance_first")

        population.append(chrom_heavy)
        population.append(chrom_small)
        population.append(chrom_dist)
     
        for _ in range(self.population_size - 3):
            pop_chrom = self.create_random_chromosome(all_blocks, len(self.drones))
            population.append(pop_chrom)

        best_chromosome = None
        best_fitness = float('-inf')
        for gen in range(self.num_generations):
            result= [GeneticAlgorithm.fitness(chromosome, simulation) for chromosome in population]
            fitnesses = result
            gen_best = max(fitnesses)
            gen_min = min(fitnesses)
            gen_avg = sum(fitnesses) / len(fitnesses)

            if gen_best > best_fitness:
                best_fitness = gen_best
                best_chromosome = population[fitnesses.index(gen_best)]


            print(f"Generation {gen} | "
                f"Gen best = {gen_best}, Gen avg = {gen_avg:.2f}, "
                f"Gen worst = {gen_min}, Global best so far = {best_fitness}")
            if progress_callback is not None:
                progress_callback(gen, best_fitness)
            for chromosome, fitness in zip(population, fitnesses):
                if fitness > best_fitness:
                    best_fitness = fitness
                    best_chromosome = chromosome


            mating_population = []        
            for _ in range(self.population_size):
                i1, i2 = random.sample(range(self.population_size), k=2)
                if fitnesses[i1] > fitnesses[i2]:
                    mating_population.append(population[i1])
                else:
                    mating_population.append(population[i2])

            new_population = []
            for i in range(0, self.population_size, 2):
                chromosome_parent1 = mating_population[i]
                chromosome_parent2 = mating_population[(i+1) % self.population_size]
                chromosome_child1, chromosome_child2 = self.crossover(chromosome_parent1, chromosome_parent2)
                chromosome_child1 = self.mutate(chromosome_child1)
                chromosome_child2 = self.mutate(chromosome_child2)
                chromosome_child1 = self.local_search(chromosome_child1, simulation)
                chromosome_child2 = self.local_search(chromosome_child2, simulation)
                new_population.append(chromosome_child1)
                new_population.append(chromosome_child2)
            population = new_population

        self.best_chromosome = best_chromosome
        self.best_fitness = best_fitness
        return best_chromosome, best_fitness