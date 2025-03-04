#!/usr/bin/env python

"""
A function for generating a sample salamander inventory
"""

import pandas as pd
import numpy as np
import random
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

# Generate random dates
def random_date(start, end):
    return start + timedelta(days=random.randint(0, (end - start).days))

# Possible values for metadata
species_list = ["Ambystoma mexicanum", "Pleurodeles waltl", "Polypterus senegalus"]
transgenic_status = ["Wildtype", "hsyn-GFP", "GCamP6s"]
protocols = ["AABF", "AABL", "AABI", "AABY"]
experimenters = ["AOG", "JW", "ECJ"]
racks = ["Rack 1", "Rack 2", "Rack 3"]
conditions = ["Terrestrial", "Aquatic", "Reaqua"]
lineage = ["YxO", "PxW", "Sweden", "Jungle Bobs"]
exp = ["Viral injection", "EdU", "Behavior Conditioning", "Regeneration"]

# Generate sample salamander inventory
num_salamanders = 50
inventory = []


for i in range(num_salamanders):
    dob = random_date(datetime(2020, 1, 1), datetime(2025, 1, 3))
    animal = {
        "Animal ID": f"SAL_{i+1:03d}",
        "Tank": random.randint(1, 10),
        "Rack": random.choice(racks),
        "DOB": dob,
        "Environmental Condition": random.choice(conditions),
        "Lineage": random.choice(lineage),
        "Transgenic Status": random.choice(transgenic_status),
        "RFID": random.randint(10000, 99999) if random.random() > 0.5 else None,
        "Experimental Holds": random.choice([True, False]),
        "Species": random.choice(species_list),
        "Protocol Number": random.choice(protocols),
        "Experimental History": random.choice(exp)
    }
    inventory.append(animal)

df = pd.DataFrame(inventory)
print(df.head())  # Display first few rows

# Function to plot Rack Space Usage Heatmap
def plot_rack_space():
    rack_tank_count = df.groupby(["Rack", "Tank"]).size().unstack(fill_value=0)
    
    plt.figure(figsize=(8, 6))
    sns.heatmap(rack_tank_count, annot=True, cmap="coolwarm", linewidths=0.5, fmt="d")
    plt.title("Salamander Distribution Across Racks and Tanks")
    plt.xlabel("Tank Number")
    plt.ylabel("Rack Location")
    plt.show()

# Function to plot Species Distribution
def plot_species_distribution():
    plt.figure(figsize=(7, 5))
    sns.countplot(y=df["Species"], palette="viridis", order=df["Species"].value_counts().index)
    plt.title("Salamander Species Distribution")
    plt.xlabel("Count")
    plt.ylabel("Species")
    plt.show()

# Call visualization functions
plot_rack_space()
plot_species_distribution()

# Function to log euthanasia events and update inventory
euthanasia_log = []

def euthanize_animal(animal_id, weight, sex, purpose, experimenter, complications="None"):
    global df, euthanasia_log
    dod = datetime.now()

    euth_entry = {
        "Animal ID": animal_id,
        "DOD": dod,
        "Weight (g)": weight,
        "Sex": sex,
        "Purpose": purpose,
        "Experimenter": experimenter,
        "Complications": complications
    }
    euthanasia_log.append(euth_entry)

    df = df[df["Animal ID"] != animal_id]  # Remove from inventory
    print(f"Animal {animal_id} euthanized and removed from inventory.")

# Example usage
euthanize_animal("SAL_005", 10, "Male", "Tissue Collection", "AOG")


# Convert logs to DataFrame for visualization if needed
df_euthanasia = pd.DataFrame(euthanasia_log)
print(df_euthanasia)


if __name__ == "__main__":
