#!/usr/bin/env python

"""
A function for parsing Tosches lab animal inventory
"""

import os
import random
import string
import tempfile
import itertools
import numpy as np
import pandas as pd
import seaborn as sns
from pathlib import Path
import matplotlib.pyplot as plt
from datetime import datetime, timedelta



class Rack:     
    def __init__(self, inventory_file="salamander_inventory.csv", filename ="inventory_state.csv", euthanasia_log_file ="euthanasia_log.csv"):
        
        # Expand and resolve relative paths to absolute     
        def resolve_path(path):
            return Path(path).expanduser().resolve() if path else None

        self.inventory_file = resolve_path(inventory_file)
        self.euthanasia_log_file = resolve_path(euthanasia_log_file)
        self.filename = resolve_path(filename) or Path(self.temp_dir.name) / "session_inventory.csv"  # File to save the state
        self.history = []  # Stack to store previous states for undo

        # Temporary directory for state saving
        self.temp_dir = tempfile.TemporaryDirectory()
        self.state_path = os.path.join(self.temp_dir.name, "inventory_state.csv")
        print(f"Temporary session directory created at {self.temp_dir}")

        #Loading inventory
        if self.inventory_file and self.inventory_file.exists():
            try:
                self.inventory = pd.read_csv(inventory_file)
                print(f"Loaded existing inventory from {inventory_file}")
            except FileNotFoundError:
                print(f"File {inventory_file} not found.")

        if self.euthanasia_log_file and self.euthanasia_log_file.exists():
            try:
                self.euthanasia_log = pd.read_csv(self.euthanasia_log_file).to_dict(orient="records")
            except pd.errors.EmptyDataError:
                print(f"{self.euthanasia_log_file} is empty. Initializing empty euthanasia log.")
                self.euthanasia_log = []
        else:
            self.euthanasia_log = []
        
        self.inventory = pd.DataFrame(self.inventory)
        self.save_state()  # Save initial state
        
    def __repr__(self):
        return f"<Inventory with {len(self.inventory)} salamanders>"

    def __str__(self):
        return f"Inventory with {len(self.inventory)} salamanders:\n{self.inventory.head()}"

    def save_state(self):
        """ Save the current state of the inventory and store in history. """
        self.history.append(self.inventory.copy())
        self.inventory.to_csv(self.filename, index=False)

    def undo(self):
        """ Revert to the last saved state if history exists. """
        if len(self.history) > 1:
            self.history.pop()
            self.inventory = self.history[-1].copy()
            self.save_inventory()
            self.save_state()
            print("Undo successful.")

            # Remove the most recent euthanasia entry, if it exists
            if self.euthanasia_log:
                removed = self.euthanasia_log.pop()  # Removes the last euthanasia entry
                self.save_euthanasia_log()
                self.log_change("Undo", f"Re-added {removed['Animal_ID']} and removed euthanasia log entry")
            else:
                self.log_change("Undo", "Inventory reverted, but no euthanasia entry to remove")

            print("Undo successful.")
        else:
            print("No previous state to undo.")

    def log_change(self, action, details):
        """ Log every change to a text file. 
        -action (str): what action taken
        -details (str): any relevant information to note"""
        with open("change_log.txt", "a") as f:
            f.write(f"{pd.Timestamp.now()} - {action}: {details}\n")
        print("Log successful")


    def save_euthanasia_log(self):
        if self.euthanasia_log_file:
            df = pd.DataFrame(self.euthanasia_log)
            
            # Append new entries without duplicating existing file
            df.to_csv(self.euthanasia_log_file, index=False)
        else:
            print("Euthanasia log not found")

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
    
        if transgenic_line not in transgenic_lines:
            print(f"Error: Transgenic line '{transgenic_line}' is not in the current inventory.")
            return

        if sex not in sex_list:
            sex = "Unknown"
            print(f"Error: Default sex to NaN")

        if tank not in self.get_tanks_for_rack(rack):
            print(f"Error: Tank '{tank}' does not exist.")
            return


        new_salamanders = []
        existing_ids = self.inventory["Animal_ID"].str.extract(r"SAL_(\d+)")  # Extract numeric part
        existing_ids = existing_ids.dropna().astype(int)  # Convert to int
        next_id = existing_ids.max().values[0] + 1 if not existing_ids.empty else 1  # Determine next ID

    
        for _ in range(num_salamanders):
            new_id = f"SAL_{next_id:03d}"
            #new_id = f"SAL_{len(self.inventory) + 1:03d}"  # Generate new unique ID
            #new_salamanders.append(animal)next_id += 1
            
            animal = {
                "Animal_ID": f"SAL_{next_id:03d}",
                "Tank": tank,
                "Rack": rack,
                "DOB": dob,
                "Environmental_Condition": env_condition,
                "Sex": sex,  # User can update later
                "Lineage": lineage,
                "Transgenic_Line": transgenic_line,
                "Experimental_Holds": experimental_holds,
                "Species": species,
                "Protocol_Number": protocol,
                "Experimental_History": experimental_history  # Can be updated later
            }

            # Save after adding
            new_salamanders.append(animal)
            next_id += 1  # Ensure unique IDs
            
            
        print(f"{num_salamanders} new salamander(s) adding successfully.")

        # Create DataFrame from new salamanders
        new_salamanders_df = pd.DataFrame(new_salamanders)

        # Ensure no duplicate IDs before appending
        if any(new_salamanders_df["Animal_ID"].isin(self.inventory["Animal_ID"])):
            print("Error: Duplicate Animal_IDs detected. Editing new IDs")
            return

        # Append new salamanders to inventory
        self.inventory = pd.concat([self.inventory, new_salamanders_df], ignore_index=True)

        self.save_inventory()
        self.save_state()
        self.log_change("Added animals", f"{num_salamanders} animals added to {rack} in {tank}.")
    
        print(f"{num_salamanders} baby salamanders added to {rack}, tank {tank}, with DOB {dob}.")

    
    def move_salamander(self, animal_id, target_rack, target_tank):
        """
        Move one or multiple salamanders from their current rack to a target rack.
    
        Parameters:
        - animal_id (str): Single animal ID or list of animal IDs to move.
        - target_rack (str): The rack to move the salamanders to.
        """
        # Normalize input to a list if it's a single ID
        if isinstance(animal_id, str):
            animal_id = [animal_id]

        if not self.is_valid_tank(target_rack, target_tank):
            print(f"Error: Tank '{target_tank}' is not valid for {target_rack}.")
            return
    
        # Loop through each animal ID and update their rack
        for animal_id in animal_id:
            # Find the animal in the inventory
            animal = self.inventory[self.inventory["Animal_ID"] == animal_id]
    
            if not animal.empty:
                # Update the rack of the animal to the target rack
                self.inventory.loc[self.inventory["Animal_ID"] == animal_id, "Rack"] = target_rack
                print(f"Animal {animal_id} moved to {target_rack}.")
                self.inventory.loc[self.inventory["Animal_ID"] == animal_id, "Tank"] = target_tank
                print(f"{target_tank}")
                self.log_change("Animals moved", f"{animal_id} to {target_rack}")
            else:
                print(f"Animal {animal_id} not found in inventory.")

        self.save_inventory()
        self.save_state()
        
    

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
        animal = self.inventory[self.inventory["Animal_ID"] == animal_id]

        if animal_id not in self.inventory["Animal_ID"].values:
            print(f"Error: Animal {animal_id} not found in inventory. Cannot euthanize.")
            return  
        
       
        # Automatically carry over the sex if it exists in inventory
        #this next line wasnt workign
        #sex = animal["Sex"].values[0] if pd.notna(animal["Sex"].values[0]) else "Unknown"

        # Retrieve the full animal information from the inventory allowing merge with inventory info
        animal_data = animal.iloc[0].to_dict()
        #old version of retrieval
        #animal_data = self.inventory[self.inventory["Animal_ID"] == animal_id].iloc[0]

        # Create the euthanasia entry by merging inventory info with euthanasia details
        euth_entry = {
            "Animal_ID": animal_id,
            "Tank": animal_data["Tank"],
            "Rack": animal_data["Rack"],
            "DOB": animal_data["DOB"],
            "Environmental_Condition": animal_data["Environmental_Condition"],
            "Lineage": animal_data["Lineage"],
            "Transgenic_Line": animal_data["Transgenic_Line"],
            "Experimental_Holds": animal_data["Experimental_Holds"],
            "Species": animal_data["Species"],
            "Protocol_Number": animal_data["Protocol_Number"],
            "Experimental_History": animal_data["Experimental_History"],
            "DOD": dod,
            "Weight_g": weight,
            "Sex": sex if sex and sex != "Unknown" else animal_data.get("Sex", "Unknown"),
            "Purpose": purpose,
            "Experimenter": experimenter,
            "Complications": complications
        }
    
        # Add the euthanasia entry to the euthanasia log
        self.euthanasia_log.append(euth_entry)

        #Remove animal from inventory
        self.inventory = self.inventory[self.inventory["Animal_ID"] != animal_id]
 
        # Save euth log changes
        self.save_euthanasia_log()

        #update change log
        self.log_change("Euthanized", f"{animal_id} on {dod}")
        
        #save changes to inventory
        self.save_inventory()
        self.save_state()

        print(f"Animal {animal_id} euthanized and removed from inventory.")

    def edit_salamander_info(self, animal_id, **updates):
        """
        Editable fields for a specific salamander by Animal ID.

        Parameters:
        - animal_id (str): ID of the salamander to edit.
        - updates (dict): Key-value pairs of the fields to update.
          Valid keys: 'Environmental Condition', 'Sex', 'Experimental Holds',
                      'Protocol Number', 'Experimental History'
        """
        valid_fields = {
            "Environmental_Condition",
            "Sex",
            "Experimental_Holds",
            "Protocol_Number",
            "Experimental_History"
        }

        if animal_id not in self.inventory["Animal_ID"].values:
            print(f"Error: Animal_ID {animal_id} not found in inventory.")
            return

        row_index = self.inventory[self.inventory["Animal_ID"] == animal_id].index[0]

        changes = []
        for key, value in updates.items():
            if key in valid_fields:
                old_value = self.inventory.at[row_index, key]
                self.inventory.at[row_index, key] = value
                changes.append(f"{key}: {old_value} → {value}")
            else:
                print(f"Warning: '{key}' is not a valid editable field. Skipped.")

        if changes:
            self.save_inventory()
            self.save_state()
            self.log_change("Edit", f"{animal_id} - " + "; ".join(changes))
            print(f"Updated {animal_id}:")
            for change in changes:
                print(" -", change)
        else:
            print("No valid changes made.")

    def analyze_euthanasia_log(self):
        if not self.euthanasia_log:
            print("No euthanasia records to analyze.")
            return

        log_df = pd.DataFrame(self.euthanasia_log)
        log_df["Year"] = pd.to_datetime(log_df["DOD"]).dt.year

        summary = (
            log_df
            .groupby(["Protocol Number", "Year"])
            .agg(
                total_euthanized=("Animal_ID", "count"),
                complications=("Complications", lambda x: (x != "None").sum())
            )
            .reset_index()
        )
        
        return summary

    def search_salamanders(self, **criteria):
        """
        Search for salamanders in the inventory based on given criteria.
    
        Parameters:
        - **criteria: Keyword arguments where keys are column names and values are search terms.
                      Supports partial matches (case-insensitive).
    
        Returns:
        - A filtered DataFrame with matching salamanders.
        """
        if not criteria and min_age is None and max_age is None:
            print("Please provide at least one search criterion.")
            return None

        exact_match_fields = {"Sex", "Rack", "Tank", "Protocol_Number"}  
    
        filtered_inventory = self.inventory.copy()  # Start with the full inventory
        
        min_age = criteria.pop("min_age", None)
        max_age = criteria.pop("max_age", None)

        # Age calculation (DOB must be datetime)
        filtered_inventory["DOB"] = pd.to_datetime(filtered_inventory["DOB"], errors="coerce")
        today = pd.Timestamp.today()
        filtered_inventory["Age_Years"] = (today - filtered_inventory["DOB"]).dt.days / 365.25

        if min_age is not None:
            filtered_inventory = filtered_inventory[filtered_inventory["Age_Years"] >= min_age]

        if max_age is not None:
            filtered_inventory = filtered_inventory[filtered_inventory["Age_Years"] <= max_age]



        for key, value in criteria.items():
            if key not in filtered_inventory.columns:
                print(f"Warning: '{key}' is not a valid column in the inventory.")
                continue  # Skip invalid columns
            if key in exact_match_fields:
                filtered_inventory = filtered_inventory[
                    filtered_inventory[key].astype(str).str.lower() == str(value).lower()
                ]

            else:
                # Use case-insensitive regex search for partial matches
                filtered_inventory = filtered_inventory[
                    filtered_inventory[key].astype(str).str.contains(str(value), case=False, na=False)
                ]
        
        return filtered_inventory if not filtered_inventory.empty else "No matches found."

    # Function to plot Rack Space Usage Heatmap
    def get_tanks_for_rack(self, rack):
        if rack in limited_racks:
            return limited_tanks
        else:
            return full_tanks

    def plot_rack_space(self, inventory_subset=None, return_fig=False):

        # Create an empty DataFrame with all possible valid (rack, tank) combinations
        full_layout = []

        for rack in valid_racks:
            tanks = limited_tanks if rack in limited_racks else full_tanks
            for tank in tanks:
                full_layout.append((rack, tank))

        layout_df = pd.DataFrame(full_layout, columns=["Rack", "Tank"])
        layout_df["Count"] = 0

        # Count current animals
        inventory = inventory_subset if inventory_subset is not None else self.inventory
        counts = inventory.groupby(["Rack", "Tank"]).size().reset_index(name="Count")


        # Merge with the full layout to ensure all (rack, tank) pairs are present
        merged = layout_df.merge(counts, on=["Rack", "Tank"], how="left", suffixes=("", "_actual"))
        merged["Count"] = merged["Count_actual"].fillna(0).astype(int)
        merged.drop(columns=["Count_actual"], inplace=True)

        # Pivot for heatmap, sorted numerically by rack
        pivot = merged.pivot(index="Rack", columns="Tank", values="Count").fillna(0)
        pivot = pivot.astype(int)
        pivot = pivot.loc[sorted(pivot.index, key=lambda x: int(x.split()[1]))]
        
        # Create a mask for invalid tank positions (tanks that don't exist for the rack)    
        mask = pd.DataFrame(False, index=pivot.index, columns=pivot.columns)
        for rack in pivot.index:
            valid_tanks = self.get_tanks_for_rack(rack)
            for tank in pivot.columns:
                if tank not in valid_tanks:
                    mask.loc[rack, tank] = True

        # Sort the tank columns in a consistent order
        sorted_tanks = sorted(pivot.columns, key=lambda x: (x[0], int(x[1:])))
        pivot = pivot[sorted_tanks]

        # Fill NaNs for safe plotting (mask handles visibility)
        #plot_data = pivot.fillna(0).astype(int)

        # Plot
        fig, ax = plt.subplots(figsize=(14, 8))
        sns.heatmap(
            pivot, 
            mask=mask, 
            annot=True, 
            fmt="d", 
            cmap="coolwarm", 
            linewidths=0.5, 
            linecolor='gray', 
            cbar_kws={'label': 'Count'},
            ax=ax
        )
        ax.set_title("Salamander Distribution Across Racks and Tanks", fontsize=16)
        ax.set_xlabel("Tank", fontsize=12)
        ax.set_ylabel("Rack", fontsize=12)
        plt.xticks(rotation=45)
        plt.tight_layout()

        if return_fig:
            return fig
        else:
            plt.show()

    # Function to plot Transgenic Distribution
    def plot_transgenic_distribution(self):
        plt.figure(figsize=(7, 5))
        sns.countplot(y=self.inventory["Transgenic Line"], order=self.inventory["Transgenic Line"].value_counts().index)
        plt.title("Salamander Transgenic Distribution")
        plt.xlabel("Count")
        plt.ylabel("Animal Line")
        plt.show()

    def save_inventory(self, inventory_file = None):
        """Save the current inventory to a CSV file."""
        if self.inventory_file:
            self.inventory.to_csv(self.inventory_file, index=False)
            print(f"Inventory saved to {self.inventory_file}.")
        else:
            print("No CSV file specified. Inventory not saved.")

    def is_valid_tank(self, rack, tank):
        """
        Check if the provided tank is valid for the given rack based on rack_layouts.
        
        Parameters:
        - rack (str): Rack name (e.g., "Rack 1")
        - tank (str): Tank ID (e.g., "A3")

            """
        valid_racks = [
            "Rack 1", "Rack 2", "Rack 3", "Rack 4", "Rack 5",
            "Rack 6", "Rack 7", "Rack 8", "Rack 9", "Rack 10", "Rack 11", "Rack 12"
        ]
        limited_racks = ["Rack 1", "Rack 3", "Rack 5", "Rack 7", "Rack 9", "Rack 10", "Rack 11"]

        if rack not in valid_racks:
            return False

        limited_tanks = [f"{row}{col}" for row in "ABC" for col in range(1, 5)] #A1-C4
        full_tanks = [f"{row}{col}" for row in "ABCD" for col in range(1, 7)] #A1-D6

        valid_tanks = limited_tanks if rack in limited_racks else full_tanks
        return tank in valid_tanks

            
