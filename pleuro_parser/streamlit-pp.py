
import io
import os 
import sys
import git
import pandas as pd
import streamlit as st
#from github import Github
from module import Rack
import matplotlib.pyplot as plt
from contextlib import contextmanager

#if str(os.getcwd()) == "/mount/src/pleuro-parser":
#      os.chdir("/mount/src/pleuro-parser")

#if str(os.getcwd()) == "/Users/jamie/hacks/pleuro-parser/pleuro_parser":
#    os.chdir("/Users/jamie/hacks/pleuro-parser")

# Initialize Rack object only once
if "rack" not in st.session_state:
    st.session_state.rack = Rack(
        inventory_file="salamander_inventory.csv",
        filename="inventory_state.csv",
        euthanasia_log_file="euthanasia_log.csv"
    )

# Use the persisted instance
R = st.session_state.rack

def ensure_initials():
    if "initials" not in st.session_state:
        st.session_state.initials = ""
    initials = st.text_input("Enter initials to login", key="initials")
    if not initials:
        st.warning("Initials are required to log actions")
        st.stop()
    return initials

#Require initials before proceeding
initials = ensure_initials()
R.initials = initials

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
            st.sidebar.markdown("### Terminal Messages")
            st.sidebar.code(logs)
        else:
            st.sidebar.markdown("### No current messages")

#Title of webapp
st.title('Tosches Lab Animal Inventory')



