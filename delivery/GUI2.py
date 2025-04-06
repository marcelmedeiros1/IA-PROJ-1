import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog
from threading import Thread
from queue import Queue
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
    def __init__(self, root):
        self.root = root
        self.root.title("Genetic Algorithm Visualization")
        self.root.geometry("1200x800")

        # Simulation data
        self.simulation = None
        self.simulation_data = None
        self.ga = None  # will store a GeneticAlgorithm instance
        self.running = False
        self.message_queue = Queue()

        # frames
        self.control_frame = ttk.LabelFrame(self.root, text="Controls", padding=10)
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        self.plot_frame = ttk.LabelFrame(self.root, text="GA Evolution Plot", padding=10)
        self.plot_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=5, pady=5)

        # build the UI
        self.create_control_widgets()
        self.create_plot_widgets()

        # Start background message processing
        self.root.after(100, self.process_messages)

    def create_control_widgets(self):
        """Create the left control panel widgets: file selection, GA param fields, run/stop, etc."""
        # Input file
        ttk.Label(self.control_frame, text="Input File:").grid(row=0, column=0, sticky=tk.W)
        self.file_entry = ttk.Entry(self.control_frame, width=30)
        self.file_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(self.control_frame, text="Browse", command=self.browse_file).grid(row=0, column=2, padx=5)

        ttk.Button(self.control_frame, text="Load Simulation", command=self.load_simulation).grid(row=1, column=0, columnspan=3, pady=10)

        # GA parameters
        ttk.Label(self.control_frame, text="Genetic Algorithm Params", font=('Arial', 10, 'bold')).grid(row=2, column=0, columnspan=3, pady=(10,5))

        ttk.Label(self.control_frame, text="Population:").grid(row=3, column=0, sticky=tk.W)
        self.pop_entry = ttk.Entry(self.control_frame, width=10)
        self.pop_entry.grid(row=3, column=1, padx=5, pady=2)
        self.pop_entry.insert(0, "20")

        ttk.Label(self.control_frame, text="Generations:").grid(row=4, column=0, sticky=tk.W)
        self.gen_entry = ttk.Entry(self.control_frame, width=10)
        self.gen_entry.grid(row=4, column=1, padx=5, pady=2)
        self.gen_entry.insert(0, "50")

        ttk.Label(self.control_frame, text="Crossover:").grid(row=5, column=0, sticky=tk.W)
        self.cross_entry = ttk.Entry(self.control_frame, width=10)
        self.cross_entry.grid(row=5, column=1, padx=5, pady=2)
        self.cross_entry.insert(0, "0.7")

        ttk.Label(self.control_frame, text="Mutation:").grid(row=6, column=0, sticky=tk.W)
        self.mut_entry = ttk.Entry(self.control_frame, width=10)
        self.mut_entry.grid(row=6, column=1, padx=5, pady=2)
        self.mut_entry.insert(0, "0.1")

        self.run_button = ttk.Button(self.control_frame, text="Run GA", command=self.run_ga)
        self.run_button.grid(row=7, column=0, columnspan=2, pady=10)
        self.stop_button = ttk.Button(self.control_frame, text="Stop", command=self.stop_ga, state=tk.DISABLED)
        self.stop_button.grid(row=7, column=2, pady=10)

        # results text
        self.results_text = tk.Text(self.control_frame, height=10, width=40)
        self.results_text.grid(row=8, column=0, columnspan=3, pady=10)

        # status bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self.control_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        self.status_bar.grid(row=9, column=0, columnspan=3, sticky=tk.EW)
        self.status_var.set("Ready")

    def create_plot_widgets(self):
        """Create a matplotlib figure for plotting generation vs. best fitness."""
        self.fig = Figure(figsize=(6,5), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("GA Best Score Evolution")
        self.ax.set_xlabel("Generation")
        self.ax.set_ylabel("Best Fitness")

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

    def run_ga(self):
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

        Thread(target=self.run_ga_threaded, daemon=True).start()

    def run_ga_threaded(self):
        try:
            pop_size = int(self.pop_entry.get())
            gens = int(self.gen_entry.get())
            cross = float(self.cross_entry.get())
            mut = float(self.mut_entry.get())

            self.status_var.set("Running GA...")

            # Build the GA
            self.ga = GeneticAlgorithm(
                simulation=self.simulation,
                population_size=pop_size,
                num_generations=gens,
                crossover_rate=cross,
                mutation_rate=mut
            )

            # define a local callback
            def ga_progress(gen, best_fit):
                if self.running:
                    self.message_queue.put(f"GEN_UPDATE:{gen}:{best_fit}")

            # Modify your GA's run() to accept progress_callback=..., e.g.:
            best_chrom, best_score = self.ga.run(self.simulation, progress_callback=ga_progress)

            if self.running:
                self.message_queue.put(f"DONE:{best_score}")
        except Exception as e:
            self.message_queue.put(f"ERROR:{str(e)}")

    def stop_ga(self):
        if self.running:
            self.running = False
            self.run_button['state'] = tk.NORMAL
            self.stop_button['state'] = tk.DISABLED
            self.status_var.set("Stopped by user")

    def process_messages(self):
        while not self.message_queue.empty():
            msg = self.message_queue.get_nowait()
            if msg.startswith("GEN_UPDATE:"):
                # partial update
                parts = msg.split(":")
                if len(parts) == 3:
                    gen = int(parts[1])
                    best_fit = float(parts[2])
                    self.update_plot(gen, best_fit)
                    self.results_text.insert(tk.END, f"Generation {gen}, Best: {best_fit}\n")
                    self.results_text.see(tk.END)
            elif msg.startswith("DONE:"):
                # GA done
                parts = msg.split(":")
                final_score = float(parts[1]) if len(parts) > 1 else 0.0
                self.results_text.insert(tk.END, "GA Completed!\n")
                self.results_text.insert(tk.END, f"Final Score: {final_score}\n")
                self.results_text.see(tk.END)
                self.running = False
                self.run_button['state'] = tk.NORMAL
                self.stop_button['state'] = tk.DISABLED
                self.status_var.set("GA completed")
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
    root = tk.Tk()
    app = GeneticGUI(root)
    app.run()