### Objective
Build a solution that enables real-time synchronization of data between a Google Sheet and a specified database (e.g., MySQL, PostgreSQL). The solution should detect changes in the Google Sheet and update the database accordingly, and vice versa.

### Problem Statement
Many businesses use Google Sheets for collaborative data management and databases for more robust and scalable data storage. However, keeping the data synchronised between Google Sheets and databases is often a manual and error-prone process. Your task is to develop a solution that automates this synchronisation, ensuring that changes in one are reflected in the other in real-time.

### Requirements:
1. Real-time Synchronisation
  - Implement a system that detects changes in Google Sheets and updates the database accordingly.
   - Similarly, detect changes in the database and update the Google Sheet.
  2.	CRUD Operations
   - Ensure the system supports Create, Read, Update, and Delete operations for both Google Sheets and the database.
   - Maintain data consistency across both platforms.
   
### Challenges (Completed):
1. Conflict Handling
- Develop a strategy to handle conflicts that may arise when changes are made simultaneously in both Google Sheets and the database.
- Provide options for conflict resolution (e.g., last write wins, user-defined rules).
    
2. Scalability: 	
- Ensure the solution can handle large datasets and high-frequency updates without performance degradation.
- Optimize for scalability and efficiency.

## Developer's Section
-------------------------------------------------------------------------------------------------------------------

# Real-Time Synchronization Between Google Sheets and MySQL

## Video Demonstration: [Link](https://drive.google.com/file/d/1-WyAr-Qe35tLvymlxNbvhzguUh6JYTUi/view?usp=sharing)