# Capture and display all print/warning output to sidebar
with capture_stdout_to_sidebar():
    # Sidebar setup with the Undo button
    with st.sidebar:

        #st.subheader("Working directory")
        #st.write(f"Inventory file path: {R.inventory_file}")
        #st.write(f"Current working dir: {os.getcwd()}")
        
        st.subheader("Undo Last Action")

        if st.button("Last Action to Undo"):
            if hasattr(R, 'last_action_type'):
                st.markdown(f"Click to undo {R.last_action_type}")
            else:
                st.warning("No action to undo")

        # Button to perform the undo
        if st.button("Undo Last Action"):
            success = R.undo()
            if success:
                st.success("Undo successful from sidebar.")
            else:
                st.warning("No previous state to undo")

        st.subheader("Custom Change Log Input")
        with st.expander("Write Custom Change Log Message", expanded = True):
            custom_message = st.text_area("Input", height = 100)

            if st.button("Submit Custom Message"):
                if custom_message:
                    action = "Custom Message"
                    details = custom_message
                    R.log_change(action, details)
                    st.success("Custom message logged successfully!")
                else: 
                    st.warning("Please enter a message before submitting")

        st.subheader("Save Changes")
        if st.button("Push Changes to Github"):
            action = "Pushing Changes"
            details = "Changes saved"
            R.log_change(action, details)
            R.push_changes()
            st.success("Changes saved successfully!")


    # Tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Animal Distribution", "Add Salamanders", "Euthanize Salamander", "Edit/Move Animal", "View Files", "User Guide"])

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
            animal_ids = st.multiselect("Animal IDs for search", options = R.inventory["Animal_ID"].tolist() )

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

                    if animal_ids:
                            search_kwargs["Animal_ID"] = animal_ids
                    
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
                    inventory_df = pd.read_csv(R.inventory_file)
                    st.dataframe(inventory_df, use_container_width=True)
            except Exception as e:
                    st.error(f"Could not load inventory: {e}")

    with tab2:
            st.subheader("Add Salamanders")
            # Form for adding salamanders

            num_salamanders = st.number_input("Number of Salamanders", min_value=1, value=1)
            dob_str = st.selectbox("Date of Birth for Clutches", options = R.get_dob_options())
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

                    new_animal_ids = R.add_salamanders(
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
                            diet=Diet
                    )

                    if new_animal_ids:
                        st.success(f"Added {num_salamanders} salamander(s) to {rack} {tank}.")
                        st.write("New Animal IDs:", ", ".join(new_animal_ids))  # Display the new Animal IDs
                    else:
                        st.warning("no new animals")

            st.subheader("Add Larval Clutch")

            dob = st.date_input("DOB")
            dob_str = dob.strftime("%m/%d/%Y")
            parents = st.text_input("Parents")
            room = st.selectbox("Room Born In", ["Main Room", "Behavior Room"])
            breeding_condition = st.selectbox("Breeding_Condition", ["Natural", "Induced", "Hormone Injection", "IVF"])
            fridging = st.text_input("Time Spent Fridging")

            if st.button("Add Larval Clutch"):

                    new_babies = R.add_larval_clutch(
                            dob_str,
                            parents, 
                            room, 
                            breeding_condition, 
                            fridging
                            )

                    if new_babies:
                        st.success(f"Added babies born on {dob_str} to batch select")
                    else: 
                        st.warning("no new clutches added")


    with tab3:
        st.subheader("Euthanize Salamander")

        animal_id = st.selectbox("Animal ID to Euthanize (SAL_###)", options = ["Select Animal ID"] + R.inventory["Animal_ID"].tolist(), index = 0)

        if animal_id:
            # Display the current inventory entry for the selected animal
            current_inventory_entry = R.inventory[R.inventory["Animal_ID"] == animal_id]
            if not current_inventory_entry.empty:
                st.markdown(f"**Current Inventory Entry for {animal_id}:**")
                st.dataframe(current_inventory_entry, use_container_width=True)
            else:
                st.warning(f"No inventory entry found for {animal_id}.")

        dod = st.date_input("Date of Death")
        dod = pd.to_datetime(dod)
        dod_str = dod.strftime("%m/%d/%Y") #convert to correct format for analyze_euthanasia function
        weight = st.number_input("Weight_g", min_value=0.0)
        sex = st.selectbox("Sex (optional)", ["", "Unknown", "Male", "Female"])
        purpose = st.text_input("Purpose of Euthanasia")
        experimenter = st.text_input("Experimenter (Initials - separate by comma if multiple - found dead = NA)")
        complications = st.selectbox("Complications if applicable", ["", "Found Dead", "Surgical Complications", "Euthanized for Illness"])

        if st.button("Euthanize"):
            success = R.euthanize_animal(animal_id, dod_str, weight, sex, purpose, experimenter, complications)
            if success:
                st.success(f"Animal {animal_id} euthanized and logged.")
            else:
                st.warning(f"Failure to euthanize {animal_id} Check terminal logs for more info")
            
        with st.expander("Current Euthanasia Log (in memory)"):
            st.dataframe(pd.DataFrame(R.euthanasia_log))

        with st.expander("Current Inventory (after euthanasia)"):
            st.dataframe(R.inventory)


        st.markdown("---")

        st.subheader("Euthanize Larvae")

        #Inputs
        dob = st.selectbox(
            "Select DOB from Larval Clutch",
            options=R.get_dob_options(),
            index=None,             # No option pre-selected
            placeholder="-- choose DOB --"
        ) # You can use the DOB options from the larval clutch data
        dod = st.date_input("DOD")
        dod = pd.to_datetime(dod)
        dod_str = dod.strftime("%m/%d/%Y")
        experimenter = st.text_input("Experimenter (Initials)")
        num_larvae = st.number_input("Number of Larvae", min_value=1, value=1, step=1)
        stage = st.text_input("Stage")
        purpose = st.text_input("Purpose")
        protocol = st.selectbox("Experimental Protocol", ["AABF2564", "AABL1550", "AABI2617", "AABY5655"])
        complications = st.selectbox("Complications",["", "Cannibalism", "Found Dead", "Surgical Complications"])


        if st.button("Euthanize Larvae"):
            success = R.log_larval_euthanasia(dob, dod_str, experimenter, num_larvae, stage, purpose, protocol, complications)
            if success:
                st.success(f"{num_larvae} euthanized and logged")

    with tab5:
        # Euthanasia Log
        st.subheader("Euthanasia Log")
        try:
            euth_log_df = pd.read_csv(R.euthanasia_log_file)

            st.dataframe(euth_log_df, use_container_width = True)

            # Add filter widgets
            protocols = sorted(euth_log_df["Protocol_Number"].dropna().unique())
            experimenters = sorted(euth_log_df["Experimenter"].dropna().unique())
            years = pd.to_datetime(euth_log_df["DOD"], errors="coerce").dt.year.dropna().astype(int).unique()

            selected_protocol = st.multiselect("Protocol", options=protocols, default = [])
            selected_experimenter = st.multiselect("Experimenter", options=experimenters, default = [])
            selected_year = st.multiselect("Year", options=sorted(years), default = [])

            # Apply filters
            filtered_df = euth_log_df.copy()

            if selected_protocol:
                filtered_df = filtered_df[filtered_df["Protocol_Number"].isin(selected_protocol)]

            if selected_experimenter:
                filtered_df = filtered_df[filtered_df["Experimenter"].isin(selected_experimenter)]

            if selected_year:
                filtered_df["DOD"] = pd.to_datetime(filtered_df["DOD"], errors="coerce")
                filtered_df = filtered_df[filtered_df["DOD"].dt.year.isin(selected_year)]

            st.dataframe(filtered_df, use_container_width=True)

        except Exception as e:
            st.error(f"Could not load euthanasia log: {e}")

        st.subheader("Analyze Euthanasia Log")

        # Date filters
        st.markdown("All entries analyzed unless date range specified")
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", value=None)
        with col2:
            end_date = st.date_input("End Date", value=None)

        # Convert to pandas datetime
        start_date = pd.to_datetime(start_date) if start_date else None
        end_date = pd.to_datetime(end_date) if end_date else None

        # Experimenter grouping toggle
        group_by_exp = st.checkbox("Group by Experimenter - animals under multiple initials counted for both individuals", value=False)


        if st.button("Run Analysis"):
            try:
                    summary_df = R.analyze_euthanasia_log(
                            start_date=start_date,
                            end_date=end_date,
                            group_by_experimenter=group_by_exp
                    )

                    if summary_df is not None and not summary_df.empty:
                        st.write("Animals Euthanized for Date Range")
                        st.dataframe(summary_df, use_container_width=True)

                    else:
                            st.info("No euthanasia data matched the selected filters.")


            except Exception as e:
                    st.error(f"Analysis failed: {e}")

        st.subheader("Larval Euthanasia Log")
        try:
            larval_euth_log = pd.read_csv(R.larval_euth_file)
            st.dataframe(larval_euth_log, use_container_width=True)
        except Exception as e:
            st.error(f"Could not load log: {e}")


        # Inventory
        st.subheader("Current Inventory")
        try:
            inventory_df = pd.read_csv(R.inventory_file)
            st.dataframe(inventory_df, use_container_width=True)
        except Exception as e:
            st.error(f"Could not load inventory: {e}")

        # Inventory State File
        st.subheader("Last Saved Inventory State")
        try:
            state_df = pd.read_csv(R.filename)
            st.dataframe(state_df, use_container_width=True)
        except Exception as e:
            st.error(f"Could not load inventory state: {e}")

        # Optional: Change log as text
        st.subheader("Change Log")
        with st.expander("View Change Log", expanded=False):
                try:
                    with open("change_log.txt", "r") as f:
                        log_content = f.read()
                        reversed_log = '\n'.join(reversed(log_content.splitlines()))
                        st.text_area("Change Log Contents", value=reversed_log, height=300, disabled=True)
                except FileNotFoundError:
                    st.info("No change log found.")

        #Clutches
        st.subheader("Clutches")
        try:
            larval_info = pd.read_csv(R.clutches_file)
            st.dataframe(larval_info, use_container_width=True)
        except Exception as e:
            st.error(f"Could not load info: {e}")


    with tab4:

            st.subheader("Move Animals")
            move_id = st.multiselect("Animal ID to Move (SAL_###)", options = R.inventory["Animal_ID"].tolist())

            if animal_ids:
                st.markdown("**Current Metadata for Selected Animals:**")
                current_rows = R.inventory[R.inventory["Animal_ID"].isin(move_id)]
                st.dataframe(current_rows, use_container_width=True)

            target_rack = st.selectbox("Target Rack", [
                    "Rack 1", "Rack 2", "Rack 3", "Rack 4", "Rack 5", "Rack 6", "Rack 7", "Rack 8", "Rack 9", "Rack 10", "Rack 11", "Rack 12", "Rack 13 - Off"])
            # Use get_tanks_for_rack method to generate valid tanks
            valid_tanks = R.get_tanks_for_rack(target_rack)
            target_tank = st.selectbox("Valid Tanks for Selected Rack", options=valid_tanks)

            if st.button("Move Salamanders"):
                    if move_id and target_rack and target_tank:
                            R.move_salamander(move_id, target_rack, target_tank)
                            st.success(f"Moved {move_id} to {target_rack} {target_tank}")
                            
                            st.markdown("**Metadata for Animals Moved:**")
                            current_rows = R.inventory[R.inventory["Animal_ID"].isin(move_id)]
                            st.dataframe(current_rows, use_container_width=True)

                    else:
                            st.warning("Please provide Animal ID, target rack, and tank.")

            st.markdown("---")

            st.subheader("Edit Metadata")
            animal_ids = st.multiselect("Animal ID to edit (SAL_###)", options = R.inventory["Animal_ID"].tolist())

            if animal_ids:
                st.markdown("**Current Metadata for Selected Animals:**")
                current_rows = R.inventory[R.inventory["Animal_ID"].isin(animal_ids)]
                st.dataframe(current_rows, use_container_width=True)

                edit_fields = {
                "Environmental_Condition": st.selectbox("Environmental Condition Change", ["", "Aquatic", "Terrestrial", "Reaqua"]),
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
                    st.warning("No edits applied")


    with tab6:  # User Guide tab
        st.markdown("""
        ## Tosches Inventory User Guide! 
        Updated: May 12 2025 JW

        ### Important Notes
            - Changes need to be Saved in the Sidebar in order for it to be 
              reflected in inventory
            - CHECK PROTOCOL animal is listed under before euthanizing. 
              This can be changed under "Edit Metadata" before logging 
              to log under correct protocol if necessary.

        ### Sidebar
            Rebooting app will reset all changes not pushed to save
            Within each session, actions that can be undone:  
            - Edit  
            - Move  
            - Add  
            - Euthanize  
            - Larval Euthanasia  
            - Added Clutch  

            This works by saving history 'states'-  
            The number of states saved will be printed at the bottom of the sidebar
             after undo  
            To ensure you're undoing the correct action, the "Last Action to Undo" 
             button prints the last action  
            Undone actions cannot be redone (except manually)  

            Undoing an "Add" Function will remove the last input from the inventory  
            Undoing a "Euthanize" Function will remove the euthanasia entry 
             and return the animal to the inventory  
            All actions record a "Change Log" that is timestamped with the action  
            Record custom logs to yourself or admin by typing in the message box  


        ### 1. Animal Distribution:
            Search by one or multiple parameters  
            Leaving the field blank will exclude the search parameter  
            Dropdown menus are provided for parameters with exact matches required  
            Other fields allow partial matches and are case insensitive  
            Age parameters allow for floats (ie 1.5)  
            When searching by Rack, Tank dropdown automatically populates the tanks 
             that exist on given rack  
            Multiple tanks can be chosen  
            Darker lines on plot correspond to row change  


        ### 2. Add Salamanders:
        ##### Add Salamanders  
            This is useful for the first time an animal or group of animals is added 
             to the rack.  
            At this point, the animals are assigned a Protocol number, and a Tank  
            Date of Birth is allowed only for those clutches that have had breeding 
             details recorded  
            Required fields are autofilled so they cannot be left blank  
            Please include initials under experimental holds if applicable   

        ##### Add Larval Clutch  
            This field is for recording breeding events  
            If the desired date of birth is not available in the dropdown above, 
             please add details of the breeding event and it will populate the dropdown  


        ### 3. Euthanize Salamander:
        ##### Euthanize Salamander  
            All animals on the rack are entered on this log - even if they are larvae
            One Animal_ID can be euthanized at a time to encourage input of individual metadata  
            Additional Notes and details can be included in Purpose  
            Animals with IDs are preassigned Protocols  
                - please make sure your animal is on the right protocol!  
                - Edit BEFORE euthanasia for a protocol transfer for proper record keeping
            Relevant information will carry over from the Inventory file  
            Initials split by a comma will allow splitting by experimenter  

        ##### Euthanize Larvae  
            Larvae that are still on the shelf are logged here - they do not have animal IDs
            Multiple larvae can be recorded  
            These animals are not preassigned protocol numbers, this is a required field  
            Additional notes can be recorded under Purpose  

        ### 4. Edit/Move Animal:
        ##### Edit Metadata
            Multiple animals can be edited at the same time  
            The current metadata is printed, for ease of verifying the correct animals are chosen  
            Please note that Terrestrial animals, and animals on Rack 8 are on a Gummy diet (May 2025)  
            ** Holds will repopulate this field   
                - please check the animals you are holding are not already being held  
                - please include initials so animals you have on hold can be easily searched  

            Experimental history will append to existing history  

        ##### Move Animals
            Multiple animals can be moved at a time, but only to the same tank  
            Only tanks that exist will appear in the dropdown  
            Rack 13 Tank 1 is a holding place for animals off the racks that have not been euthanized  

        ### 5. View Files:
            Preview all files and logged changes to the inventory  

        ##### Analyze Euthanasia Log:  
            Analyzes entire inventory unless date range specified   
            Complications include animals found dead or surgical complications  
            Only protocols with entries in the date range will appear in the analysis table   


        Feel free to ask questions and give recommendations for things that can be optimized!  
        
        ### Notes: 
        - The data is saved automatically to CSV files, so you don't need to worry about manually saving any changes.  
        - Ensure all inputs are valid, especially when specifying dates and numerical values.  
 
        Happy parsing! - Jamie
        """)
