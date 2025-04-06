from models.model import *
from parsers.parsing import * 
from algorithms.genetics1 import *
from utils.utils import *
import copy

def main():
    data = parse_file("mother_of_all_warehouses.in")   
    sim = Simulation(data)

    ga = GeneticAlgorithm(sim, population_size=2, num_generations=50,crossover_rate=0.7 ,mutation_rate=0.3)

    best_chrom, best_score = ga.run(sim)
    print("\n=== GA run complete ===")
    print("Best Score:", best_score)
    ga.print_solution()

if __name__ == "__main__":
    main()

