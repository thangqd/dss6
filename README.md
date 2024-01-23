# MKDC DSS-6
This repository contains code for Decision Support System 6 within the Mekong Delta Centre.

# Land Use Decision Support System for the Mekong Delta

This Decision Support System (DSS) is designed to forecast the impact of different types of natural hazards within the Mekong Delta. 

## Features

- Support for four types of natural hazards
	- Floods
	- Drought
	- Saline Intrusion
	- Landslides
- Forecast the economic damage of the natural hazards.
- Forecast the amount of people which are involved by the natural hazards 
- Perform analysis in an online hosted environment and download the results as a file. 

## Prerequisites

- Docker installed on your machine.

## Getting Started

1. **Clone the Repository:**
    ```bash
    git clone https://github.com/thangqd/dss6.git
	```
	
2. **Create a .env file with an API key**

To access the Lizard webservice a valid API key is required. This is supplied in a .env file. An example file is available in the repo. 
	
3. **Build the Docker Image:**
	```bash
	cd dss6
	docker-compose build 
	```
	
4. **Run the Docker Container:**
    ```bash
    docker-compose up
	```

5. **Access the DSS:**

Open your web browser and go to http://localhost:8501 to interact with the Decision Support System.

## Support
For any inquiries or issues, please https://github.com/thangqd/dss6/issues