species_list = ["Ambystoma mexicanum", "Pleurodeles waltl", "Polypterus senegalus"]
transgenic_lines = ["Wildtype", "hsyn-GFP", "hsyn-GCamP6s", "hsyn-Cre", "mDlx-ChR2"]
racks = ["Rack 1", "Rack 2", "Rack 3", "Rack 4", "Rack 5", "Rack 6", "Rack 7", "Rack 8", "Rack 9", "Rack 10", "Rack 11", "Rack 12"]
protocols = ["AABF2564", "AABL1550", "AABI2617", "AABY5655"]
conditions = ["Terrestrial", "Aquatic", "Reaqua"]
sex_list = ["None", "Male", "Female"]
# Define valid racks and tank layout
valid_racks = [
        "Rack 1", "Rack 2", "Rack 3", "Rack 4", "Rack 5",
        "Rack 6", "Rack 7", "Rack 8", "Rack 9", "Rack 10", "Rack 11", "Rack 12"
        ]
limited_racks = ["Rack 1", "Rack 3", "Rack 5", "Rack 7", "Rack 9", "Rack 10", "Rack 11"]

limited_tanks = [f"{row}{col}" for row in "ABC" for col in range(1, 5)]   # A1–C4
full_tanks = [f"{row}{col}" for row in "ABCD" for col in range(1, 7)]     # A1–D6

