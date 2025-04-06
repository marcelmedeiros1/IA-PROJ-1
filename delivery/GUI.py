import tkinter as tk
from tkinter import ttk, messagebox
from threading import Thread
from queue import Queue
from models.model import *
from parsers.parsing import * 
from algorithms.algorithm import *
from algorithms.genetics1 import *

class DroneDeliveryGUI:
    def __init__(self, root, algorithm_type="ACO"):
        self.root = root
        self.root.title("Drone Delivery Simulation")
        self.root.geometry("1200x800")
        
        # Simulation data
        self.simulation = None
        self.simulation_data = None
        self.algorithm = algorithm_type
        self.running = False
        self.message_queue = Queue()
        
        # Create frames first
        self.control_frame = ttk.LabelFrame(self.root, text="Controls", padding=10)
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        self.visualization_frame = ttk.LabelFrame(self.root, text="Visualization", padding=10)
        self.visualization_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=5, pady=5)
        
        # Now create widgets
        if(self.algorithm == "ACO"):
            self.create_widgets_aco()
        elif(self.algorithm == "SA"):
            self.create_widgets_sa()
        elif(self.algorithm == "GEN"):
            self.create_widgets_gen()
        else:
            messagebox.showerror("Error", "Invalid algorithm selected")
            return
        
        # Start the message pump
        self.root.after(100, self.process_messages)

    def create_widgets_aco(self):
        """Create all GUI widgets"""
        # Input file selection
        ttk.Label(self.control_frame, text="Input File:").grid(row=0, column=0, sticky=tk.W)
        self.file_entry = ttk.Entry(self.control_frame, width=30)
        self.file_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(self.control_frame, text="Browse", command=self.browse_file).grid(row=0, column=2, padx=5)
        
        ttk.Button(self.control_frame, text="Load Simulation", command=self.load_simulation).grid(row=1, column=0, columnspan=3, pady=10)
        
        # Algorithm parameters
        ttk.Label(self.control_frame, text="Algorithm Parameters", font=('Arial', 10, 'bold')).grid(row=2, column=0, columnspan=3, pady=(10,5))
        
        params = [
            ("Number of Ants:", "10", "ants_entry"),
            ("Iterations:", "10", "iterations_entry"),
            ("Alpha:", "1.0", "alpha_entry"),
            ("Beta:", "2.0", "beta_entry"),
            ("Evaporation:", "0.5", "evaporation_entry")
        ]
        
        for i, (label, default, attr) in enumerate(params, start=3):
            ttk.Label(self.control_frame, text=label).grid(row=i, column=0, sticky=tk.W)
            entry = ttk.Entry(self.control_frame, width=10)
            entry.grid(row=i, column=1, padx=5, pady=2)
            entry.insert(0, default)
            setattr(self, attr, entry)
        
        # Control buttons
        self.run_button = ttk.Button(self.control_frame, text="Run Simulation", command=self.run_simulation)
        self.run_button.grid(row=8, column=0, columnspan=2, pady=10)
        
        self.stop_button = ttk.Button(self.control_frame, text="Stop Simulation", command=self.stop_simulation, state=tk.DISABLED)
        self.stop_button.grid(row=8, column=2, pady=10)
        
        # Results display
        self.results_text = tk.Text(self.control_frame, height=10, width=40)
        self.results_text.grid(row=9, column=0, columnspan=3, pady=10)
        
        # Visualization canvas
        self.canvas = tk.Canvas(self.visualization_frame, bg="white")
        self.canvas.pack(expand=True, fill=tk.BOTH)
        
        # Scale control
        self.scale_frame = ttk.Frame(self.visualization_frame)
        self.scale_frame.pack(fill=tk.X, pady=5)
        ttk.Label(self.scale_frame, text="Zoom:").pack(side=tk.LEFT)
        self.scale_slider = ttk.Scale(self.scale_frame, from_=1, to=20, value=10, command=self.update_visualization)
        self.scale_slider.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_var.set("Ready")

    def create_widgets_sa(self):
        """Create all GUI widgets for Simulated Annealing"""
        # Input file selection
        ttk.Label(self.control_frame, text="Input File:").grid(row=0, column=0, sticky=tk.W)
        self.file_entry = ttk.Entry(self.control_frame, width=30)
        self.file_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(self.control_frame, text="Browse", command=self.browse_file).grid(row=0, column=2, padx=5)
        
        ttk.Button(self.control_frame, text="Load Simulation", command=self.load_simulation).grid(row=1, column=0, columnspan=3, pady=10)
        
        # Simulated Annealing parameters
        ttk.Label(self.control_frame, text="Simulated Annealing Parameters", font=('Arial', 10, 'bold')).grid(row=2, column=0, columnspan=3, pady=(10,5))
        
        # Lista de parâmetros para SA: (rótulo, valor padrão, nome do atributo)
        sa_params = [
            ("Initial Temperature:", "100.0", "initial_temp_entry"),
            ("Cooling Rate:", "0.95", "cooling_rate_entry"),
            ("Minimum Temperature:", "0.1", "min_temp_entry"),
            ("Max Iterations:", "1000", "max_iterations_entry")
        ]
        
        for i, (label, default, attr) in enumerate(sa_params, start=3):
            ttk.Label(self.control_frame, text=label).grid(row=i, column=0, sticky=tk.W)
            entry = ttk.Entry(self.control_frame, width=10)
            entry.grid(row=i, column=1, padx=5, pady=2)
            entry.insert(0, default)
            setattr(self, attr, entry)
        
        # Control buttons
        self.run_button = ttk.Button(self.control_frame, text="Run Simulation", command=self.run_simulation)
        self.run_button.grid(row=7, column=0, columnspan=2, pady=10)
        
        self.stop_button = ttk.Button(self.control_frame, text="Stop Simulation", command=self.stop_simulation, state=tk.DISABLED)
        self.stop_button.grid(row=7, column=2, pady=10)
        
        # Results display
        self.results_text = tk.Text(self.control_frame, height=10, width=40)
        self.results_text.grid(row=8, column=0, columnspan=3, pady=10)
        
        # Visualization canvas
        self.canvas = tk.Canvas(self.visualization_frame, bg="white")
        self.canvas.pack(expand=True, fill=tk.BOTH)
        
        # Scale control for zoom
        self.scale_frame = ttk.Frame(self.visualization_frame)
        self.scale_frame.pack(fill=tk.X, pady=5)
        ttk.Label(self.scale_frame, text="Zoom:").pack(side=tk.LEFT)
        self.scale_slider = ttk.Scale(self.scale_frame, from_=1, to=20, value=10, command=self.update_visualization)
        self.scale_slider.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_var.set("Ready")

    def create_widgets_gen(self):
        """Create all GUI widgets for Genetic Algorithm"""
        ttk.Label(self.control_frame, text="Input File:").grid(row=0, column=0, sticky=tk.W)
        self.file_entry = ttk.Entry(self.control_frame, width=30)
        self.file_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(self.control_frame, text="Browse", command=self.browse_file).grid(row=0, column=2, padx=5)
        
        ttk.Button(self.control_frame, text="Load Simulation", command=self.load_simulation).grid(row=1, column=0, columnspan=3, pady=10)
        
        ttk.Label(self.control_frame, text="Genetic Algorithm Parameters", font=('Arial', 10, 'bold')).grid(row=2, column=0, columnspan=3, pady=(10,5))
        
        ga_params = [
            ("Population Size:", "2", "population_size_entry"),
            ("Generations:", "50", "generations_entry"),
            ("Crossover Rate:", "0.7", "crossover_rate_entry"),
            ("Mutation Rate:", "0.1", "mutation_rate_entry"),
        ]
        
        for i, (label, default, attr) in enumerate(ga_params, start=3):
            ttk.Label(self.control_frame, text=label).grid(row=i, column=0, sticky=tk.W)
            entry = ttk.Entry(self.control_frame, width=10)
            entry.grid(row=i, column=1, padx=5, pady=2)
            entry.insert(0, default)
            setattr(self, attr, entry)
        
        self.run_button = ttk.Button(self.control_frame, text="Run Simulation", command=self.run_simulation)
        self.run_button.grid(row=7, column=0, columnspan=2, pady=10)
        
        self.stop_button = ttk.Button(self.control_frame, text="Stop Simulation", command=self.stop_simulation, state=tk.DISABLED)
        self.stop_button.grid(row=7, column=2, pady=10)
        
        self.results_text = tk.Text(self.control_frame, height=10, width=40)
        self.results_text.grid(row=8, column=0, columnspan=3, pady=10)
        
        self.canvas = tk.Canvas(self.visualization_frame, bg="white")
        self.canvas.pack(expand=True, fill=tk.BOTH)
        
        self.scale_frame = ttk.Frame(self.visualization_frame)
        self.scale_frame.pack(fill=tk.X, pady=5)
        ttk.Label(self.scale_frame, text="Zoom:").pack(side=tk.LEFT)
        self.scale_slider = ttk.Scale(self.scale_frame, from_=1, to=20, value=10, command=self.update_visualization)
        self.scale_slider.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_var.set("Ready")



    def browse_file(self):
        from tkinter import filedialog
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
            self.simulation_data = parse_file(filename.split('/')[-1])
            self.simulation = Simulation(self.simulation_data)
            self.status_var.set(f"Loaded simulation: {filename}")
            self.update_visualization()
            
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, f"Grid: {self.simulation.grid.rows}x{self.simulation.grid.cols}\n")
            self.results_text.insert(tk.END, f"Drones: {len(self.simulation.drones)}\n")
            self.results_text.insert(tk.END, f"Warehouses: {len(self.simulation.warehouses)}\n")
            self.results_text.insert(tk.END, f"Orders: {len(self.simulation.orders)}\n")
            self.results_text.insert(tk.END, f"Products: {len(self.simulation.products)}\n")
            self.results_text.insert(tk.END, f"Deadline: {self.simulation.deadline} turns\n")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load simulation: {str(e)}")

    def update_visualization(self, event=None):
        """Update the visualization canvas with delivery paths"""
        if not self.simulation:
            return
            
        self.canvas.delete("all")
        
        # Get scale factor from slider (1-20)
        scale_factor = self.scale_slider.get()
        
        # Calculate canvas dimensions
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # Calculate grid scaling factors
        rows = self.simulation.grid.rows
        cols = self.simulation.grid.cols
        
        # Determine cell size based on scale factor
        cell_size = min(canvas_width / cols, canvas_height / rows) * (scale_factor / 10)
        
        # Draw grid (simplified for large instances)
        if rows * cols <= 10000:  # Only draw grid for smaller instances
            for r in range(0, rows + 1, max(1, rows//50)):
                y = r * cell_size
                self.canvas.create_line(0, y, cols * cell_size, y, fill="lightgray")
            for c in range(0, cols + 1, max(1, cols//50)):
                x = c * cell_size
                self.canvas.create_line(x, 0, x, rows * cell_size, fill="lightgray")
        
        # FIRST DRAW PATHS (so they appear behind the nodes)
        if self.algorithm and hasattr(self.algorithm, 'best_path'):
            for order_solution in self.algorithm.best_path:
                drones_used, warehouses_visited, order_id, commands = order_solution
                try:
                    order = next(o for o in self.simulation.orders if o.order_id == order_id)
                    
                    # Draw paths from warehouses to order
                    for warehouse_id in warehouses_visited:
                        warehouse = next(w for w in self.simulation.warehouses if w.warehouse_id == warehouse_id)
                        x1 = warehouse.location.x * cell_size + cell_size/2
                        y1 = warehouse.location.y * cell_size + cell_size/2
                        x2 = order.location.x * cell_size + cell_size/2
                        y2 = order.location.y * cell_size + cell_size/2
                        self.canvas.create_line(x1, y1, x2, y2, 
                                            fill="orange", 
                                            width=2, 
                                            dash=(4,2),
                                            arrow=tk.LAST)  # Add arrow to show direction
                except StopIteration:
                    continue
        
        # THEN DRAW NODES (so they appear on top of paths)
        self.draw_simplified_elements(cell_size)

    def draw_simplified_elements(self, cell_size):
        """Draw simplified version of elements with better visibility"""
        # Draw warehouses (blue squares with white border)
        for warehouse in self.simulation.warehouses[:50]:  # Limit to first 50 warehouses
            x = warehouse.location.x * cell_size
            y = warehouse.location.y * cell_size
            self.canvas.create_rectangle(
                x+1, y+1, x + cell_size-1, y + cell_size-1,
                fill="blue", outline="white", width=2
            )
            self.canvas.create_text(
                x + cell_size/2, y + cell_size/2,
                text=f"W{warehouse.warehouse_id}",
                fill="white", font=('Arial', 8)
            )
        
        # Draw orders (red circles with white border)
        for order in self.simulation.orders[:100]:  # Limit to first 100 orders
            x = order.location.x * cell_size
            y = order.location.y * cell_size
            self.canvas.create_oval(
                x+1, y+1, x + cell_size-1, y + cell_size-1,
                fill="red", outline="white", width=2
            )
            self.canvas.create_text(
                x + cell_size/2, y + cell_size/2,
                text=f"O{order.order_id}",
                fill="white", font=('Arial', 8)
            )
        
        # Draw drones (green triangles with white border)
        for drone in self.simulation.drones[:20]:  # Limit to first 20 drones
            x = drone.location.x * cell_size
            y = drone.location.y * cell_size
            points = [
                x + cell_size/2, y+2,
                x+2, y + cell_size-2,
                x + cell_size-2, y + cell_size-2
            ]
            self.canvas.create_polygon(
                points,
                fill="green", outline="white", width=2
            )
            self.canvas.create_text(
                x + cell_size/2, y + cell_size/2,
                text=f"D{drone.drone_id}",
                fill="white", font=('Arial', 8)
            )

    def process_messages(self):
        """Handle messages from the background thread"""
        while not self.message_queue.empty():
            msg = self.message_queue.get_nowait()
            if msg == "COMPLETED":
                self.on_simulation_complete()
            elif msg.startswith("STATUS:"):
                self.status_var.set(msg[7:])
            elif msg.startswith("ERROR:"):
                messagebox.showerror("Error", msg[6:])
                self.running = False
        self.root.after(100, self.process_messages)

    def stop_simulation(self):
        """Stop a running simulation"""
        if self.running:
            self.running = False
            self.status_var.set("Simulation stopped by user")
            self.stop_button['state'] = tk.DISABLED
            self.run_button['state'] = tk.NORMAL

    def run_simulation_threaded(self):
        """Run the simulation in a background thread"""
        try:
            if self.algorithm == "ACO":
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
                
                # Run algorithm
                self.message_queue.put("STATUS:Running simulation...")
                best_path = self.algorithm.run()
                
                if not self.running:
                    self.message_queue.put("STATUS:Simulation stopped")
                    return
                    
                self.message_queue.put("COMPLETED")
            elif self.algorithm == "SA":
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
                self.message_queue.put("STATUS:Running simulation...")
                best_path, best_score = self.algorithm.run(
                    initial_temperature=initial_temp,
                    cooling_rate=cooling_rate,
                    min_temperature=min_temp,
                    max_iterations=max_iterations
                )
                
                if not self.running:
                    self.message_queue.put("STATUS:Simulation stopped")
                    return
                    
                self.message_queue.put("COMPLETED")
            elif self.algorithm == "GEN":
                pop_size = int(self.population_size_entry.get())
                num_gens = int(self.generations_entry.get())
                cross_rate = float(self.crossover_rate_entry.get())
                mut_rate  = float(self.mutation_rate_entry.get())
                
                self.algorithm = GeneticAlgorithm(
                    simulation=self.simulation,
                    population_size=pop_size,
                    num_generations=num_gens,
                    crossover_rate=cross_rate,
                    mutation_rate=mut_rate
                )
                
                self.message_queue.put("STATUS:Running Genetic Algorithm...")
                
                # We'll modify the GA run method to accept a "progress_callback" 
                # that is called after each generation with (gen, best_fit).
                best_chrom, best_fit = self.algorithm.run(progress_callback=self.genetic_progress_update)
                
                if not self.running:
                    self.message_queue.put("STATUS:Simulation stopped")
                    return
                self.message_queue.put("COMPLETED")
            
        except Exception as e:
            self.message_queue.put(f"ERROR:{str(e)}")
            self.running = False
    def sa_progress_update(self, iteration, current_best):
        """
        Example callback for SA so we can show partial updates.
        Called by the SA code each iteration or every N iterations.
        """
        # Post partial update
        if self.running:
            self.message_queue.put(f"UPDATE_GEN:{iteration}:{current_best}")  # reuse the "UPDATE_GEN" format

    def genetic_progress_update(self, gen, best_fitness):
        """
        Called by the GA code after each generation, or every few generations.
        """
        if self.running:
            self.message_queue.put(f"UPDATE_GEN:{gen}:{best_fitness}")



    def on_simulation_complete(self):
        """Handle simulation completion"""
        self.running = False
        self.stop_button['state'] = tk.DISABLED
        self.run_button['state'] = tk.NORMAL
        
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, f"Best solution found:\n")
        self.results_text.insert(tk.END, f"Score: {self.algorithm.score:.2f}\n")
        self.results_text.insert(tk.END, f"Completed in: {self.algorithm.completed_turns} turns\n\n")
        
        # Limit displayed results for large instances
        max_display = 5  # Show only first 5 orders for large instances
        for i, order_solution in enumerate(self.algorithm.best_path):
            if i >= max_display and len(self.algorithm.best_path) > max_display:
                remaining = len(self.algorithm.best_path) - max_display
                self.results_text.insert(tk.END, f"... and {remaining} more orders\n")
                break
                
            drones_used, warehouses_visited, order_id, commands = order_solution
            self.results_text.insert(tk.END, f"Order {order_id}:\n")
            self.results_text.insert(tk.END, f"  Drones: {drones_used}\n")
            self.results_text.insert(tk.END, f"  Warehouses: {warehouses_visited}\n")
            
            # Limit displayed commands
            cmd_display = min(3, len(commands))
            for cmd in commands[:cmd_display]:
                self.results_text.insert(tk.END, f"  - {cmd}\n")
            if len(commands) > cmd_display:
                self.results_text.insert(tk.END, f"  ... and {len(commands)-cmd_display} more commands\n")
            self.results_text.insert(tk.END, "\n")
        
        self.status_var.set(f"Simulation completed with score: {self.algorithm.score:.2f}")
        self.update_visualization()

    def run_simulation(self):
        """Start the simulation in a background thread"""
        if not self.simulation:
            messagebox.showerror("Error", "Please load a simulation first")
            return
            
        if self.running:
            messagebox.showwarning("Warning", "Simulation already running")
            return
            
        self.running = True
        self.run_button['state'] = tk.DISABLED
        self.stop_button['state'] = tk.NORMAL
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "Starting simulation...\n")
        
        # Start simulation in a separate thread
        Thread(target=self.run_simulation_threaded, daemon=True).start()

if __name__ == "__main__":
    print("Choose an algorithm to use:")
    print("  - ACO (Ant Colony Optimization)")
    print("  - SA  (Simulated Annealing)")
    print("  - GEN (Genetic Algorithm)")
    
    algo = input("Enter algorithm (ACO/SA/GEN): ").strip().upper()

    if algo not in ["ACO", "SA", "GEN"]:
        print("❌ Invalid choice. Defaulting to ACO.")
        algo = "ACO"

    root = tk.Tk()
    app = DroneDeliveryGUI(root, algorithm_type=algo)
    root.mainloop()