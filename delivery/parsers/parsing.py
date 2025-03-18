def parse_file(filename):
    """
    Parse a file and return a list of locations.
    :param file: file to be parsed
    :return: list of locations
    """

    data = {}
    locations = []
    with open(f"inputs/{filename}", "r", encoding="utf-8") as file:
        # 📌 First Section
        rows, cols, drones, deadline, max_load = map(int, file.readline().split())
        data["simulation"] = {
            "rows": rows,
            "cols": cols,
            "drones": drones,
            "deadline": deadline,
            "max_load": max_load
        }

        # 📌 Second Section
        num_products = int(file.readline().strip())
        data["num_products"] = num_products
        product_weights = list(map(int, file.readline().split()))
        data["product_weights"] = product_weights

        # 📌 Third Section
        num_warehouses = int(file.readline().strip())
        data["num_warehouses"] = num_warehouses
        data["warehouses"] = []
        for _ in range(num_warehouses):
            row, col = map(int, file.readline().split())
            stock = list(map(int, file.readline().split()))
            data["warehouses"].append({"location": (row, col), "stock": stock})
        
        # 📌 Fourth Section
        num_orders = int(file.readline().strip())
        data["num_orders"] = num_orders
        data["orders"] = []
        for _ in range(num_orders):
            row, col = map(int, file.readline().split())
            num_items = int(file.readline().strip())
            product_types = list(map(int, file.readline().split()))
            data["orders"].append({
                "destination": (row, col),
                "num_items": num_items,
                "product_types": product_types
            })

    return data
        

# ----- Testing ------ #
# simulation_data = parse_file("busy_day.in")
# print(simulation_data["num_warehouses"])