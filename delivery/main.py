from models.model import *
from parsers.parsing import * 
from algorithms.algorithm import *

# Carregar os dados do problema
#grid, drones, warehouses, orders, products = load_input("test_inputs/example.in")

# Escolher um algoritmo de otimização
#solution = greedy_algorithm(grid, drones, warehouses, orders, products)

# Salvar a saída no formato esperado

#save_output("results/solution.txt", solution)

# Testing Parsing
# python3 main.py > parsing_test.txt (command to execute)

simulation_data = parse_file("busy_day.in")
simulation = Simulation(simulation_data)
#simulation.testing_parse()

# Testing Algorithm
aco = AntColonyOpt(simulation.grid, simulation.drones, simulation.warehouses, simulation.orders, simulation.products, 10)
solution = aco.run()
aco.print_solution()