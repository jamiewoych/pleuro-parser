#!/usr/bin/env python

"""
A function for parsing Tosches lab animal inventory
"""

import pandas as pd
import numpy as np
import random
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta


class Rack:     
    def __init__(self, inventory_file=None):
        self.inventory =[]
        self.euthanasia_log = []

        if inventory_file:
            try:
                self.inventory = pd.read_csv(inventory_file)
                print(f"Loaded existing inventory from {inventory_file}")
            except FileNotFoundError:
                print(f"File {inventory_file} not found.")
                
        self.inventory = pd.DataFrame(self.inventory)
        
    def __repr__(self):
        return f"<Inventory with {len(self.inventory)} salamanders>"

    def __str__(self):
        return f"Inventory with {len(self.inventory)} salamanders:\n{self.inventory.head()}"

    def add_salamanders(self, num_salamanders, dob, species, transgenic_line, lineage, protocol, rack, tank, env_condition, sex, experimental_holds, experimental_history):
        """
        Adds multiple salamanders with the same date of birth to the inventory.
    
        Parameters:
        - num_salamanders (int): Number of salamanders to add.
        - dob (str): Date of birth (format: "YYYY-MM-DD").
        - species (str): Species of the salamanders.
        - transgenic_line (str): Transgenic line.
        - lineage (str): Lineage of the salamanders.
        - protocol (str): Associated protocol number.
        - rack (str): The rack where salamanders will be placed.
        - tank (int): The tank where salamanders will be placed.
        - env_condition (str): Terra, Aqua, Reaqua
        - sex (str): Male, Female, Unknown
        - experimental_holds (bool): Whether the salamanders are on experimental holds.
        - experimental_history (str): Experiments animals have undergone
        """
        if rack not in racks:
            print(f"Error: Rack '{rack}' is not in the current inventory.")
            return
    
        if species not in species_list:
            print(f"Error: Species '{species}' is not in the current inventory.")
            return
    
        if transgenic_line not in transgenic_line:
            print(f"Error: Transgenic line '{transgenic_line}' is not in the current inventory.")
            return

        if sex not in sex:
            print(f"Error: Default to unknown")
    
        for _ in range(num_salamanders):
            new_id = f"SAL_{len(self.inventory) + 1:03d}"  # Generate new unique ID
    
            animal = {
                "Animal ID": new_id,
                "Tank": tank,
                "Rack": rack,
                "DOB": dob,
                "Environmental Condition": env_condition,
                "Sex": None,  # User can update later
                "Lineage": lineage,
                "Transgenic Line": transgenic_line,
                "Experimental Holds": experimental_holds,
                "Species": species,
                "Protocol Number": protocol,
                "Experimental History": None  # Can be updated later
            }
    
            self.inventory = pd.concat([self.inventory, pd.DataFrame([animal])], ignore_index=True)
    
        print(f"{num_salamanders} new salamanders added to {rack}, tank {tank}, with DOB {dob}.")

    
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
        """
        Euthanizes a salamander and records it in the euthanasia log.
    
        Parameters:
        - animal_id (str): ID of the salamander to be euthanized.
        - dod (str): Date of death.
        - weight (float): Weight in grams.
        - sex (str): Sex of the salamander.
        - purpose (str): Reason for euthanasia.
        - experimenter (str): Name of the experimenter.
        - complications (str, optional): Any complications. Defaults to "None".
        """
        # Check if the animal exists in the inventory
        if animal_id not in self.inventory["Animal ID"].values:
            print(f"Error: Animal {animal_id} not found in inventory. Cannot euthanize.")
            return  
            
        # Automatically carry over the sex if it exists in inventory
        sex = animal["Sex"].values[0] if pd.notna(animal["Sex"].values[0]) else "Unknown"

        # Retrieve the full animal information from the inventory
        animal_data = self.inventory[self.inventory["Animal ID"] == animal_id].iloc[0]

        # Create the euthanasia entry by merging inventory info with euthanasia details
        euth_entry = {
            "Animal ID": animal_id,
            "Tank": animal_data["Tank"],
            "Rack": animal_data["Rack"],
            "DOB": animal_data["DOB"],
            "Environmental Condition": animal_data["Environmental Condition"],
            "Lineage": animal_data["Lineage"],
            "Transgenic Line": animal_data["Transgenic Line"],
            "Experimental Holds": animal_data["Experimental Holds"],
            "Species": animal_data["Species"],
            "Protocol Number": animal_data["Protocol Number"],
            "Experimental History": animal_data["Experimental History"],
            "DOD": dod,
            "Weight (g)": weight,
            "Sex": sex,
            "Purpose": purpose,
            "Experimenter": experimenter,
            "Complications": complications
        }
    
        # Add the euthanasia entry to the euthanasia log

        self.euthanasia_log.append(euth_entry)

        self.inventory = self.inventory[self.inventory["Animal ID"] != animal_id]  # Remove from inventory
        #self.euthanasia_log = pd.DataFrame(self.euthanasia_log)

        print(f"Animal {animal_id} euthanized and removed from inventory.")
        #animals that dont exist still works - do input validation &regulate values of metadata

    def search_salamanders(self, **criteria):
        """
        Search for salamanders in the inventory based on given criteria.
    
        Parameters:
        - **criteria: Keyword arguments where keys are column names and values are search terms.
                      Supports partial matches (case-insensitive).
    
        Returns:
        - A filtered DataFrame with matching salamanders.
        """
        if not criteria:
            print("Please provide at least one search criterion.")
            return None
    
        filtered_inventory = self.inventory  # Start with the full inventory
    
        for key, value in criteria.items():
            if key not in self.inventory.columns:
                print(f"Warning: '{key}' is not a valid column in the inventory.")
                continue  # Skip invalid columns
    
            # Use case-insensitive regex search for partial matches
            filtered_inventory = filtered_inventory[
                filtered_inventory[key].astype(str).str.contains(str(value), case=False, na=False)
            ]
    
        return filtered_inventory if not filtered_inventory.empty else "No matches found."

    # Function to plot Rack Space Usage Heatmap
    def plot_rack_space(self):
        rack_tank_count = self.inventory.groupby(["Rack", "Tank"]).size().unstack(fill_value=0)
    
        plt.figure(figsize=(8, 6))
        sns.heatmap(rack_tank_count, annot=True, cmap="coolwarm", linewidths=0.5, fmt="d")
        plt.title("Salamander Distribution Across Racks and Tanks")
        plt.xlabel("Tank Number")
        plt.ylabel("Rack Location")
        plt.show()
        #empty racks arent shown

    # Function to plot Transgenic Distribution
    def plot_transgenic_distribution(self):
        plt.figure(figsize=(7, 5))
        sns.countplot(y=self.inventory["Transgenic Line"], order=self.inventory["Transgenic Line"].value_counts().index)
        plt.title("Salamander Transgenic Distribution")
        plt.xlabel("Count")
        plt.ylabel("Animal Line")
        plt.show()
            
species_list = ["Ambystoma mexicanum", "Pleurodeles waltl", "Polypterus senegalus"]
transgenic_line = ["Wildtype", "hsyn-GFP", "hsyn-GCamP6s", "hsyn-Cre", "mDlx-ChR2"]
racks = ["Rack 1", "Rack 2", "Rack 3", "Rack 4", "Rack 5", "Rack 6", "Rack 7", "Rack 8", "Rack 9", "Rack 10", "Rack 11" "Rack 12"]
protocols = ["AABF2564", "AABL1550", "AABI2617", "AABY5655"]
conditions = ["Terrestrial", "Aquatic", "Reaqua"]
sex = ["None", "Male", "Female"]

#store changes as text file with timestamp to track what people have done
# Example usage
#R.euthanize_animal("SAL_005", "2025-3-9", 10, "Male", "Tissue Collection", "AOG")


if __name__ == "__main__":
    pass
