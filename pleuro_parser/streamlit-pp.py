
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time # <- We'll need this later as well

from module import Rack

#Title of webapp
st.title('Pleurodeles Parsing')

# Initialize Rack object only once
if "rack" not in st.session_state:
    st.session_state.rack = Rack(
        inventory_file="salamander_inventory.csv",
        filename="inventory_state.csv",
        euthanasia_log_file="euthanasia_log.csv"
    )

# Use the persisted instance
R = st.session_state.rack


#st.write


# Tabs
tab1, tab2, tab3 = st.tabs(["Animal Distribution", "Add Salamanders", "Euthanize Salamander"])

with tab1:
        #search and plot tank distribution
        st.subheader("Animal Search")
        species = st.selectbox("Species", ["", "Pleurodeles waltl", "Axolotl mexicanum", "Polypterus senegalus" ])
        sex = st.selectbox("Sex", ["", "Male", "Female", "Unknown"])
        transgenic_line = st.selectbox("Transgenic_Line", ["", "WT", "hsyn-GFP", "hsyn-GCaMP6s", "mDlx-GFP", "mDlx-ChR2", "hsyn-Cre"])
        min_age = st.text_input("Minimum Age in years")
        max_age = st.text_input("Maximum Age in years")
        protocol = st.selectbox("Protocol_Number", ["", "AABL1550", "AABF2564", "AABI2617", "AABY5655"])
        experimental_holds = st.text_input("Experimental_Holds - None if None")
        environmental_condition = st.selectbox("Condition", ["", "Aquatic", "Terrestrial", "Reaqua"])
        rack = st.selectbox("Rack", ["", "Rack 1", "Rack 2", "Rack 3", "Rack 4", "Rack 5", "Rack 6", "Rack 7", "Rack 8", "Rack 9", "Rack 10", "Rack 11", "Rack 12"])
        #tank = st.selectbox("Tank", [full_tanks])

        # Optionally filter before plotting
        if st.button("Plot All Racks"):
                fig = R.plot_rack_space(return_fig=True)
                st.pyplot(fig)

        if st.button("Search"):
                search_kwargs = {}
                if species:
                        search_kwargs["Species"] = species
                if sex:
                        search_kwargs["Sex"] = sex

                if transgenic_line:
                        search_kwargs["Transgenic_Line"] = transgenic_line

                if protocol:
                        search_kwargs["Protocol_Number"] = protocol

                if min_age:
                    try:
                        search_kwargs["min_age"] = float(min_age)
                    except ValueError:
                        st.warning("Minimum age must be a number.")

                if max_age:
                    try:
                        search_kwargs["max_age"] = float(max_age)
                    except ValueError:
                        st.warning("Maximum age must be a number.")

                if experimental_holds.strip().lower() == "none":
                    search_kwargs["Experimental_Holds"] = "none"
                elif experimental_holds.strip():
                    search_kwargs["Experimental_Holds"] = experimental_holds.strip()

                if rack:
                        search_kwargs["Rack"] = rack

                if environmental_condition:
                        search_kwargs["Environmental_Condition"] = environmental_condition

                results = R.search_salamanders(**search_kwargs)
                if isinstance(results, pd.DataFrame):
                    st.session_state["search_results"] = results
                    st.dataframe(results)
                else:
                        st.warning(results)
                        st.session_state["search_results"] = None

        if st.button("Plot Filtered Results"):
                results = st.session_state.get("search_results")
                if isinstance(results, pd.DataFrame):
                        fig = R.plot_rack_space(inventory_subset=results, return_fig=True)
                        st.pyplot(fig)
                else:
                        st.warning("Please run a search first")

with tab2:
        st.subheader("Add Salamanders")
        # Form for adding salamanders

        num_salamanders = st.number_input("Number of Salamanders", min_value=1, value=1)
        dob = st.date_input("Date of Birth")
        species = st.text_input("Species", value="Pleurodeles waltl")
        transgenic_line = st.selectbox("Transgenic Line", ["WT", "hsyn-GFP", "hsyn-GCaMP6s", "mDlx-GFP", "mDlx-ChR2", "hsyn-Cre"])
        lineage = st.text_input("Lineage")
        protocol = st.selectbox("Protocol Number", ["AABL1550", "AABF2564", "AABI2617", "AABY5655"])
        rack = st.selectbox("Rack", options=[
                "Rack 1", "Rack 2", "Rack 3", "Rack 4", "Rack 5",
                "Rack 6", "Rack 7", "Rack 8", "Rack 9", "Rack 10", "Rack 11", "Rack 12"
            ])
        tank = st.text_input("Tank (e.g., A1, B2, etc.)")
        env_condition = st.text_input("Environmental_Condition", value="Aquatic")
        sex = st.selectbox("Sex", options=["Unknown", "Male", "Female"])
        experimental_holds = st.text_input("Experimental_Holds - Defaults None")
        experimental_history = st.text_input("Experimental_History - Defaults None")
        RFID = st.text_input("RFID - defaults None")
        terra_date = st.date_input("Date of Terra")
        reaqua_date = st.date_input("Date of Reaqua")
        Diet = st.selectbox("Diet", ["MWF Schedule", "Daily", "Gummy Schedule"])
        if st.button("Add Salamanders"):
                R.add_salamanders(
                        num_salamanders,
                        dob,
                        species,
                        transgenic_line,
                        lineage,
                        protocol,
                        rack, 
                        tank, 
                        env_condition, 
                        sex, 
                        experimental_holds=experimental_holds, 
                        experimental_history=experimental_history, 
                        rfid=RFID, 
                        terra_date=terra_date, 
                        aqua_date=reaqua_date, 
                        diet=Diet)
                st.success(f"Added {num_salamanders} salamander(s) to {rack} {tank}.")

with tab3:
    st.header("Euthanize Salamander")

    animal_id = st.text_input("Animal ID to Euthanize")
    dod = st.date_input("Date of Death").isoformat()
    weight = st.number_input("Weight_g", min_value=0.0)
    sex = st.selectbox("Sex (optional)", ["Unknown", "Male", "Female"])
    purpose = st.text_input("Purpose of Euthanasia")
    experimenter = st.text_input("Experimenter")
    complications = st.text_area("Complications (if any)", value="None")

    if st.button("Euthanize"):
        R.euthanize_animal(animal_id, dod, weight, sex, purpose, experimenter, complications)
        st.success(f"Animal {animal_id} euthanized and logged.")

    if st.button("Undo Last Action"):
        R.undo()
        st.success("Undo successful from webapp.")
        
    with st.expander("Current Euthanasia Log (in memory)"):
        st.dataframe(pd.DataFrame(R.euthanasia_log))

    with st.expander("Current Inventory (after euthanasia)"):
        st.dataframe(R.inventory)





