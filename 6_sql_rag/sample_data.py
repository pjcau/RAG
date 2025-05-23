import random
from datetime import datetime, timedelta
import csv
import os
import sqlite3


def generate_cars_motors_dataset(num_records=5000):
    models = {
        "Porsche 911": {"price_range": (120000, 250000), "mileage_range": (280, 350)},
        "Audi RS e-tron GT": {"price_range": (150000, 180000), "mileage_range": (330, 420)},
        "Ferrari SF90": {"price_range": (450000, 550000), "mileage_range": (340, 380)},
        "Lamborghini Huracán": {"price_range": (200000, 300000), "mileage_range": (290, 340)},
        "Maserati MC20": {"price_range": (230000, 280000), "mileage_range": (310, 370)},
        "Bentley Continental GT": {"price_range": (220000, 280000), "mileage_range": (280, 350)},
        "Aston Martin DBS": {"price_range": (300000, 380000), "mileage_range": (290, 340)},
        "McLaren 720S": {"price_range": (280000, 350000), "mileage_range": (300, 360)},
        "Rolls-Royce Ghost": {"price_range": (350000, 450000), "mileage_range": (320, 380)},
        "Bugatti Chiron": {"price_range": (2500000, 3500000), "mileage_range": (350, 420)},
        "Lexus LC 500": {"price_range": (95000, 120000), "mileage_range": (270, 330)},
        "Range Rover Sport": {"price_range": (80000, 150000), "mileage_range": (250, 300)},
        "Pagani Huayra": {"price_range": (2800000, 3200000), "mileage_range": (330, 380)},
        "Koenigsegg Jesko": {"price_range": (3000000, 3500000), "mileage_range": (340, 400)},
        "BMW M8": {"price_range": (130000, 160000), "mileage_range": (290, 350)},
        "Jaguar F-Type": {"price_range": (75000, 95000), "mileage_range": (260, 310)},
        "Alpine A110": {"price_range": (65000, 85000), "mileage_range": (180, 220)},
        "Lotus Emira": {"price_range": (85000, 105000), "mileage_range": (225, 275)},
        "Mercedes-AMG GT": {"price_range": (120000, 160000), "mileage_range": (280, 330)},
        "Nissan GT-R": {"price_range": (115000, 145000), "mileage_range": (275, 315)},
        "Audi RS7": {"price_range": (120000, 150000), "mileage_range": (265, 305)},
        "Maserati Ghibli": {"price_range": (75000, 95000), "mileage_range": (255, 295)},
        "BMW M5 CS": {"price_range": (140000, 170000), "mileage_range": (270, 310)},
        "Porsche Cayman GT4": {"price_range": (105000, 125000), "mileage_range": (240, 280)},
        "Aston Martin Vantage": {"price_range": (150000, 180000), "mileage_range": (270, 320)}
    }
    colors = ["Pearl White", "Solid Black", "Deep Blue Metallic",
              "Midnight Silver Metallic", "Red Multi-Coat", "Ultra Red", "Stealth Grey"]
    # Tesla only has automatic transmission
    fuel_types = ["Diesel", "Oil"]
    transmission_types = {"Automatic": 1.0}
    states = [
        "Japan", "Italy", "South Korea", "New York", "German", "Washington", "Massachusetts",
        "New Jersey", "Colorado", "Virginia", "China", "Nevada", "France", "Connecticut", "Maryland"
    ]
    dataset = []

    for _ in range(num_records):
        model = random.choice(list(models.keys()))
        color = random.choice(colors)
        transmission = "Automatic"
        fuel_type = random.choice(fuel_types)

        price_range = models[model]["price_range"]
        price = round(random.uniform(*price_range), 2)

        mileage_range = models[model]["mileage_range"]
        mileage = round(random.uniform(*mileage_range), 1)

        manufacture_date = datetime.now() - timedelta(days=random.randint(1, 730)
                                                      )  # Up to 2 years old
        sale_date = manufacture_date + \
            timedelta(days=random.randint(1, 90))  # Up to 3 months to sell
        state = random.choice(states)

        seating_capacity = 4 if model in [
            "BMV X5", "Alfa Romeo Tonale"] else 6
        ground_clearance = round(random.uniform(140, 170), 1)
        boot_space = random.randint(
            425, 900 if model in ["BMV X5", "Alfa Romeo Tonale"] else 650
        )

        record = {
            "model": model,
            "color": color,
            "fuel_type": fuel_type,
            "transmission": transmission,
            "price": price,
            "manufacture_date": manufacture_date.strftime("%Y-%m-%d"),
            "sale_date": sale_date.strftime("%Y-%m-%d"),
            "state": state,
            "mileage": mileage,
            "seating_capacity": seating_capacity,
            "ground_clearance": ground_clearance,
            "boot_space": boot_space
        }

        dataset.append(record)

    return dataset


def save_to_csv(data, filename="cars_motors_data.csv"):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, filename)

    with open(file_path, 'w', newline='') as csvfile:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for row in data:
            writer.writerow(row)

    return file_path


def save_to_sqlite(data, db_name="cars_motors_data.db"):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, db_name)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cars_motors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        model TEXT,
        color TEXT,
        fuel_type TEXT,
        transmission TEXT,
        price REAL,
        manufacture_date TEXT,
        sale_date TEXT,
        state TEXT,
        mileage REAL,
        seating_capacity INTEGER,
        ground_clearance REAL,
        boot_space INTEGER
    )
    ''')

    # Insert data
    for record in data:
        cursor.execute('''
        INSERT INTO cars_motors (
            model, color, fuel_type, transmission, price, manufacture_date, sale_date,
            state, mileage, seating_capacity,
            ground_clearance, boot_space
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', tuple(record.values()))

    conn.commit()
    conn.close()

    return db_path


# Generate the dataset
cars_motors_data = generate_cars_motors_dataset(5000)

# Save the dataset to a CSV file
csv_file_path = save_to_csv(cars_motors_data)

# Save the dataset to a SQLite database
db_file_path = save_to_sqlite(cars_motors_data)

print(f"Dataset has been saved to CSV: {csv_file_path}")
print(f"Dataset has been saved to SQLite database: {db_file_path}")

# Print the first 5 records as a sample
for i, record in enumerate(cars_motors_data[:5], 1):
    print(f"\nRecord {i}:")
    for key, value in record.items():
        print(f"  {key}: {value}")

print(f"\nTotal records generated and saved: {len(cars_motors_data)}")