## Table of Contents
- [Project Overview](#project-overview)
- [Problem Statement](#problem-statement)
- [Approach](#approach)
- [Technologies and Tools Used](#technologies-and-tools-used)
- [Implementation Steps](#implementation-steps)
  - [1. Setting Up Google Sheets API](#1-setting-up-google-sheets-api)
  - [2. MySQL Database Configuration](#2-mysql-database-configuration)
  - [3. Flask Application Setup](#3-flask-application-setup)
  - [4. Handling CRUD Operations](#4-handling-crud-operations)
  - [5. Handling Edge Cases](#5-handling-edge-cases)
- [Error Handling and Resilience](#error-handling-and-resilience)
- [Planned-Out Approach to the Problem](#planned-out-approach-to-the-problem)
- [Conclusion](#conclusion)

## Project Overview

This project provides a robust solution for real-time synchronization between Google Sheets and MySQL. It automates data updates, ensuring consistency between Google Sheets, which is user-friendly and collaborative, and MySQL, which is ideal for structured and large datasets. The project involves real-time CRUD operations, allowing changes in one platform to reflect seamlessly in the other.

## Problem Statement

Many businesses use Google Sheets for collaborative data management but rely on MySQL for scalable and robust data storage. Manually keeping data synchronized between these platforms is error-prone and time-consuming. The goal of this project is to automate the synchronization process, enabling real-time updates between Google Sheets and MySQL while maintaining data integrity and handling edge cases gracefully.

## Approach

To achieve real-time synchronization, we built a Flask-based backend service that listens for changes in both Google Sheets and MySQL. This service handles CRUD operations by capturing events, logging them, and processing these logs to update the other platform accordingly.

Key steps:
1. **Set up event triggers** in MySQL to log changes.
2. **Use Google Apps Script** to detect changes in Google Sheets and send updates to Flask.
3. **Implement a Flask service** that continuously polls event logs and synchronizes changes.
4. **Handle edge cases** like deletion and outdated data with robust error handling.

## Technologies and Tools Used

- **Python**: Core programming language for building the backend service.
- **Flask**: Web framework for handling HTTP requests and integrating synchronization logic.
- **MySQL**: Database system for scalable and reliable data storage.
- **Google Sheets API**: For programmatically accessing and manipulating Google Sheets.
- **gspread**: Python library for interacting with Google Sheets.
- **Google Apps Script**: To create triggers for detecting changes in Google Sheets.
- **Threading**: For running continuous polling in the background.
- **MySQL Triggers**: To log changes automatically in an event log table.

## Implementation Steps

### 1. Setting Up Google Sheets API

- **Step 1**: Create a Google Cloud project and enable the Google Sheets API.
- **Step 2**: Create a service account, generate a key, and download the `service_account_key.json` file.
- **Step 3**: Share the Google Sheet with the service account email to grant access.
- **Step 4**: Use the `gspread` library to authenticate and connect to the Google Sheet.

### 2. MySQL Database Configuration

- **Step 1**: Install MySQL and create a database named `superjoin_db`.
- **Step 2**: Create a table named `superjoin_table` to store synchronized data.
- **Step 3**: Create an `event_log` table to capture all changes (INSERT, UPDATE, DELETE) made in MySQL.
- **Step 4**: Set up MySQL triggers for each CRUD operation to log events automatically.

### 3. Flask Application Setup

- **Step 1**: Set up a Python virtual environment and install required dependencies from `requirements.txt`.
- **Step 2**: Create a Flask application that handles POST requests from Google Sheets and processes event logs from MySQL.
- **Step 3**: Implement endpoints in Flask to handle CRUD operations and synchronize data between Google Sheets and MySQL.
- **Step 4**: Use threading to continuously poll the event log and update Google Sheets as needed.

### 4. Handling CRUD Operations

- **INSERT/UPDATE**: New or modified rows in MySQL are captured in the event log and reflected in Google Sheets by appending or updating rows.
- **DELETE**: Rows deleted in MySQL trigger a DELETE event, which finds the corresponding row in Google Sheets and removes it.

### 5. Handling Edge Cases

1. **Outdated Data Overwriting**: We compared timestamps between MySQL and Google Sheets to ensure that only the most recent changes were applied.
   
2. **Row Identification for Deletion**: When a row was cleared or deleted, the application accurately identified the row in Google Sheets using unique identifiers from `col1`. This ensured that the correct row was removed without affecting other data.

3. **Handling Missing Rows**: If a row was not found in Google Sheets during the delete operation, the error was logged without interrupting the rest of the synchronization process.

4. **Retry Mechanism**: Implemented retries for operations like updates and deletions in case of temporary failures due to changes in MySQL schema, which ensured resilience in the system.

## Error Handling and Resilience

- **Logging and Error Handling**: All CRUD operations and synchronization steps were wrapped in try-except blocks to capture and log errors without crashing the application.
- **Retry Mechanism**: Critical operations like MySQL updates were retried with a delay in case of transient errors, ensuring data consistency.
- **Graceful Failure Handling**: For instance, if a Google Sheets row deletion failed due to the row not existing, the error was caught, logged, and the script continued to process other updates.

## Planned-Out Approach to the Problem

1. **Identify Synchronization Points**: Defined key points where data needed to be captured and synchronized between Google Sheets and MySQL.
   
2. **Design Event-Driven Architecture**: Used MySQL triggers and Google Apps Script triggers to capture changes as events, enabling a seamless flow of updates.

3. **Implement Core Synchronization Logic**: Developed a central Flask service that handled incoming requests and polled event logs to synchronize changes.

4. **Optimize for Performance and Scalability**: Batched updates and deletions in Google Sheets to minimize API calls and improve performance. Introduced threading for continuous background processing.

5. **Edge Case Management**: Strategically handled potential issues like timestamp mismatches, failed deletions, and outdated data overwrites by designing robust comparison and error handling logic.

6. **Testing and Validation**: Extensively tested each CRUD operation, including inserts, updates, and deletions, across both platforms to ensure the system worked as intended.

## Conclusion

The project successfully automates real-time synchronization between Google Sheets and MySQL, providing a reliable, scalable, and efficient solution for data management. By addressing critical edge cases and implementing resilient error handling, the system ensures data consistency and integrity, making it an ideal solution for businesses needing synchronized collaborative and structured data storage.


