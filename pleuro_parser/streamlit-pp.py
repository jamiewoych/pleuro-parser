
import io
import sys
import pandas as pd
import streamlit as st
from module import Rack
import matplotlib.pyplot as plt
from contextlib import contextmanager


@contextmanager
def capture_stdout_to_sidebar():
    buffer = io.StringIO()
    original_stdout = sys.stdout
    sys.stdout = buffer
    try:
        yield
    finally:
        sys.stdout = original_stdout
        logs = buffer.getvalue()
        if logs.strip():
            st.sidebar.markdown("### ⚠️ Warnings & Logs")
            st.sidebar.code(logs)
        else:
            st.sidebar.markdown("### ✅ No warnings")

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


# Capture and display all print/warning output to sidebar
with capture_stdout_to_sidebar():

    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Animal Distribution", "Add Salamanders", "Euthanize Salamander", "View Files", "Edit/Move Animal"])

    with tab1:

            if st.button("Plot All Racks"):
                    fig = R.plot_rack_space(return_fig=True)
                    st.pyplot(fig)


            #search and plot tank distribution
            st.subheader("Animal Search")
            species = st.selectbox("Species", ["", "Pleurodeles waltl", "Axolotl mexicanum", "Polypterus senegalus" ])
            sex = st.selectbox("Sex", ["", "Male", "Female", "Unknown"])
            transgenic_line = st.selectbox("Transgenic_Line", ["", "WT", "hsyn-GFP", "hsyn-GCaMP6s", "mDlx-GFP", "mDlx-ChR2", "hsyn-Cre"])
            cohort = st.text_input("Cohort, ex. Terra A, EdU, Viral, F0")
            min_age = st.text_input("Minimum Age in years")
            max_age = st.text_input("Maximum Age in years")
            protocol = st.selectbox("Protocol_Number", ["", "AABL1550", "AABF2564", "AABI2617", "AABY5655"])
            experimental_holds = st.text_input("Experimental_Holds - Priority to Use, None, or Initials")
            environmental_condition = st.selectbox("Condition", ["", "Aquatic", "Terrestrial", "Reaqua"])
            rack = st.selectbox("Rack", ["", "Rack 1", "Rack 2", "Rack 3", "Rack 4", "Rack 5", "Rack 6", "Rack 7", "Rack 8", "Rack 9", "Rack 10", "Rack 11", "Rack 12", "Rack 13 - Off"])
            valid_tanks = R.get_tanks_for_rack(rack)
            tank = st.multiselect("Tank", options=valid_tanks)

            if st.button("Search"):
                    search_kwargs = {}
                    if species:
                            search_kwargs["Species"] = species
                    if sex:
                            search_kwargs["Sex"] = sex

                    if transgenic_line:
                            search_kwargs["Transgenic_Line"] = transgenic_line

                    if cohort:
                        search_kwargs["Cohort"] = cohort

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

                    if tank:
                            search_kwargs["Tank"] = tank

                    if environmental_condition:
                            search_kwargs["Environmental_Condition"] = environmental_condition
                    
                    results = R.search_salamanders(**search_kwargs)
                    if isinstance(results, pd.DataFrame): #check if search results in dataframe
                            st.subheader("Search Results")
                            st.dataframe(results, use_container_width=True)

                            #Summary counts
                            total_animals = len(R.inventory)
                            filtered_animals = len(results)
                            st.markdown(f"**Filtered Animals:** {filtered_animals} out of {total_animals} total animals in inventory")

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

            # Inventory
            st.subheader("Current Inventory")
            try:
                    inventory_df = pd.read_csv("salamander_inventory.csv")
                    st.dataframe(inventory_df, use_container_width=True)
            except Exception as e:
                    st.error(f"Could not load inventory: {e}")

    with tab2:
            st.subheader("Add Salamanders")
            # Form for adding salamanders

            num_salamanders = st.number_input("Number of Salamanders", min_value=1, value=1)
            dob_str = st.text_input("Date of Birth (YYYY/MM/DD)")
            cohort = st.text_input("Cohort ie. Terra A, EdU, Viral")
            species = st.selectbox("Species -", ["Pleurodeles waltl", "Axolotl mexicanum", "Polypterus senegalus"])
            transgenic_line = st.selectbox("Transgenic Line", ["WT", "hsyn-GFP", "hsyn-GCaMP6s", "mDlx-GFP", "mDlx-ChR2", "hsyn-Cre"])
            lineage = st.text_input("Lineage")
            protocol = st.selectbox("Protocol Number", ["AABL1550", "AABF2564", "AABI2617", "AABY5655"])
            rack = st.selectbox("Rack", options=[
                    "Rack 1", "Rack 2", "Rack 3", "Rack 4", "Rack 5",
                    "Rack 6", "Rack 7", "Rack 8", "Rack 9", "Rack 10", "Rack 11", "Rack 12", "Rack 13 - Off"
                ])
            # Use get_tanks_for_rack method to generate valid tanks
            valid_tanks = R.get_tanks_for_rack(rack)
            tank = st.selectbox("Available Tanks for Selected Rack", options=valid_tanks)
            #tank = st.text_input("Tank (e.g., A1, B2, etc.)*")
            env_condition = st.selectbox("Environmental_Condition", ["Aquatic", "Terrestrial", "Reaqua"])
            sex = st.selectbox("Sex", options=["Unknown", "Male", "Female"])
            experimental_holds = st.text_input("Experimental_Holds - Include Initials - Defaults None")
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
                            cohort = cohort, 
                            experimental_holds=experimental_holds, 
                            experimental_history=experimental_history, 
                            rfid=RFID, 
                            terra_date=terra_date, 
                            aqua_date=aqua_date, 
                            diet=Diet)
                    st.success(f"Added {num_salamanders} salamander(s) to {rack} {tank}.")

    with tab3:
        st.subheader("Euthanize Salamander/Undo")

        animal_id = st.text_input("Animal ID to Euthanize (SAL_###)")
        dod = st.date_input("Date of Death").isoformat()
        weight = st.number_input("Weight_g", min_value=0.0)
        sex = st.selectbox("Sex (optional)", ["Unknown", "Male", "Female"])
        purpose = st.text_input("Purpose of Euthanasia")
        experimenter = st.text_input("Experimenter (Initials - separate by comma if multiple)")
        complications = st.selectbox("Complications if applicable", ["", "Found Dead", "Surgical Complications"])

        if st.button("Euthanize"):
            success = R.euthanize_animal(animal_id, dod, weight, sex, purpose, experimenter, complications)
            if success:
                st.success(f"Animal {animal_id} euthanized and logged.")
            else:
                st.warning(f"Failure to euthanize {animal_id} Check terminal logs for more info")

        if st.button("Undo Last Action"):
            success = R.undo()
            if success:
                st.success("Undo successful from webapp.")
            else:
                st.warning("No previous state to undo")
            
        with st.expander("Current Euthanasia Log (in memory)"):
            st.dataframe(pd.DataFrame(R.euthanasia_log))

        with st.expander("Current Inventory (after euthanasia)"):
            st.dataframe(R.inventory)

    with tab4:
        # Euthanasia Log
        st.subheader("Euthanasia Log")
        try:
            euth_log_df = pd.read_csv("euthanasia_log.csv")

            # Add filter widgets
            protocols = sorted(euth_log_df["Protocol_Number"].dropna().unique())
            experimenters = sorted(euth_log_df["Experimenter"].dropna().unique())
            years = pd.to_datetime(euth_log_df["DOD"], errors="coerce").dt.year.dropna().astype(int).unique()

            selected_protocol = st.selectbox("Protocol", options=["All"] + list(protocols))
            selected_experimenter = st.selectbox("Experimenter", options=["All"] + list(experimenters))
            selected_year = st.selectbox("Year", options=["All"] + sorted(years))

            # Apply filters
            filtered_df = euth_log_df.copy()

            if selected_protocol != "All":
                filtered_df = filtered_df[filtered_df["Protocol_Number"] == selected_protocol]

            if selected_experimenter != "All":
                filtered_df = filtered_df[filtered_df["Experimenter"] == selected_experimenter]

            if selected_year != "All":
                filtered_df["DOD"] = pd.to_datetime(filtered_df["DOD"], errors="coerce")
                filtered_df = filtered_df[filtered_df["DOD"].dt.year == selected_year]

            st.dataframe(filtered_df, use_container_width=True)

        except Exception as e:
            st.error(f"Could not load euthanasia log: {e}")

        st.subheader("Analyze Euthanasia Log")

        # Date filters
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", value=None)
        with col2:
            end_date = st.date_input("End Date", value=None)

        # Experimenter grouping toggle
        group_by_exp = st.checkbox("Group by Experimenter (handles multiple initials)", value=False)


        if st.button("Run Analysis"):
            try:
                    summary_df = R.analyze_euthanasia_log(
                            start_date=start_date if start_date else None,
                            end_date=end_date if end_date else None,
                            group_by_experimenter=group_by_exp
                    )

                    if summary_df is not None and not summary_df.empty:
                        st.write("Animals Euthanized for Date Range")
                        st.dataframe(summary_df, use_container_width=True)

                    else:
                            st.info("No euthanasia data matched the selected filters.")


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


    with tab5:
            st.subheader("Edit Metadata")
            animal_ids = st.multiselect("Animal ID to edit (SAL_###)", options = R.inventory["Animal_ID"].tolist())

            if animal_ids:
                st.markdown("**Current Metadata for Selected Animals:**")
                current_rows = R.inventory[R.inventory["Animal_ID"].isin(animal_ids)]
                st.dataframe(current_rows, use_container_width=True)

                edit_fields = {
                "Environmental_Condition": st.selectbox("Environmental Condition Change", ["Aquatic", "Terrestrial", "Reaqua"]),
                "Sex": st.selectbox("Sex", ["", "Female", "Male", "Unknown"]),
                "Experimental_Holds": st.text_input("Holds: Initials with Details, or Breeding - Please Check if Current Holds"),
                "Protocol_Number": st.selectbox("Protocol Transfer", ["", "AABL1550", "AABF2564", "AABI2617", "AABY5655"]),
                "Experimental_History": st.text_area("Experimental History"), 
                "RFID": st.text_input("RFID"),
                "Diet": st.selectbox("Diet Change", ["", "MWF Schedule", "Daily", "Gummy Schedule"]), 
                "Cohort": st.text_input("Cohort, ie. Terra A")
                }
                            
                # Optional terra/aqua dates
                col1, col2 = st.columns(2)
                terra_date = col1.date_input("Date of Terrestrialization (optional)", value=None)
                aqua_date = col2.date_input("Date of Reaqua (optional)", value=None)


                if st.button("Apply Edits"):
                    updates = {k: v for k, v in edit_fields.items() if v}

                    if terra_date:
                        updates["Date_of_Terra"] = str(terra_date)
                    if aqua_date:
                        updates["Date_of_Reaqua"] = str(aqua_date)

                    if updates: #Ensure not updating on empty updates
                        R.edit_salamander_info(animal_ids, **updates)
                        st.success(f"Updated metadata for {len(animal_ids)} animal(s).")
                        st.markdown("**Updated Metadata:**")
                        updated_rows = R.inventory[R.inventory["Animal_ID"].isin(animal_ids)]
                        styled_df = R.highlight_changes(updated_rows, current_rows)
                        st.dataframe(styled_df, use_container_width=True)
                    else: 
                        st.warning("No changes specified")

                elif animal_id:
                    st.warning("Animal ID not found in inventory")

            st.markdown("---")

            st.subheader("Move Animals")
            move_id = st.multiselect("Animal ID to Move (SAL_###)", options = R.inventory["Animal_ID"].tolist())
            target_rack = st.selectbox("Target Rack", [
                    "Rack 1", "Rack 2", "Rack 3", "Rack 4", "Rack 5", "Rack 6", "Rack 7", "Rack 8", "Rack 9", "Rack 10", "Rack 11", "Rack 12", "Rack 13 - Off"])
            # Use get_tanks_for_rack method to generate valid tanks
            valid_tanks = R.get_tanks_for_rack(target_rack)
            target_tank = st.selectbox("Valid Tanks for Selected Rack", options=valid_tanks)

            if st.button("Move Salamanders"):
                    if move_id and target_rack and target_tank:
                            R.move_salamander(move_id, target_rack, target_tank)
                            st.success(f"Moved {move_id} to {target_rack} {target_tank}")

                    else:
                            st.warning("Please provide Animal ID, target rack, and tank.")



