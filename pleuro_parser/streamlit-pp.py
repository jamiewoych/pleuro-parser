
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

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["Animal Distribution", "Add Salamanders", "Euthanize Salamander", "View Files"])

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
                if isinstance(results, pd.DataFrame): #check if search results in dataframe
                        st.subheader("Search Results")
                        st.dataframe(results, use_container_width=True)

                        st.subheader("Rack Plot of Filtered Results")
                        fig = R.plot_rack_space(inventory_subset=results, return_fig=True)
                        st.pyplot(fig)

                        # Optionally store in session state
                        st.session_state["search_results"] = results

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
        dob_str = st.text_input("Date of Birth (YYYY/MM/DD)")
        species = st.text_input("Species", value="Pleurodeles waltl")
        transgenic_line = st.selectbox("Transgenic Line", ["WT", "hsyn-GFP", "hsyn-GCaMP6s", "mDlx-GFP", "mDlx-ChR2", "hsyn-Cre"])
        lineage = st.text_input("Lineage")
        protocol = st.selectbox("Protocol Number", ["AABL1550", "AABF2564", "AABI2617", "AABY5655"])
        rack = st.selectbox("Rack", options=[
                "Rack 1", "Rack 2", "Rack 3", "Rack 4", "Rack 5",
                "Rack 6", "Rack 7", "Rack 8", "Rack 9", "Rack 10", "Rack 11", "Rack 12"
            ])
        tank = st.text_input("Tank (e.g., A1, B2, etc.)*")
        env_condition = st.text_input("Environmental_Condition", value="Aquatic")
        sex = st.selectbox("Sex", options=["Unknown", "Male", "Female"])
        experimental_holds = st.text_input("Experimental_Holds - Defaults None")
        experimental_history = st.text_input("Experimental_History - Defaults None")
        RFID = st.text_input("RFID - defaults None")
        Diet = st.selectbox("Diet", ["", "MWF Schedule", "Daily", "Gummy Schedule"])
        terra_date_str = st.text_input("Date of Terrestrialization (YYYY-MM-DD, optional)")
        reaqua_date_str = st.text_input("Date of Reaquatic Transition (YYYY-MM-DD, optional)")

        if st.button("Add Salamanders"):
                try:
                        dob = pd.to_datetime(dob_str) if dob_str else None
                        terra_date = pd.to_datetime(terra_date_str) if terra_date_str else None
                        aqua_date = pd.to_datetime(reaqua_date_str) if reaqua_date_str else None
                except ValueError:
                        st.warning("Invalid Date format. Please use YYYY-MM-DD.")
                        st.stop()

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

    animal_id = st.text_input("Animal ID to Euthanize (SAL_###)")
    dod = st.date_input("Date of Death").isoformat()
    weight = st.number_input("Weight_g", min_value=0.0)
    sex = st.selectbox("Sex (optional)", ["Unknown", "Male", "Female"])
    purpose = st.text_input("Purpose of Euthanasia")
    experimenter = st.text_input("Experimenter (Initials)")
    complications = st.selectbox("Complications", ["", "Found Dead", "Surgical Complications"])

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

with tab4:
    st.header("Preview Files")

    # Euthanasia Log
    st.subheader("Euthanasia Log")
    try:
        euth_log_df = pd.read_csv("euthanasia_log.csv")
        st.dataframe(euth_log_df, use_container_width=True)
    except Exception as e:
        st.error(f"Could not load euthanasia log: {e}")

    st.subheader("Analyze Euthanasia Log")
    if st.button("Run Analysis"):
        try:
                summary_df = R.analyze_euthanasia_log()
                if summary_df is not None:
                    st.write("Animals Euthanized per Protocol per Year")
                    st.dataframe(summary_df, use_container_width=True)

        except Exception as e:
                st.error(f"Analysis failed: {e}")

    # Inventory
    st.subheader("Current Inventory")
    try:
        inventory_df = pd.read_csv("salamander_inventory.csv")
        st.dataframe(inventory_df, use_container_width=True)
    except Exception as e:
        st.error(f"Could not load inventory: {e}")

    # Inventory State File
    st.subheader("Last Saved Inventory State")
    try:
        state_df = pd.read_csv("inventory_state.csv")
        st.dataframe(state_df, use_container_width=True)
    except Exception as e:
        st.error(f"Could not load inventory state: {e}")

    # Optional: Change log as text
    st.subheader("Change Log")
    with st.expander("View Change Log", expanded=False):
            try:
                with open("change_log.txt", "r") as f:
                    log_content = f.read()
                    st.text_area("Change Log Contents", value=log_content, height=300, disabled=True)
            except FileNotFoundError:
                st.info("No change log found.")




