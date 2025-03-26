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

# drones_copy = copy.deepcopy(simulation.drones)
# warehouses_copy = copy.deepcopy(simulation.warehouses)
# orders_copy = copy.deepcopy(simulation.orders)
# products_copy = copy.deepcopy(simulation.products)  # Opcional, se produtos mudam no seu código
# # Rodando a simulação com os objetos copiados
# total_score = simulation_greedy(drones_copy, warehouses_copy, orders_copy, products_copy, simulation.deadline)
# print(total_score)


# Parâmetros do Simulated Annealing
initial_temperature = 100.0
cooling_rate = 0.995
min_temperature = 0.01
max_iterations = 10000

# Supondo que você já tenha as listas drones, warehouses, orders e products definidas, além do valor de max_turns
best_orders, best_score = simulated_annealing(simulation.drones, simulation.warehouses, simulation.orders, simulation.products, simulation.deadline, initial_temperature, cooling_rate, min_temperature, max_iterations)

print(f"Melhor score obtido: {best_score:.2f}")


# simulation_data = parse_file("busy_day.in")
# simulation = Simulation(simulation_data)
# # Testing Algorithm
# aco = AntColonyOpt(simulation.grid, simulation.drones, simulation.warehouses, simulation.orders, simulation.products, 10)
# solution = aco.run()
# aco.print_solution()
