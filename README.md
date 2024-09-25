# Project Overview

This project consists of four key Python scripts, each serving a specific functionality within the overall system. Below is a brief overview of each script and its role:

## 1. `db_operations.py`

This script handles all database-related operations such as connecting to the database, executing queries, and managing transactions. It abstracts the database layer, providing functions to interact with the data seamlessly. Key functions include:

- **Database Connection**: Establishes a connection to the database.
- **CRUD Operations**: Create, Read, Update, and Delete operations on the database.
- **Transaction Management**: Handles database transactions and ensures rollback in case of failure.

## 2. `main.py`

This is the main entry point of the project. It initializes the application, manages the flow of control, and orchestrates interactions between various modules. Key responsibilities include:

- **Initialization**: Loads configurations, initializes objects and resources.
- **Control Flow**: Directs the sequence of operations by invoking appropriate modules like `db_operations.py` or `mpox_scraper.py`.
- **Error Handling**: Manages exceptions and ensures graceful application shutdown in case of errors.

## 3. `mpox_scraper.py`

This script is responsible for scraping Mpox-related data from external sources. It retrieves, processes, and stores data in a structured format. Major functionalities include:

- **Web Scraping**: Extracts Mpox-related information from specified URLs.
- **Data Cleaning**: Processes and filters the scraped data to ensure accuracy and relevance.
- **Data Storage**: Interfaces with the database to store the cleaned data.

## 4. `Page.py`

`Page.py` handles the rendering and management of pages within the application. It is primarily focused on the user interface (UI) aspects, allowing for dynamic page content and layout rendering. Key features include:

- **Page Rendering**: Dynamically generates HTML or UI elements.
- **User Interaction**: Manages user inputs and page transitions.
- **Template Management**: Utilizes pre-defined templates to create consistent page layouts.

---

## Installation

To run this project, ensure you have Python installed on your machine. Then, install the necessary dependencies by running:

```bash
pip install -r requirements.txt
