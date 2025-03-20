from models.model import *
from parsers.parsing import * 
from algorithms.algorithm import *
from utils.utils import *

# Carregar os dados do problema
#grid, drones, warehouses, orders, products = load_input("test_inputs/example.in")

# Escolher um algoritmo de otimização
#solution = greedy_algorithm(grid, drones, warehouses, orders, products)

# Salvar a saída no formato esperado

#save_output("results/solution.txt", solution)

# Testing Parsing
# python3 main.py > parsing_test.txt (command to execute)

simulation_data = parse_file("tiny.in")
simulation = Simulation(simulation_data)
simulation.testing_parse()

sequences= generate__all_orders_sequences(simulation.orders)

# for seq in sequences:
#     total_score = simulate(seq, simulation.drones, simulation.warehouses, simulation.orders, simulation.products, simulation.deadline)
#     print(total_score)

total_score = simulate(sequences[0], simulation.drones, simulation.warehouses, simulation.orders, simulation.products, simulation.deadline)
print(total_score)