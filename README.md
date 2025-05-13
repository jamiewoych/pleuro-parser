# Pleuro_Parser


##  Spreadsheet parsing tool for manipulating metadata of salamander inventory 

This project was chosen for ease of tracking movement, experimental history, and euthanasia of animals. 
The Streamlit based webapp provides function for the following tasks

- Add new animals to inventory
- Move salamanders between racks and tanks
- Visualize animal distribution across tanks and racks with a heatmap
- Search for animals of interest, and plot search results on heatmap
- View and edit animal metadata, which is retained in the euthanasia log
- View and analyze the euthanasia log

## Features

- **Add Salamanders**: Add one or multiple salamanders to the inventory with their metadata (e.g. rack, tank, DOB, protocol number).
- **Move Salamanders**: Move salamanders between racks and tanks, updating their locations in the inventory.
- **Euthanize Salamanders**: Euthanize salamanders and log their details (e.g., date of death, purpose, experimenter).
- **Search Salamanders**: Search the salamander inventory based on various criteria such as species, age, rack, tank, environmental condition, etc.
- **Euthanasia Log Analysis**: Analyze euthanasia logs by filtering by date, experimenter, or protocol 
- **Plot Rack Space**: Visualize the distribution of salamanders across racks and tanks using a heatmap.
- **Undo**: restore previous state before changes made to invenotry
- **Change log**: automatically reports time, date, and change made



### Installation

#### Packages
- io: used for displaying stdout in sidebar panel. Useful for troubleshooting
- sys: also used for redirecting stdout to sidebar panel. Useful for troubleshooting
- contextlib.contextmanager: sidebar panel usage again. Used for troubleshooting
- pandas: Used for reading and manipulating CSV files (inventory, euthanasia_log)
- streamlit: Needed to create webapp interface
- matplotlib.pyplot: Needed for heatmap visualization
- os: used for handling absolute file paths, and checking if files exist
- tempfile: used to temporarily store history to enable undo 
- seaborn: used for plotting heatmap
- pathlib.Path: used to resolve file path
- datetime, timedelta: calculating age and logging dates

git clone https://github.com/jamiewoych/pleuro-parser.git

cd pleuro-parser/

pip install -e .

cd pleuro_parser/

streamlit run streamlit-pp.py

PASSWORD = "Pleurodeles123!" #This is temporary

**this will be run on the Workstation through the Tosches Lab github page to ensure only one copy of the inventory is circulating**

#### Files
**salamander_inventory.csv**: Stores the salamander inventory.
- Animal_ID: unique barcode assigned by webapp 
- Tank: dynamic dropdowns for available tanks for each rack 
- Rack: location of animal; "Rack 13 - Off" is a slot for animals temporarily removed from rack for recovery or treatment
- DOB: date of birth 
- Cohort: useful for searching - commonly includes "Viral", "Terra X" Group Assignment, "EdU"
- Environmental_Condition: terrestrial, aquatic, or reaquatic
- Sex: if known, generally only tracked for breeders
- Lineage: tracking source of animal or F0/F1 status of transgenic 
- Transgenic_Line: WT or transgenic line generated
- Experimental_Holds: initials and reason, None if None, Priority for finding animals to use, or Breeding, 
- Species: generally Pleurodeles waltl, sometimes we have Polypterus or Ambystoma
- Protocol_Number: All animals must have associated Protocol number
- Experimental_History: any previous surgical records, or notable events
- RFID: if tag has been inserted to distinguish between other animals in the tank, 
- Date_of_Terra: date of start of terrestrialization
- Date_of_Reaqua: date of start of reaquaticization
- Diet: Diet schedule - useful for matching controls 

**euthanasia_log.csv**: Logs the euthanized salamanders.

-Information transferred from inventory:
Animal_ID, Tank, Rack, DOB, Cohort, Environmental_Condition, Lineage, Transgenic_Line, Experimental_Holds, Species, Protocol_Number, Experimental_History, RFID, Date_of_Terra, Date_of_Reaqua, Diet, Sex if applicable

Additional information to supply for euthanasia
- DOD: date of death, 
- Weight_g: weight in grams 
- Sex: if noted following euthanasia, 
- Purpose: experiment information, 
- Experimenter: who is performing the experiment; can handle multiple initials if separated by commas
- Complications: If animal died of natural cause "found dead", or due to "Surgical Complications"

**Larval_Clutches.csv**:
Breeding events

**Larval_euth_log.csv**
larval euthanasia

### Future directions
- Deploy webapp so others in the lab can use it before to many things change to track