"""rack_layouts = {
    "Rack 1":  {"rows": ["A", "B", "C"], "cols": [1, 2, 3, 4]},
    "Rack 3":  {"rows": ["A", "B", "C"], "cols": [1, 2, 3, 4]},
    "Rack 5":  {"rows": ["A", "B", "C"], "cols": [1, 2, 3, 4]},
    "Rack 7":  {"rows": ["A", "B", "C"], "cols": [1, 2, 3, 4]},
    "Rack 9":  {"rows": ["A", "B", "C"], "cols": [1, 2, 3, 4]},
    "Rack 10": {"rows": ["A", "B", "C"], "cols": [1, 2, 3, 4]},
    "Rack 11": {"rows": ["A", "B", "C"], "cols": [1, 2, 3, 4]},
    "Rack 2":  {"rows": ["A", "B", "C", "D"], "cols": [1, 2, 3, 4, 5, 6]},
    "Rack 4":  {"rows": ["A", "B", "C", "D"], "cols": [1, 2, 3, 4, 5, 6]},
    "Rack 6":  {"rows": ["A", "B", "C", "D"], "cols": [1, 2, 3, 4, 5, 6]},
    "Rack 8":  {"rows": ["A", "B", "C", "D"], "cols": [1, 2, 3, 4, 5, 6]},
    "Rack 12": {"rows": ["A", "B", "C", "D"], "cols": [1, 2, 3, 4, 5, 6]},
}"""


if __name__ == "__main__":
    pass
