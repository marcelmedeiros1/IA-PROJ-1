from models.model import *
from parsers.parsing import * 
from algorithms.algorithm import *
from utils.utils import *
import copy

# Carregar os dados do problema
#grid, drones, warehouses, orders, products = load_input("test_inputs/example.in")

# Escolher um algoritmo de otimização
#solution = greedy_algorithm(grid, drones, warehouses, orders, products)

# Salvar a saída no formato esperado

#save_output("results/solution.txt", solution)

# Testing Parsing
# python3 main.py > parsing_test.txt (command to execute)


# Testing Brute-Force
simulation_data = parse_file("tiny.in")
simulation_o = Simulation(simulation_data)
simulation = copy.deepcopy(simulation_o)
total_score = simulate_turns(simulation.drones, simulation.warehouses, simulation.orders, simulation.products, simulation.deadline)
print(total_score)


simulation_data = parse_file("busy_day.in")
simulation = Simulation(simulation_data)
# Testing Algorithm
aco = AntColonyOpt(simulation.grid, simulation.drones, simulation.warehouses, simulation.orders, simulation.products, 10)
solution = aco.run()
aco.print_solution()
