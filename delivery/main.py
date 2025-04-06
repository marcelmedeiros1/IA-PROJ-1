from parsers.parsing import * 
from algorithms.algorithm import *
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
simulation_data = parse_file("busy_day.in")
simulation = Simulation(simulation_data)

# Supondo que você já tenha as listas drones, warehouses, orders e products definidas, além do valor de max_turns
optimizer = SimulatedAnnealingOptimizer(simulation.drones, simulation.warehouses, simulation.orders, simulation.products, simulation.deadline)
best_plan, best_score = optimizer.run(
    initial_temperature=100,
    cooling_rate=0.98,
    min_temperature=1.5,
    max_iterations=1000
)
# simulation_data = parse_file("busy_day.in")
# simulation = Simulation(simulation_data)
# # Testing Algorithm
# aco = AntColonyOpt(simulation.grid, simulation.drones, simulation.warehouses, simulation.orders, simulation.products, 10)
# solution = aco.run()
# aco.print_solution()
simulation_data = parse_file("redundancy.in")
simulation = Simulation(simulation_data)
#simulation.testing_parse()

# # Testing Algorithm
# aco = AntColonyOpt(simulation.grid, simulation.drones, simulation.warehouses, simulation.orders, simulation.products, 10, simulation.deadline)
# solution = aco.run()
# aco.print_solution()