
import streamlit as st
import pandas as pd
import numpy as np
import time # <- We'll need this later as well

from module import Rack

st.title('Pleurodeles Parsing')
R = Rack(inventory_file = "salamander_inventory.csv", filename = "current.csv", csv_file = "update.csv")

R.add_salamanders(5, '2022-05-22', "Pleurodeles waltl", "GCaMP", "PxO", "AABL1550", "Rack 3", "A5", "Aqua", "Unknown", "False", "Edu")
st.write
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