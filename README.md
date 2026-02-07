# Drone Delivery Scheduling Problem (IART Assignment 1)

This project addresses a **drone delivery scheduling and optimization problem**, developed for the **IART (Artificial Intelligence)** course.  
The objective is to coordinate a fleet of drones to fulfill customer orders **as early as possible**, given product availability in warehouses and operational constraints.

The problem is inspired by the **Google Hash Code 2016 – Drone Delivery** challenge and focuses on modeling, constraint handling, and solution evaluation for a complex logistics scenario.

---

## 🚁 Problem Overview

Given:
- A **2D grid** representing the environment
- A set of **warehouses**, each with limited stock of different product types
- A set of **customer orders**, each requiring specific products
- A fleet of **drones** with limited payload capacity and movement constraints

The goal is to generate a **valid sequence of commands** for each drone such that:
- All orders are fulfilled
- Constraints are respected
- Orders are completed **as early as possible**

---

## 🗺️ Environment Model

- Each warehouse and customer location is placed at coordinates `(row, column)` on a finite grid
- The grid is **non-cyclic**; drones cannot leave its boundaries
- Drones can fly over any cell in the grid
- Distance between two positions is computed using **Euclidean distance**

---

## 📦 Orders and Products

- Each product type has a **fixed weight**
- A drone cannot exceed its **maximum payload**
- Total product demand does not exceed total warehouse availability
- Warehouses may not contain all product types

---

## 🤖 Drone Operations

Each drone can execute the following commands:

- **Load** products from a warehouse  
- **Deliver** products to a customer  
- **Unload** products  
- **Wait**

A solution is represented as a sequence of commands of the form:  (drone_id, command, warehouse_id, product_type, quantity)


---

## 🧠 Solution Approach

The project models the problem as a **search and optimization task**, with:

- **Neighborhood / mutation operators**, such as:
  - Swapping deliveries between drones
  - Reordering deliveries for a single drone
  - Inserting wait commands
- **Crossover operators** to combine two valid solutions
- **Hard constraints**, including:
  - Drone payload limits
  - Warehouse stock limits
  - Order demand limits
  - Simulation deadline

---

## 📊 Evaluation Function

Solutions are evaluated based on how early orders are completed.

The score is computed as: Score = ((T - t) / T) × 100


Where:
- `T` is the total number of simulation turns
- `t` is the turn in which an order is completed

Earlier deliveries result in higher scores.

---

## 🧱 Implementation Status

The project is implemented in **Python** and currently includes core data structures such as:

- `Grid`
- `Product`
- `Warehouse`
- `Order`
- `Drone`
- `Simulation`

These classes model the environment, entities, and simulation state required to build and evaluate solutions.

---

## 🛠️ Technologies Used

- Python
- Object-Oriented Programming
- Heuristic Optimization Concepts
- Constraint-Based Problem Modeling

---

## 👥 Authors

- Leonardo Garcia  
- Marcel Medeiros  
- Manoela Américo


