from parsers.parsing import * 
from algorithms.genetics1 import *
from algorithms.algorithm import *
import copy

def main():
    data = parse_file("busy_day.in")   
    sim = Simulation(data)
    # Supondo que você já tenha as listas drones, warehouses, orders e products definidas, além do valor de max_turns
    # optimizer = SimulatedAnnealingOptimizer(simulation.drones, simulation.warehouses, simulation.orders, simulation.products, simulation.deadline)
    # # best_plan, best_score = optimizer.run(
    # #     initial_temperature=100,
    # #     cooling_rate=0.98,
    # #     min_temperature=1.5,
    # #     max_iterations=1000
    # )
    # simulation_data = parse_file("busy_day.in")
    # simulation = Simulation(simulation_data)
    # # Testing Algorithm
    # aco = AntColonyOpt(simulation.grid, simulation.drones, simulation.warehouses, simulation.orders, simulation.products, 10)
    # solution = aco.run()
    # aco.print_solution()
    # simulation_data = parse_file("redundancy.in")
    # simulation = Simulation(simulation_data)
    #simulation.testing_parse()

    # # Testing Algorithm
    # aco = AntColonyOpt(simulation.grid, simulation.drones, simulation.warehouses, simulation.orders, simulation.products, 10, simulation.deadline)
    # solution = aco.run()
    # aco.print_solution()

    ga = GeneticAlgorithm(sim, population_size=2, num_generations=50,crossover_rate=0.7 ,mutation_rate=0.3)

    best_chrom, best_score = ga.run(sim)
    print("\n=== GA run complete ===")
    print("Best Score:", best_score)
    ga.print_solution()

if __name__ == "__main__":
    main()

