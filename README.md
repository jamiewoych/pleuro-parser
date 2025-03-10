# mini-project
Spreadsheet parsing tool for manipulating metadata of salamander inventory
Metadata for each animal includes:
Animal location
DOB
Environmental condition
Lineage
Transgenic status
RFID if applicable
Experimental holds
Species
Protocol number
Experimental history

Euthanasia log:
DOD
weight
sex
purpose
experimentor
complications

Expected output: Interface for tracking animal usage by protocol, visualizing usage of space, and updating inventory when moving, using, or adding clutches to the rack space. 

### Installation

conda install pandas numpy random matplotlib.pyplot seaborn datetime -c conda-forge

git clone https://github.com/jamiewoych/mini-project
cd ./mini-project
pip install -e
