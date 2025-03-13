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


class Rack:
    def __init__(self, num_salamanders=50):
        self.inventory =[]
        self.num_salamanders = num_salamanders
        self.euthanasia_log = []
        
        for i in range(self.num_salamanders):
            dob = random_date(datetime(2020, 1, 1), datetime(2025, 1, 3))
            animal = {
            "Animal ID": f"SAL_{i+1:03d}",
            "Tank": random.randint(1, 10),
            "Rack": random.choice(racks),
            "DOB": dob,
            "Environmental Condition": random.choice(conditions),
            "Sex": None,
            "Lineage": random.choice(lineage),
            "Transgenic Status": random.choice(transgenic_status),
            "Experimental Holds": random.choice([True, False]),
            "Species": random.choice(species_list),
            "Protocol Number": random.choice(protocols),
            "Experimental History": random.choice(exp)
            }
            self.inventory.append(animal)
        self.inventory = pd.DataFrame(self.inventory)
        
    def __repr__(self):
        return f"<Rack with {len(self.inventory)} salamanders>"

    def __str__(self):
        return f"Rack with {len(self.inventory)} salamanders:\n{self.inventory.head()}"

    def move_salamander(self, animal_id, target_rack):
        """
        Move one or multiple salamanders from their current rack to a target rack.
    
        Parameters:
        - animal_id (str): Single animal ID or list of animal IDs to move.
        - target_rack (str): The rack to move the salamanders to.
        """
        # Trying for multiple animals to move - animal ids as list
        #if isinstance(animal_id, str):
            #animal_id = [animal_ids]  # Convert single ID to list
    
        # Loop through each animal ID and update their rack
        for animal_id in animal_id:
            # Find the animal in the inventory
            animal = self.inventory[self.inventory["Animal ID"] == animal_id]
    
            if not animal.empty:
                # Update the rack of the animal to the target rack
                self.inventory.loc[self.inventory["Animal ID"] == animal_id, "Rack"] = target_rack
                print(f"Animal {animal_id} moved to {target_rack}.")
            else:
                print(f"Animal {animal_id} not found in inventory.")

    def euthanize_animal(self, animal_id, dod, weight, sex, purpose, experimenter, complications="None"):
        euth_entry = {
            "Animal ID": animal_id,
            "DOD": dod,
            "Weight (g)": weight,
            "Sex": sex,
            "Purpose": purpose,
            "Experimenter": experimenter,
            "Complications": complications
        }
        self.euthanasia_log.append(euth_entry)

        self.inventory = self.inventory[self.inventory["Animal ID"] != animal_id]  # Remove from inventory
        #self.euthanasia_log = pd.DataFrame(self.euthanasia_log)

        print(f"Animal {animal_id} euthanized and removed from inventory.")



    # Function to plot Rack Space Usage Heatmap
    def plot_rack_space(self):
        rack_tank_count = self.inventory.groupby(["Rack", "Tank"]).size().unstack(fill_value=0)
    
        plt.figure(figsize=(8, 6))
        sns.heatmap(rack_tank_count, annot=True, cmap="coolwarm", linewidths=0.5, fmt="d")
        plt.title("Salamander Distribution Across Racks and Tanks")
        plt.xlabel("Tank Number")
        plt.ylabel("Rack Location")
        plt.show()

    # Function to plot Species Distribution
    def plot_transgenic_distribution(self):
        plt.figure(figsize=(7, 5))
        sns.countplot(y=self.inventory["Transgenic Status"], order=self.inventory["Transgenic Status"].value_counts().index)
        plt.title("Salamander Transgenic Distribution")
        plt.xlabel("Count")
        plt.ylabel("Animal Line")
        plt.show()

        
            
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
sex = ["None", "Male", "Female"]



# Example usage
#R.euthanize_animal("SAL_005", "2025-3-9", 10, "Male", "Tissue Collection", "AOG")


if __name__ == "__main__":
    pass
