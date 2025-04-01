In this proposal you should expand upon the contents in your mini-project proposal to incorporate any feedback that we provided previously, and to update it with any new ideas or progress you have made in designing your project. Using markdown, you should create nicely formatted headings and paragraphs to list the following topics and your answers:

## What task/goal will the project accomplish and why is this useful?
This project will allow ease of updating, tracking, and visualizing the Tosches lab animal inventory. Instead of multiple spreadsheets needing to be updated to track animals, both the inventory and euthanasia log can be updated at the same time. Visualization of rack space allows users to identify or find animals of interest. 

## What type of data/input will a user provide to the program?
From the database, users can contribute to the inventory by adding, removing, or moving animals in tanks. Using a webapp interface, users will be able to select one of these tasks, and input the required information. 

## Where will the data come from?
I can store my data as a SQL database that uses json format, and retrieve this data via REST API for updating in my Flask webapp. For example, my data may be stored like this:

I
[
    {
        "animal_id": "SAL_001",
        "rack": "Rack 1",
        "tank": 3,
        "dob": "2022-06-15",
        "species": "Ambystoma mexicanum",
        "transgenic_status": "hsyn-GFP",
        "rfid": "1234567890",
        "protocol_number": "AABF",
        "experimental_history": ["Viral injection", "Regeneration"]
    },
    {
        "animal_id": "SAL_002",
        "rack": "Rack 2",
        "tank": 5,
        "dob": "2021-11-30",
        "species": "Pleurodeles waltl",
        "transgenic_status": "Wildtype",
        "rfid": null,
        "protocol_number": "AABL",
        "experimental_history": ["Behavior Conditioning"]
    }
]

## How will a user interact with the program?
In my mini project version, animals could be added to the euthanasia log even if they weren't in the inventory. This version will have limitations to avoid this situation, and provide prompts for information needed to be entered for ease of use. The REST API will be deployed using Railway to make it accessible to the rest of the lab

## What type of output will the program produce (e.g., text, plots)?
The program will produce visualizations for which Rack/Tank each salamander is on, as well as the ability to query for specific ages, or conditions, or transgenic line. 

## What other tools currently exist to do this task, or something similar?
GBIF uses a REST API to query a database. There are likely many others.