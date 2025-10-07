#!/usr/bin/env python

"""
A function for parsing Tosches lab animal inventory
"""

import os
import git
import shutil
import tempfile
import pandas as pd
import seaborn as sns
import streamlit as st
from pathlib import Path
#from github import Github
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

#to run locally switch comment for 18/19 and 158/159
class Rack:     
    #def __init__(self, inventory_file="https://raw.githubusercontent.com/jamiewoych/pleuro-parser/refs/heads/main/pleuro_parser/salamander_inventory.csv", filename ="https://raw.githubusercontent.com/jamiewoych/pleuro-parser/refs/heads/main/pleuro_parser/inventory_state.csv", euthanasia_log_file ="https://raw.githubusercontent.com/jamiewoych/pleuro-parser/refs/heads/main/pleuro_parser/euthanasia_log.csv", clutches_file = "https://raw.githubusercontent.com/jamiewoych/pleuro-parser/refs/heads/main/pleuro_parser/Larval_Clutches.csv", larval_euth_file = "https://raw.githubusercontent.com/jamiewoych/pleuro-parser/refs/heads/main/pleuro_parser/larval_euth_log.csv"):
    def __init__(self, inventory_file="salamander_inventory.csv", filename ="inventory_state.csv", euthanasia_log_file ="euthanasia_log.csv", clutches_file = "Larval_Clutches.csv", larval_euth_file = "larval_euth_log.csv"):
        # Expand and resolve relative paths to absolute     
        def resolve_path(path):
            return Path(path).expanduser().resolve() if path else None


        # Check if we are running in a Streamlit environment or locally
        is_streamlit = "STREAMLIT" in os.environ  # Streamlit Cloud or similar platform can set this variable


        # Get the base directory for the pleuro_parser folder (current working directory is the pleuro_parser directory)
        base_dir = Path(__file__).resolve().parent  # Directory of the current script (i.e., pleuro_parser)

        if is_streamlit:
            self.inventory_file="https://raw.githubusercontent.com/jamiewoych/pleuro-parser/refs/heads/main/pleuro_parser/salamander_inventory.csv" 
            self.filename ="https://raw.githubusercontent.com/jamiewoych/pleuro-parser/refs/heads/main/pleuro_parser/inventory_state.csv"
            self.euthanasia_log_file ="https://raw.githubusercontent.com/jamiewoych/pleuro-parser/refs/heads/main/pleuro_parser/euthanasia_log.csv" 
            self.clutches_file = "https://raw.githubusercontent.com/jamiewoych/pleuro-parser/refs/heads/main/pleuro_parser/Larval_Clutches.csv",
            self.larval_euth_file = "https://raw.githubusercontent.com/jamiewoych/pleuro-parser/refs/heads/main/pleuro_parser/larval_euth_log.csv"
        else:
            # Local paths for local development
            parent_dir = base_dir.parent  # This points to the 'pleuro-parser' parent folder
            
            # Local file paths
            self.inventory_file = parent_dir / 'salamander_inventory.csv'
            self.filename = parent_dir / 'inventory_state.csv'
            self.euthanasia_log_file = parent_dir / 'euthanasia_log.csv'
            self.clutches_file = parent_dir / 'Larval_Clutches.csv'
            self.larval_euth_file = parent_dir / 'larval_euth_log.csv'

        """
        Removed 6-10-25 
        self.inventory_file = resolve_path(inventory_file)
        self.euthanasia_log_file = resolve_path(euthanasia_log_file)
        self.filename = resolve_path(filename) or Path(self.temp_dir.name) / "session_inventory.csv"  # File to save the state
        self.history = []  # Stack to store previous states for undo
        self.clutches_file = resolve_path(clutches_file)
        self.larval_euth_file = resolve_path(larval_euth_file)"""

        # Print paths for debugging
        #st.write(f"Inventory file path: {self.inventory_file}")
        #st.write(f"Clutches file path: {self.clutches_file}")
        #st.write(f"Current working dir: {os.getcwd()}")

        #Initialize inventory
        self.inventory = pd.DataFrame()
        # Initialize history (to store previous states for undo functionality)
        self.history = []  # Initialize the history attribute
        
        # Temporary directory for state saving
        self.temp_dir = tempfile.TemporaryDirectory()
        self.state_path = os.path.join(self.temp_dir.name, "inventory_state.csv")
        print(f"Temporary session directory created at {self.temp_dir}")


        """ #Rewrote 6-10-25 idea to remove redundancy from loading in each log
        #Loading inventory
        if self.inventory_file and self.inventory_file.exists():
            try:
                self.inventory = pd.read_csv(inventory_file)
                print(f"Loaded existing inventory from {self.inventory_file}")
            except FileNotFoundError:
                print(f"File {self.inventory_file} not found.")
                self.inventory = pd.DataFrame()
        else:
            print("No inventory file found, initializing with empty DataFrame")

        if self.euthanasia_log_file and self.euthanasia_log_file.exists():
            try:
                self.euthanasia_log = pd.read_csv(self.euthanasia_log_file).to_dict(orient="records")
            except pd.errors.EmptyDataError:
                print(f"{self.euthanasia_log_file} is empty. Initializing empty euthanasia log.")
                self.euthanasia_log = []
        else:
            self.euthanasia_log = []

        if self.clutches_file and self.clutches_file.exists():
            try:
                self.larval_clutches = pd.read_csv(clutches_file)
                print(f"Loading existing inventory from {clutches_file}")
            except pd.errors.EmptyDataError:
                print(f"{self.clutches_file} is empty. Initializing empty log.")
                self.larval_clutches = []

        if self.larval_euth_file and self.larval_euth_file.exists():
            try:
                self.larval_euth_log = pd.read_csv(larval_euth_file)
                print(f"Loading existing inventory from {larval_euth_file}")
            except pd.errors.EmptyDataError:
                print(f"{self.larval_euth_file} is empty. Initializing empty log.")
                self.larval_euth_log = []

        """   

        # **USE ABSOLUTE PATH** to load inventory file (either from GitHub or local)
        try:
            if self.inventory_file.exists():
                self.inventory = pd.read_csv(self.inventory_file)
                print(f"Loaded existing inventory from {self.inventory_file}")
            elif isinstance(self.inventory_file, str) and self.inventory_file.startswith("https://"):
                self.inventory = pd.read_csv(self.inventory_file)  # Load from GitHub URL
                print(f"Loaded inventory from {self.inventory_file}")
            else:
                print(f"File {self.inventory_file} not found.")
                self.inventory = pd.DataFrame()  # Initialize as empty DataFrame
        except FileNotFoundError as e:
            print(f"FileNotFoundError: {e}")
            self.inventory = pd.DataFrame()  # Initialize as empty DataFrame
        except Exception as e:
            print(f"Failed to load inventory: {e}")
            self.inventory = pd.DataFrame()  # Initialize as empty DataFrame
        
        # Load other files (euthanasia log, clutches, etc.) using similar logic
        self.euthanasia_log = self.load_log(self.euthanasia_log_file)
        self.larval_clutches = self.load_log(self.clutches_file)
        self.larval_euth_log = self.load_log(self.larval_euth_file)

        
        self.last_action_type = ""
        self.initials = None
        self.save_state()  # Save initial state
        
    def __repr__(self):
        return f"<Inventory with {len(self.inventory)} salamanders>"

    def __str__(self):
        return f"Inventory with {len(self.inventory)} salamanders:\n{self.inventory.head()}"

    def load_log(self, file_path):
        """Helper function to load log files (euthanasia, larval euthanasia, etc.)"""
        log_data = pd.DataFrame()  # Initialize as empty DataFrame
        try:
            if file_path.exists():
                log_data = pd.read_csv(file_path)  # Load as DataFrame
                print(f"Loaded log from {file_path}")
            elif isinstance(file_path, str) and file_path.startswith("https://"):
                log_data = pd.read_csv(file_path)  # Load from GitHub URL
                print(f"Loaded log from {file_path}")
        except Exception as e:
            print(f"Failed to load log from {file_path}: {e}")
        return log_data  # Return as DataFrame

    def save_state(self):
        """ Save the current state of the inventory and store in history. """
        self.history.append(self.inventory.copy())
        print(f"State saved: {len(self.history)} states in history at {self.history}.")  # Debugging line
        self.inventory.to_csv(self.filename, index=False)

    def undo(self):
        """ Revert to the last saved state if history exists. """
        if len(self.history) > 1:
            print(f"History before undo: {len(self.history)} states")  # Debugging line
            self.history.pop()
            print(f"History after undo: {len(self.history)} states")  # Debugging line

            #revert to previous state
            self.inventory = self.history[-1].copy()

            # Ensure last_action_type is set correctly
            print(f"Last action type: {getattr(self, 'last_action_type', 'Not Set')}")

            if hasattr(self, 'last_action_type') and self.last_action_type == "Euthanize":
                # Remove the most recent euthanasia entry, if it exists
                if not self.euthanasia_log.empty:
                    idx = self.euthanasia_log.index[-1]
                    removed = self.euthanasia_log.loc[idx]
                    self.euthanasia_log.drop(idx, inplace=True)  # Removes the last euthanasia entry
                    print(f"Removed euthanasia log entry: {removed['Animal_ID']}")
                    self.save_euthanasia_log()
                    print(f"Euthanasia log saved to {self.euthanasia_log_file}")
                    self.log_change("Undo", f"Re-added {removed['Animal_ID']} and removed euthanasia log entry")
                else:
                    print("No euth log entry to remove")
                    self.log_change("Undo", "Inventory reverted, but no euthanasia entry to remove")
            elif hasattr(self, 'last_action_type') and self.last_action_type == "Larval Euthanasia":
                if not self.larval_euth_log.empty:
                    removed = self.larval_euth_log.iloc[-1]  # Get the last clutch added
                    self.larval_euth_log = self.larval_euth_log.iloc[:-1]
                    print("Removed larval euthanasia log entry")
                    self.save_larval_euthanasia_log()
                    print(f"Euthanasia log saved to {self.larval_euth_file}")
                    self.log_change("Undo", "Removed entry from larval euthanasia log")
                else:
                    print("No larval euth entry to remove")
                    self.log_change("Undo", "State reverted, nothing really changed")
            elif hasattr(self, 'last_action_type') and self.last_action_type == "Added Clutch":
                if not self.larval_clutches.empty:
                    removed = self.larval_clutches.iloc[-1]  # Get the last clutch added
                    self.larval_clutches = self.larval_clutches.iloc[:-1] #Remove last row
                    print("Removed last batch of larvae")
                    self.save_larval_clutches()
                    print(f"Saved larval clutch log to {self.clutches_file}")
                else:
                    print("Last action was adding larvae, no clutch to remove")
                    self.log_change("Undo", "State reverted, no clutches to remove")

            else: 
                print("No actions to undo.")
                self.log_change("Undo", "Inventory reverted")

            self.save_inventory()
            print(f"Inventory saved to {self.filename}")
            print("Undo successful.")
            return True
        else:
            print("No previous state to undo.")
            return False

    def log_change(self, action, details):
        """ Log every change to a text file. 
        -action (str): what action taken
        -details (str): any relevant information to note"""
        user = self.initials if self.initials else "Unknown"
        with open("change_log.txt", "a") as f: 
        #with open("https://raw.githubusercontent.com/jamiewoych/pleuro-parser/refs/heads/main/pleuro_parser/change_log.txt", "a") as f:
            f.write(f"{pd.Timestamp.now()} - {action} by {user}: {details}\n")
        print(f"Log added: {action} by {self.initials} :{details}")


    def save_euthanasia_log(self):
        if self.euthanasia_log_file:
            df = pd.DataFrame(self.euthanasia_log)
            
            # Append new entries without duplicating existing file
            df.to_csv(self.euthanasia_log_file, index=False)
        else:
            print("Euthanasia log not found")

    def save_larval_euthanasia_log(self):
        """ Save the larval euthanasia log to the file. """
        if self.larval_euth_file:
            self.larval_euth_log.to_csv(self.larval_euth_file, index=False)
            print(f"Larval euthanasia log saved to {self.larval_euth_file}.")
        else:
            print("No file specified for larval euthanasia log. Log not saved.")

    def save_larval_clutches(self, clutches = None):
        if self.clutches_file:
            self.larval_clutches.to_csv(self.clutches_file, index = False)
            print(f"Larval batch saved to {self.clutches_file}")
        else: 
            print("No CSV file specified. Inventory not saved")

    def save_inventory(self, inventory_file = None):
        """Save the current inventory to a CSV file."""
        if self.inventory_file:
            self.inventory.to_csv(self.inventory_file, index=False)
            print(f"Inventory saved to {self.inventory_file}.")
        else:
            print("No CSV file specified. Inventory not saved.")

    def add_salamanders(self, num_salamanders, dob, species, transgenic_line, lineage, protocol, rack, tank, env_condition, sex, cohort = None, experimental_holds = None, experimental_history= None, rfid = None, terra_date = None, aqua_date = None, diet = None):
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
        - experimental_holds (str): Details if the salamanders are on experimental holds.
        - experimental_history (str): Experiments animals have undergone
        - rfid (str): RFID tag
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

        if rack in blocked_tanks and tank in blocked_tanks[rack]:
            print(f"Error: Tank {tank} on {rack} is blocked for use.")
            return
        
        # Handle empty euthanasia log by checking before performing operations
        if not hasattr(self, 'euthanasia_log') or self.euthanasia_log.empty:  # Check if euthanasia log is empty
            old_ids = pd.DataFrame()  # Initialize an empty DataFrame
        else:
            old_ids = pd.DataFrame(self.euthanasia_log)["Animal_ID"].str.extract(r"SAL_(\d+)").dropna().astype(int) # already used and in euthanasia log
        
        
        # Handle empty inventory for first time initializing
        if self.inventory.empty:
            # Initialize the inventory DataFrame with columns, no rows
            self.inventory = pd.DataFrame(columns=["Animal_ID", "Tank", "Rack", "DOB", "Cohort", "Environmental_Condition", "Sex", "Lineage", "Transgenic_Line", "Experimental_Holds", "Species", "Protocol_Number", "Experimental_History", "RFID", "Date_of_Terra", "Date_of_Reaqua", "Diet"])
        

        new_salamanders = []
        existing_ids = self.inventory["Animal_ID"].str.extract(r"SAL_(\d+)")  # Extract numeric part
        existing_ids = existing_ids.dropna().astype(int)  # Convert to int
        #old_ids = pd.DataFrame(self.euthanasia_log)["Animal_ID"].str.extract(r"SAL_(\d+)").dropna().astype(int) #already used and in euthanasia log
        all_ids = pd.concat([existing_ids, old_ids], ignore_index = True)
        next_id = all_ids.max().values[0] + 1 if not all_ids.empty else 1  # Determine next ID
        #append new animal IDs to a list
        new_animal_ids = []
    
        for _ in range(num_salamanders):
            new_id = f"SAL_{next_id:03d}"
            new_animal_ids.append(new_id)
            animal = {
                "Animal_ID": f"SAL_{next_id:03d}",
                "Tank": tank,
                "Rack": rack,
                "DOB": dob,
                "Cohort": cohort,
                "Environmental_Condition": env_condition,
                "Sex": sex,  # User can update later
                "Lineage": lineage,
                "Transgenic_Line": transgenic_line,
                "Experimental_Holds": experimental_holds,
                "Species": species,
                "Protocol_Number": protocol,
                "Experimental_History": experimental_history,  # Can be updated later
                "RFID": rfid,
                "Date_of_Terra": terra_date,
                "Date_of_Reaqua": aqua_date,
                "Diet": diet
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
        # Set the last action type to "Add"
        self.last_action_type = "Add"

        self.save_inventory()
        self.save_state()
        self.log_change("Added animals", f"{num_salamanders} animals added to {rack} in {tank}.")
    
        print(f"{new_animal_ids} salamanders added to {rack}, tank {tank}, with DOB {dob}.")
        return new_animal_ids
    
    def move_salamander(self, animal_ids, target_rack, target_tank):
        """
        Move one or multiple salamanders from their current rack to a target rack.
    
        Parameters:
        - animal_id (str): Single animal ID or list of animal IDs to move.
        - target_rack (str): The rack to move the salamanders to.
        """
        # Normalize input to a list if it's a single ID
        if isinstance(animal_ids, str):
            animal_ids = [animal_ids]

        if not self.is_valid_tank(target_rack, target_tank):
            print(f"Error: Tank '{target_tank}' is not valid for {target_rack}.")
            return

        if target_rack in blocked_tanks and target_tank in blocked_tanks[target_rack]:
            print(f"Error: Tank {target_tank} on {target_rack} is blocked for use.")
            return

    
        # Loop through each animal ID and update their rack
        for animal_id in animal_ids:
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

        # Set the last action type to "Move"
        self.last_action_type = "Move" 
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
            return False
        
        # Normalize DOD immediately
        dod_clean = self.parse_date(dod)

        # Retrieve the full animal information from the inventory allowing merge with inventory info
        animal_data = animal.iloc[0].to_dict()


        # Create the euthanasia entry by merging inventory info with euthanasia details
        euth_entry = {
            "Animal_ID": animal_id,
            "Tank": animal_data["Tank"],
            "Rack": animal_data["Rack"],
            "DOB": animal_data["DOB"],
            "Cohort": animal_data["Cohort"],
            "Environmental_Condition": animal_data["Environmental_Condition"],
            "Lineage": animal_data["Lineage"],
            "Transgenic_Line": animal_data["Transgenic_Line"],
            "Experimental_Holds": animal_data["Experimental_Holds"],
            "Species": animal_data["Species"],
            "Protocol_Number": animal_data["Protocol_Number"],
            "Experimental_History": animal_data["Experimental_History"],
            "RFID": animal_data["RFID"],
            "Date_of_Terra": animal_data["Date_of_Terra"],
            "Date_of_Reaqua": animal_data["Date_of_Reaqua"],
            "Diet": animal_data["Diet"],
            "DOD": dod_clean,
            "Weight_g": weight,
            "Sex": sex if sex and sex != "Unknown" else animal_data.get("Sex", "Unknown"),
            "Purpose": purpose,
            "Experimenter": experimenter,
            "Complications": complications

        }
    
        # Convert the euthanasia entry to a DataFrame
        euth_entry_df = pd.DataFrame([euth_entry])

        # Use pd.concat() to add the new entry to the existing euthanasia log DataFrame
        self.euthanasia_log = pd.concat([self.euthanasia_log, euth_entry_df], ignore_index=True)


        #Remove animal from inventory
        self.inventory = self.inventory[self.inventory["Animal_ID"] != animal_id]
 
        # Save euth log changes
        self.save_euthanasia_log()

        # Set the last action type to "Euthanize"
        self.last_action_type = "Euthanize"

        #update change log
        self.log_change("Euthanized", f"{animal_id} on {dod}")
        
        #save changes to inventory
        self.save_inventory()
        self.save_state()

        print(f"Animal {animal_id} euthanized and removed from inventory.")
        return True


    def log_larval_euthanasia(self, dob, dod, experimenter, num_larvae, stage, purpose, protocol, complications):
        """ Log a larval euthanasia event to the log. """
        
        # Prepare the new log entry as a dataframe
        new_entry = pd.DataFrame([{
            "DOB": dob,
            "DOD": dod,
            "Experimenter": experimenter,
            "Num_Larvae": num_larvae,
            "Stage": stage,
            "Purpose": purpose,
            "Protocol_Number": protocol,
            "Complications": complications
        }])
        
        # Concatenate the new entry to the existing log
        self.larval_euth_log = pd.concat([self.larval_euth_log, new_entry], ignore_index=True)
        
        # Save the updated log to the CSV file
        self.save_larval_euthanasia_log()
        self.log_change("Larval Euthanasia", f"{num_larvae} on {protocol}")
        self.save_state()
        self.last_action_type = "Larval Euthanasia"
        return True  # Return True to indicate success

    def add_larval_clutch(self, dob, parents, room, breeding_condition, fridging):

        #New batch of larvae
        new_batch = pd.DataFrame([{
            "DOB": dob,
            "Parents": parents,
            "Room": room,
            "Breeding_Condition": breeding_condition,
            "Fridging": fridging
        }])

        #Append new entry to inventory
        self.larval_clutches = pd.concat([self.larval_clutches, new_batch], ignore_index=True)
        print("New DOB options added, and clutch logged")

        #Save to csv
        self.save_larval_clutches()
        self.log_change("Added Clutch", f"{dob} from {parents}")
        self.save_state()
        self.last_action_type = "Added Clutch"
        return True

    def edit_salamander_info(self, animal_ids, **updates):
        """
        Editable fields for a specific salamander by Animal ID or list of IDs.

        Parameters:
        - animal_id (str): ID of the salamander to edit.
        - updates (dict): Key-value pairs of the fields to update.
          Valid keys: 'Environmental Condition', 'Sex', 'Experimental Holds',
                      'Protocol Number', 'Experimental History'
        """
        if isinstance(animal_ids, str):
            animal_ids = [animal_ids]

        valid_fields = {
            "Environmental_Condition",
            "Sex",
            "Experimental_Holds",
            "Protocol_Number",
            "Experimental_History",
            "Experimental_Holds",
            "RFID",
            "Date_of_Terra", 
            "Date_of_Reaqua", 
            "Diet", 
            "Cohort"
        }

        for animal_id in animal_ids:
            if animal_id not in self.inventory["Animal_ID"].values:
                print(f"Error: Animal_ID {animal_id} not found in inventory.")
                continue

            row_index = self.inventory[self.inventory["Animal_ID"] == animal_id].index[0]

            changes = []
            for key, value in updates.items():
                if key in valid_fields:
                    old_value = self.inventory.at[row_index, key]
                    if key == "Experimental_History" and pd.notna(old_value) and value:
                        new_value = f"{old_value}; {value}"
                    else:
                        new_value = value

                    self.inventory.at[row_index, key] = value
                    changes.append(f"{key}: {old_value} → {value}")
                else:
                    print(f"Warning: '{key}' is not a valid editable field. Skipped.")

            if changes:
                # Set the last action type to "Edit"
                self.last_action_type = "Edit"
                self.save_inventory()
                self.save_state()
                self.log_change("Edit", f"{animal_id} - " + "; ".join(changes))
                print(f"Updated {animal_id}:")
                for change in changes:
                    print(" -", change)
            else:
                print("No valid changes made.")

    def highlight_changes(self, updated_df, original_df):
        """
        Returns a styled DataFrame where cells with changed values are highlighted.

        Parameters:
        - updated_df (pd.DataFrame): The current inventory after updates.
        - original_df (pd.DataFrame): The inventory snapshot before updates.

        Returns:
        - styled DataFrame with yellow highlights on modified cells
        """
        def style_row(row):
            animal_id = row["Animal_ID"]
            original = original_df[original_df["Animal_ID"] == animal_id]
            if original.empty:
                return [""] * len(row)
            original_row = original.squeeze()
            return [
                "background-color: yellow" if str(row[col]) != str(original_row.get(col, "")) else ""
                for col in row.index
            ]

        return updated_df.style.apply(style_row, axis = 1)


    def analyze_euthanasia_log(self, start_date=None, end_date=None, group_by_experimenter=False):
        if not hasattr(self, 'euthanasia_log') or len(self.euthanasia_log) == 0:
            print("No adult euthanasia records to analyze.")
            return

        if not hasattr(self, 'larval_euth_log') or len(self.larval_euth_log) == 0:
            larval_df = pd.DataFrame(columns=["DOD", "Experimenter", "Protocol_Number", "Complications"])  # empty frame
        else:
            larval_df = pd.DataFrame(self.larval_euth_log)
            larval_df["DOD"] = pd.to_datetime(larval_df["DOD"], format="%m/%d/%Y", errors="coerce")

        #Adult euthanasia log to dataframe
        log_df = pd.DataFrame(self.euthanasia_log)
        log_df["DOD"] = pd.to_datetime(log_df["DOD"], errors="coerce")
        log_df["Complications_clean"] = log_df["Complications"].fillna("").str.strip().str.title()

        #Larval euthanasia log to dataframe
        larval_df = pd.DataFrame(self.larval_euth_log)
        larval_df["DOD"] = pd.to_datetime(larval_df["DOD"], errors="coerce")
        larval_df["Complications_clean"] = larval_df["Complications"].fillna("").str.strip().str.title()


        # Apply date filtering if specified
        if start_date:
            start_date = pd.to_datetime(start_date)
            log_df = log_df[log_df["DOD"] >= start_date]
            larval_df = larval_df[larval_df["DOD"] >= start_date]
        if end_date:
            end_date = pd.to_datetime(end_date)
            log_df = log_df[log_df["DOD"] <= end_date]
            larval_df = larval_df[larval_df["DOD"] <= end_date]

        # Handle multiple experimenters in one cell by splitting and exploding
        if group_by_experimenter:
            log_df["Experimenter"] = log_df["Experimenter"].fillna("")
            log_df["Experimenter"] = log_df["Experimenter"].str.strip().str.upper()
            log_df["Experimenter_List"] = log_df["Experimenter"].str.split(r"[,\s/]+")
            log_df = log_df.explode("Experimenter_List")
  

            # Do the same for larval euthanasia log
            larval_df["Experimenter"] = larval_df["Experimenter"].fillna("")
            larval_df["Experimenter"] = larval_df["Experimenter"].str.strip().str.upper()  # Clean and normalize
            larval_df["Experimenter_List"] = larval_df["Experimenter"].str.split(r",\s*")  # Split by commas and spaces
            larval_df = larval_df.explode("Experimenter_List")  # Create a row for each experimenter

            group_cols = ["Experimenter_List"]

        else:
            group_cols = ["Protocol_Number"]


        euth_summary = (
            log_df
            .groupby(group_cols)
            .agg(
                total_animals_euthanized=("Animal_ID",
                    lambda x: (log_df.loc[x.index, "Complications_clean"]
                           .isin(["", "Euthanized For Illness"])
                    ).sum()
                ),
                total_animals_with_surgical_complications=(
                    "Animal_ID",
                    lambda x: (log_df.loc[x.index, "Complications_clean"]
                           .eq("Surgical Complications")
                    ).sum()
                ),                
                total_animals_found_dead=(
                    "Animal_ID",
                    lambda x: (log_df.loc[x.index, "Complications_clean"]
                               .eq("Found Dead")
                    ).sum()
                ),

            )
            .reset_index()
        )


        # Grouping and aggregation for larval euthanasia log
        larval_summary = larval_df.groupby(group_cols, dropna=False).apply(
            lambda g: pd.Series({
                "total_larvae_euthanized": g.loc[g["Complications_clean"]=="", "Num_Larvae"].sum(),
                "larval_surgical_complications": g.loc[g["Complications_clean"]=="Surgical Complications", "Num_Larvae"].sum(),
                "total_larvae_found_dead": g.loc[g["Complications_clean"]=="Found Dead", "Num_Larvae"].sum()
            })
        ).reset_index(drop=False)

        # Merge both summaries into one final summary
        # summary = pd.merge(euth_summary, larval_summary, on=group_cols, how="outer")
        return euth_summary, larval_summary


    def parse_date(self, x):
        """Helper to normalize dates to YYYY-MM-DD if possible, else keep original."""
        for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y"):
            try:
                return pd.to_datetime(x, format=fmt).strftime("%Y-%m-%d")
            except (ValueError, TypeError):
                continue
        return x  # keep original if unrecognized

    def search_salamanders(self, **criteria):
        """
        Search for salamanders in the inventory based on given criteria.
    
        Parameters:
        - **criteria: Keyword arguments where keys are column names and values are search terms.
                      Supports partial matches (case-insensitive).
    
        Returns:
        - A filtered DataFrame with matching salamanders.
        """

        min_age = criteria.pop("min_age", None)
        max_age = criteria.pop("max_age", None)

        if not criteria and min_age is None and max_age is None:
            print("Please provide at least one search criterion.")
            return None

        exact_match_fields = {"Sex", "Rack", "Tank", "Protocol_Number", "Animal_ID"}  
    
        filtered_inventory = self.inventory.copy()  # Start with the full inventory
        

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

            if isinstance(value, list): #allow multiple tanks for filtering dataframe
                filtered_inventory = filtered_inventory[
                    filtered_inventory[key].astype(str).isin([str(v) for v in value])
                ]

            elif value is None or str(value).lower() in {"none", "nan", "null"}:
                # Search for missing values
                filtered_inventory = filtered_inventory[
                filtered_inventory[key].isna()
                ]
            elif key in exact_match_fields:
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

        tanks = limited_tanks if rack in limited_racks else full_tanks

        if rack in blocked_tanks:
            tanks = [t for t in tanks if t not in blocked_tanks[rack]]

        return tanks


    def plot_rack_space(self, inventory_subset=None, return_fig=False):

        # Create an empty DataFrame with all possible valid (rack, tank) combinations
        full_layout = []
        
        # Generate possible Rack/Tank pairings based on if rack is limited or full as defined in is_valid_tank()
        for rack in valid_racks:
            tanks = limited_tanks if rack in limited_racks else full_tanks
            for tank in tanks:
                full_layout.append((rack, tank))   #Appends pairings to full_layout list     

        # Generate Dataframe from full layout list, with column for count
        layout_df = pd.DataFrame(full_layout, columns=["Rack", "Tank"])
        layout_df["Count"] = 0

        # Use subset or full inventory; make a copy to safely edit tank labels
        inventory = inventory_subset.copy() if inventory_subset is not None else self.inventory.copy()


        #Count animals per tank in dataframe, reset index for simple dataframe structure
        counts = inventory.groupby(["Rack", "Tank"]).size().reset_index(name="Count")


        # Merge counts with the full layout dataframe ensuring all (rack, tank) pairs are present even if empty counts
        merged = layout_df.merge(counts, on=["Rack", "Tank"], how="left", suffixes=("", "_actual"))
        merged["Count"] = merged["Count_actual"].fillna(0).astype(int)
        merged.drop(columns=["Count_actual"], inplace=True)

        # Pivot for heatmap, sorted numerically by rack in rows, tank in columns
        pivot = merged.pivot(index="Rack", columns="Tank", values="Count").fillna(0).astype(int)
        pivot = pivot.loc[sorted(pivot.index, key=lambda x: int(x.split()[1]))]
        

        # Sort the tank columns in a consistent order A1-D6, supporting merged tanks
        sorted_tanks = sorted(pivot.columns, key=lambda x: (x[0], int(x[1:])))
        pivot = pivot[sorted_tanks]

        # Create a mask for invalid tank positions (tanks that don't exist for the rack)    
        mask = pd.DataFrame(False, index=pivot.index, columns=pivot.columns)
        for rack in pivot.index:
            valid_tanks = self.get_tanks_for_rack(rack)
            for tank in pivot.columns:
                if tank not in valid_tanks or (rack in blocked_tanks and tank in blocked_tanks[rack]):
                    mask.loc[rack, tank] = True

        # Plot with Seaborn heatmap
        fig, ax = plt.subplots(figsize=(14, 8))
        sns.heatmap(
            pivot, 
            mask=mask, #hides invalid tanks
            annot=True, 
            fmt="d", #annotations as integers
            cmap="coolwarm",  
            linewidths=0.5, 
            linecolor='gray', 
            cbar_kws={'label': 'Count'}, #label for color bar
            ax=ax
        )

        # Add darker lines between rows for easier visualization
        tank_columns = list(pivot.columns)  # Get the column names (tank identifiers)

        # Identify the boundary between sets of rows
        boundary_idx_AB = next(i for i, t in enumerate(tank_columns) if not t.startswith('A')) #first column not starting with A
        boundary_idx_BC = next(i for i, t in enumerate(tank_columns) if not t.startswith('B') and t.startswith('C'))
        boundary_idx_CD = next(i for i, t in enumerate(tank_columns) if not t.startswith('C') and t.startswith('D'))

        # Draw vertical lines between the row boundaries
        ax.vlines(boundary_idx_AB, 0, len(pivot), color='black', linewidth=2)
        ax.vlines(boundary_idx_BC, 0, len(pivot), color ='black', linewidth=2)
        ax.vlines(boundary_idx_CD, 0, len(pivot), color='black', linewidth=2)

        ax.set_title("Salamander Distribution Across Racks and Tanks", fontsize=16)
        ax.set_xlabel("Tank", fontsize=12)
        ax.set_ylabel("Rack", fontsize=12)
        plt.xticks(rotation=45)
        plt.tight_layout()

        if return_fig:
            return fig
        else:
            plt.show()


    def is_valid_tank(self, rack, tank):
        """
        Check if the provided tank is valid for the given rack based on rack_layouts.
        
        Parameters:
        - rack (str): Rack name (e.g., "Rack 1")
        - tank (str): Tank ID (e.g., "A3")

            """
        valid_racks = [
            "Rack 1", "Rack 2", "Rack 3", "Rack 4", "Rack 5",
            "Rack 6", "Rack 7", "Rack 8", "Rack 9", "Rack 10", "Rack 11", "Rack 12", "Rack 13 - Off"
        ]
        limited_racks = ["Rack 1", "Rack 3", "Rack 5", "Rack 7", "Rack 9", "Rack 10", "Rack 11", "Rack 13 - Off"]

        if rack not in valid_racks:
            return False

        limited_tanks = [f"{row}{col}" for row in "ABC" for col in range(1, 5)] #A1-C4
        full_tanks = [f"{row}{col}" for row in "ABCD" for col in range(1, 6)] #A1-D5

        valid_tanks = limited_tanks if rack in limited_racks else full_tanks
        
        blocked_tanks = { #! Can be adjusted if smaller tanks replace large tanks
            "Rack 1": ["C4"], #polypterus tank in two slots
            "Rack 3": ["A2", "A4", "B2", "C2"], #Large breeding tanks
            "Rack 10": ["C1"], #Bucket lives here
            "Rack 12": ["B2", "B3", "B5", "C2", "C3", "C5", "D2", "D3", "D5"], #Breeding tanks
            "Rack 13 - Off": ["A3", "A4","B1", "B2", "B3", "B4", "C1", "C2", "C3", "C4"] # This rack doesnt really exist - for noting which animals are off rack
        }
        #Remove blocked tanks
        if rack in blocked_tanks:
            valid_tanks = [t for t in valid_tanks if t not in blocked_tanks[rack]]

        return tank in valid_tanks


    def get_dob_options(self):
        """ Return a list of unique DOBs from the larval clutch data """
        if hasattr(self, 'larval_clutches') and not self.larval_clutches.empty:
            # Get unique DOB values from the larval clutch data
            dob_options = self.larval_clutches['DOB'].dropna().unique()
            dob_options = list(dob_options)
            return dob_options
        else:
            # If no larval clutch data is available, return None
            print("No larval clutch data available.")
            return None

    # Function to clone the repository (or pull the latest changes)
    def clone_or_pull_repo(self):
        repo_dir = "/tmp/pleuro-parser"
        token = st.secrets["GITHUB_TOKEN"]
        git_url = "https://github.com/jamiewoych/pleuro-parser.git"
        # Embed token into the URL
        authed_url = git_url.replace("https://", f"https://{token}:x-oauth-basic@")
        if not os.path.exists(repo_dir):
            # Clone the repo if it doesn't exist
            repo = git.Repo.clone_from(authed_url, repo_dir)
        else:
            # Pull the latest changes if the repo already exists
            repo = git.Repo(repo_dir)
            repo.remotes.origin.set_url(authed_url)
            repo.remotes.origin.pull()
        return repo

    def push_changes(self):
        try:
            repo = self.clone_or_pull_repo()
            repo_root = repo.working_tree_dir  # e.g. /tmp/pleuro-parser

            # 🟢 NEW: Always pull latest from GitHub before saving anything
            st.info("Pulling latest changes from GitHub before pushing...")
            repo.remotes.origin.fetch()
            repo.git.pull('origin', 'main')

            # Paths inside the repo
            files_to_push = {
                "inventory": {
                    "src": self.inventory_file,
                    "dst": os.path.join(repo_root, "salamander_inventory.csv"),
                    "save": lambda dst=os.path.join(repo_root, "salamander_inventory.csv"): self.inventory.to_csv(dst, index=False),
                },
                "euth_log": {
                    "src": self.euthanasia_log_file,
                    "dst": os.path.join(repo_root, "euthanasia_log.csv"),
                    "save": lambda dst=os.path.join(repo_root, "euthanasia_log.csv"): pd.DataFrame(self.euthanasia_log).to_csv(dst, index=False),
                },
                "state": {
                    "src": self.filename,
                    "dst": os.path.join(repo_root, "inventory_state.csv"),
                    "save": lambda dst=os.path.join(repo_root, "inventory_state.csv"): pd.read_csv(self.filename).to_csv(dst, index=False),
                },
                "clutches": {
                    "src": self.clutches_file,
                    "dst": os.path.join(repo_root, "Larval_Clutches.csv"),
                    "save": lambda dst=os.path.join(repo_root, "Larval_Clutches.csv"): self.larval_clutches.to_csv(dst, index=False),
                },
                "larval_euth": {
                    "src": self.larval_euth_file,
                    "dst": os.path.join(repo_root, "larval_euth_log.csv"),
                    "save": lambda dst=os.path.join(repo_root, "larval_euth_log.csv"): self.larval_euth_log.to_csv(dst, index=False),
                },
                "change_log": {
                    "src": "change_log.txt",
                    "dst": os.path.join(repo_root, "change_log.txt"),
                    "save": lambda dst=os.path.join(repo_root, "change_log.txt"): shutil.copy("change_log.txt", dst),

                },
            }

            # Save or copy each file into the repo
            for key, file_map in files_to_push.items():
                src = file_map["src"]
                dst = file_map["dst"]
                save_func = file_map["save"]

                if os.path.exists(src) or getattr(self, key, None) is not None:
                    save_func()
                    repo.git.add(dst)

            # 🟢 NEW: Check if there are any staged changes before committing
            if repo.is_dirty(untracked_files=True):
                commit_msg = "📦 Update salamander inventory & logs"
                repo.index.commit(commit_msg)
                repo.remotes.origin.push()
                st.success("All updated files pushed to GitHub successfully!")
            else:
                st.info("No new changes to push — repo already up to date.")
                
        except Exception as e:
            st.error(f"Error pushing changes to GitHub: {e}")

""" #old push_changes , only for updating inventory
    def push_changes(self):
        try:
            # Clone or pull the repository
            repo = self.clone_or_pull_repo()
            repo_root = repo.working_tree_dir
            
            # Write the current inventory DataFrame to CSV in the repo
            file_path = os.path.join(repo_root, "salamander_inventory.csv")
            self.inventory.to_csv(file_path, index=False)
            
            # Stage the changes
            repo.git.add(file_path)  # Add the modified files

            # Commit the changes
            repo.index.commit("Updated salamander inventory")

            # Push changes back to GitHub
            repo.remotes.origin.push()

            st.success("Changes pushed to GitHub successfully!")

        except Exception as e:
            st.error(f"Error pushing changes to GitHub: {e}")

# Old password function for streamlit-pp.py
PASSWORD = "Pleurodeles123!" #This is temporary

# Function to check password
def check_password():
    password = st.text_input("Enter password", type="password")
    initials = st.text_input("Enter initials here to login")
    if password != PASSWORD:
        st.markdown("Enter password!")
        return False
    if not initials:
        st.markdown("Initials are required to log actions")
        return False
    st.session_state.initials = initials
    return True

if not check_password():
    st.stop() #stops app if password is wrong
    st.write("Incorrect password! Access denied.")"""


            
species_list = ["Ambystoma mexicanum", "Pleurodeles waltl", "Polypterus senegalus"]
transgenic_lines = ["WT", "hsyn-GFP", "hsyn-GCaMP6s", "hsyn-GCaMP6s F1", "hsyn-Cre", "mDlx-ChR2", "mDlx-GFP"]
racks = ["Rack 1", "Rack 2", "Rack 3", "Rack 4", "Rack 5", "Rack 6", "Rack 7", "Rack 8", "Rack 9", "Rack 10", "Rack 11", "Rack 12", "Rack 13 - Off"]
protocols = ["AABF2564", "AABL1550", "AABI2617", "AABY5655"]
conditions = ["Terrestrial", "Aquatic", "Reaqua"]
sex_list = ["None", "Male", "Female"]


# Define valid racks and tank layout
valid_racks = [
        "Rack 1", "Rack 2", "Rack 3", "Rack 4", "Rack 5",
        "Rack 6", "Rack 7", "Rack 8", "Rack 9", "Rack 10", "Rack 11", "Rack 12", "Rack 13 - Off"
        ]
limited_racks = ["Rack 1", "Rack 3", "Rack 5", "Rack 7", "Rack 9", "Rack 10", "Rack 11", "Rack 13 - Off"]

limited_tanks = [f"{row}{col}" for row in "ABC" for col in range(1, 5)]   # A1–C4
full_tanks = [f"{row}{col}" for row in "ABCD" for col in range(1, 6)]     # A1–D5

#When a large tank is in the place of two tank slots 
blocked_tanks = { #! Can be adjusted if smaller tanks replace large tanks
    "Rack 1": ["C4"], #polypterus tank in two slots
    "Rack 3": ["A2", "A4", "B2", "C2"], #Large breeding tanks
    "Rack 10": ["C1"], #Bucket lives here
    "Rack 12": ["B2", "B3", "B5", "C2", "C3", "C5", "D2", "D3", "D5"],
    "Rack 13 - Off": ["A3", "A4","B1", "B2", "B3", "B4", "C1", "C2", "C3", "C4"] # This rack doesnt really exist - for noting which animals are off rack #Breeding tanks
}


if __name__ == "__main__":
    pass
