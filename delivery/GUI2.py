import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog
from threading import Thread
from queue import Queue
import traceback
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
import math
from models.model import *
from parsers.parsing import * 
from algorithms.algorithm import *
from algorithms.genetics1 import *


class GeneticGUI:
    def __init__(self, root, algorithm_type="GA"):
        self.root = root
        self.root.title("Drone Delivery Simulation")
        self.root.geometry("1200x800")

        # Simulation data
        self.simulation = None
        self.simulation_data = None
        self.algorithm = None  # will store a GeneticAlgorithm instance
        self.running = False
        self.message_queue = Queue()
        self.algorithm_type = algorithm_type

        # frames
        self.control_frame = ttk.LabelFrame(self.root, text="Controls", padding=10)
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        self.plot_frame = ttk.LabelFrame(self.root, text="Evolution Plot", padding=10)
        self.plot_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=5, pady=5)

        # build the UI
        self.create_control_widgets_ga()
        self.create_plot_widgets()

        # Start background message processing
        self.root.after(100, self.process_messages)

    def create_control_widgets_ga(self):
        ttk.Label(self.control_frame, text="Input File:").grid(row=0, column=0, sticky=tk.W)
        self.file_entry = ttk.Entry(self.control_frame, width=30)
        self.file_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(self.control_frame, text="Browse", command=self.browse_file).grid(row=0, column=2, padx=5)

        ttk.Button(self.control_frame, text="Load Simulation", command=self.load_simulation).grid(row=1, column=0, columnspan=3, pady=10)
        if(self.algorithm_type == "GA"):
            # GA Params
            ttk.Label(self.control_frame, text="Genetic Algorithm Parameters", font=('Arial', 10, 'bold')).grid(row=2, column=0, columnspan=3, pady=(10, 5))

            param_fields = [
                ("Population Size:", "20", "pop_entry"),
                ("Generations:", "50", "gen_entry"),
                ("Crossover Rate:", "0.7", "cross_entry"),
                ("Mutation Rate:", "0.1", "mut_entry"),
            ]
        elif(self.algorithm_type == "ACO"):
            # Algorithm parameters
            ttk.Label(self.control_frame, text="Algorithm Parameters", font=('Arial', 10, 'bold')).grid(row=2, column=0, columnspan=3, pady=(10,5))
            
            param_fields = [
                ("Number of Ants:", "10", "ants_entry"),
                ("Iterations:", "10", "iterations_entry"),
                ("Alpha:", "1.0", "alpha_entry"),
                ("Beta:", "2.0", "beta_entry"),
                ("Evaporation:", "0.5", "evaporation_entry")
            ]
        elif(self.algorithm_type == "SA"):
            # Simulated Annealing parameters
            ttk.Label(self.control_frame, text="Simulated Annealing Parameters", font=('Arial', 10, 'bold')).grid(row=2, column=0, columnspan=3, pady=(10,5))
            
            # Lista de parâmetros para SA: (rótulo, valor padrão, nome do atributo)
            param_fields = [
                ("Initial Temperature:", "100.0", "initial_temp_entry"),
                ("Cooling Rate:", "0.95", "cooling_rate_entry"),
                ("Minimum Temperature:", "0.1", "min_temp_entry"),
                ("Max Iterations:", "1000", "max_iterations_entry")
            ]

        for i, (label, default, attr) in enumerate(param_fields, start=3):
            ttk.Label(self.control_frame, text=label).grid(row=i, column=0, sticky=tk.W)
            entry = ttk.Entry(self.control_frame, width=10)
            entry.grid(row=i, column=1, padx=5, pady=2)
            entry.insert(0, default)
            setattr(self, attr, entry)

        self.run_button = ttk.Button(self.control_frame, text="Run Simulation", command=self.run_simulation)
        self.run_button.grid(row=7, column=0, columnspan=2, pady=10)

        self.stop_button = ttk.Button(self.control_frame, text="Stop", command=self.stop_simulation, state=tk.DISABLED)
        self.stop_button.grid(row=7, column=2, pady=10)

        self.results_text = tk.Text(self.control_frame, height=10, width=40)
        self.results_text.grid(row=8, column=0, columnspan=3, pady=10)

        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_var.set("Ready")

    def create_plot_widgets(self):
        """Create a matplotlib figure for plotting generation vs. best score."""
        self.fig = Figure(figsize=(6,5), dpi=100)
        self.ax = self.fig.add_subplot(111)
        if self.algorithm_type == "GA":
            self.ax.set_title("GA Best Score Evolution")
            self.ax.set_xlabel("Generation")
            self.ax.set_ylabel("Best score")
        elif self.algorithm_type == "ACO":
            self.ax.set_title("ACO Best Score Evolution")
            self.ax.set_xlabel("Iteration")
            self.ax.set_ylabel("Best score")
        elif self.algorithm_type == "SA":
            self.ax.set_title("SA Best Score Evolution")
            self.ax.set_xlabel("Iteration")
            self.ax.set_ylabel("Best score")

        self.gens = []
        self.best_scores = []
        self.line, = self.ax.plot(self.gens, self.best_scores, marker='o')

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def browse_file(self):
        filename = filedialog.askopenfilename(
            initialdir="inputs",
            filetypes=[("Input files", "*.in"), ("All files", "*.*")]
        )
        if filename:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, filename)

    def load_simulation(self):
        filename = self.file_entry.get()
        if not filename:
            messagebox.showerror("Error", "Please select an input file")
            return
        try:
            short_name = filename.split('/')[-1]
            self.simulation_data = parse_file(short_name)
            self.simulation = Simulation(self.simulation_data)

            self.results_text.delete("1.0", tk.END)
            self.results_text.insert(tk.END, f"Loaded simulation: {filename}\n")
            self.results_text.insert(tk.END, f"Grid: {self.simulation.grid.rows}x{self.simulation.grid.cols}\n")
            self.results_text.insert(tk.END, f"Drones: {len(self.simulation.drones)}\n")
            self.results_text.insert(tk.END, f"Warehouses: {len(self.simulation.warehouses)}\n")
            self.results_text.insert(tk.END, f"Orders: {len(self.simulation.orders)}\n")
            self.results_text.insert(tk.END, f"Products: {len(self.simulation.products)}\n")
            self.results_text.insert(tk.END, f"Deadline: {self.simulation.deadline} turns\n")

            self.status_var.set(f"Loaded simulation {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load simulation: {str(e)}")

    def run_simulation(self):
        if not self.simulation:
            messagebox.showerror("Error", "Please load a simulation first!")
            return
        if self.running:
            messagebox.showwarning("Warning", "GA is already running!")
            return

        self.running = True
        self.run_button['state'] = tk.DISABLED
        self.stop_button['state'] = tk.NORMAL
        self.results_text.delete("1.0", tk.END)

        # Clear old data from the chart
        self.gens.clear()
        self.best_scores.clear()
        self.line.set_xdata(self.gens)
        self.line.set_ydata(self.best_scores)
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw_idle()

        Thread(target=self.run_simulation_threaded, daemon=True).start()

    def run_simulation_threaded(self):
        try:
            if(self.algorithm_type == "GA"):
                pop_size = int(self.pop_entry.get())
                gens = int(self.gen_entry.get())
                cross = float(self.cross_entry.get())
                mut = float(self.mut_entry.get())

                self.status_var.set("Running GA...")

                # Build the GA
                self.algorithm = GeneticAlgorithm(
                    simulation=self.simulation,
                    population_size=pop_size,
                    num_generations=gens,
                    crossover_rate=cross,
                    mutation_rate=mut
                )
                def progress(gen, best_score):
                    if self.running:
                        self.message_queue.put(f"ITER_UPDATE:{gen}:{best_score}")
                best_chrom, best_score = self.algorithm.run(self.simulation, progress_callback=progress)

                if self.running:
                    self.message_queue.put(f"DONE:{best_score}")

            elif(self.algorithm_type == "ACO"):
                # Get algorithm parameters
                num_ants = int(self.ants_entry.get())
                num_iterations = int(self.iterations_entry.get())
                alpha = float(self.alpha_entry.get())
                beta = float(self.beta_entry.get())
                evaporation_rate = float(self.evaporation_entry.get())
                
                # Initialize algorithm
                self.algorithm = AntColonyOpt(
                    grid=self.simulation.grid,
                    drones=self.simulation.drones,
                    warehouses=self.simulation.warehouses,
                    orders=self.simulation.orders,
                    products=self.simulation.products,
                    num_ants=num_ants,
                    num_turns=self.simulation.deadline,
                    num_iterations=num_iterations,
                    alpha=alpha,
                    beta=beta,
                    evaporation_rate=evaporation_rate
                )
                def progress(gen, best_score):
                    if self.running:
                        self.message_queue.put(f"ITER_UPDATE:{gen}:{best_score}")
                best_path,best_score = self.algorithm.run( progress_callback=progress)

                if self.running:
                    self.message_queue.put(f"DONE:{best_score}")

            elif(self.algorithm_type == "SA"):
                # Get algorithm parameters
                initial_temp = float(self.initial_temp_entry.get())
                cooling_rate = float(self.cooling_rate_entry.get())
                min_temp = float(self.min_temp_entry.get())
                max_iterations = int(self.max_iterations_entry.get())
                
                # Initialize algorithm
                self.algorithm = SimulatedAnnealingOptimizer(
                    self.simulation.drones,
                    self.simulation.warehouses,
                    self.simulation.orders,
                    self.simulation.products,
                    self.simulation.deadline
                )
                # Run algorithm
                self.status_var.set("STATUS:Running simulation...")

                def progress(gen, best_score):
                    if self.running:
                        self.message_queue.put(f"ITER_UPDATE:{gen}:{best_score}")
                best_path, best_score = self.algorithm.run(
                    initial_temperature=initial_temp,
                    cooling_rate=cooling_rate,
                    min_temperature=min_temp,
                    max_iterations=max_iterations,
                    progress_callback=progress
                )

                if self.running:
                    self.message_queue.put(f"DONE:{best_score}")

        except Exception as e:
            self.message_queue.put(f"ERROR:{str(e)}")
            traceback.print_exc() 

    def stop_simulation(self):
        if self.running:
            self.running = False
            self.run_button['state'] = tk.NORMAL
            self.stop_button['state'] = tk.DISABLED
            self.status_var.set("Stopped by user")

    def process_messages(self):
        while not self.message_queue.empty():
            msg = self.message_queue.get_nowait()
            if msg.startswith("ITER_UPDATE:"):
                # partial update
                parts = msg.split(":")
                if len(parts) == 3:
                    gen = int(parts[1])
                    best_score = float(parts[2])
                    self.update_plot(gen, best_score)
                    self.results_text.insert(tk.END, f"Iteration {gen}, Best: {best_score}\n")
                    self.results_text.see(tk.END)
            elif msg.startswith("DONE:"):
                # GA done
                parts = msg.split(":")
                try:
                    final_score = float(parts[1]) if len(parts) > 1 and parts[1] != '[]' else 0.0
                except ValueError:
                    print(f"Invalid score value: {parts}")
                    final_score = 0.0  # Or another default value, depending on your use case
                self.results_text.insert(tk.END, "Algorithm Completed!\n")
                self.results_text.insert(tk.END, f"Final Score: {final_score}\n")
                self.results_text.see(tk.END)
                self.running = False
                self.run_button['state'] = tk.NORMAL
                self.stop_button['state'] = tk.DISABLED
                self.status_var.set("Algorithm completed")
            elif msg.startswith("ERROR:"):
                messagebox.showerror("Error", msg[6:])
                self.running = False
                self.run_button['state'] = tk.NORMAL
                self.stop_button['state'] = tk.DISABLED
            # else: ignore
        self.root.after(100, self.process_messages)

    def update_plot(self, gen, best):
        self.gens.append(gen)
        self.best_scores.append(best)

        self.line.set_xdata(self.gens)
        self.line.set_ydata(self.best_scores)
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw_idle()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    print("Choose an algorithm to use:")
    print("  - ACO (Ant Colony Optimization)")
    print("  - SA  (Simulated Annealing)")
    print("  - GA (Genetic Algorithm)")
    
    algo = input("Enter algorithm (ACO/SA/GA): ").strip().upper()

    if algo not in ["ACO", "SA", "GA"]:
        print("❌ Invalid choice. Defaulting to ACO.")
        algo = "ACO"

    root = tk.Tk()
    app = GeneticGUI(root, algorithm_type=algo)
    root.mainloop()