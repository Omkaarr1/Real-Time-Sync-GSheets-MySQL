import threading
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# MySQL Setup
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="0000",
    database="superjoin_db"
)
cursor = db.cursor()

# Google Sheets Setup
SERVICE_ACCOUNT_FILE = 'service_account_key.json'  # Ensure this file is in the same directory as your script
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
client = gspread.authorize(credentials)
spreadsheet = client.open("Superjoin_Assessment")  # Change this to your actual Google Sheet name
sheet = spreadsheet.sheet1

def execute_with_retry(query, params, retries=3, delay=2):
    """
    Execute a MySQL query with retry mechanism in case of table definition change errors.
    """
    for attempt in range(retries):
        try:
            cursor.execute(query, params)
            db.commit()
            return
        except Error as e:
            if "1412 (HY000)" in str(e):
                print(f"Retrying query due to table definition change: Attempt {attempt + 1}")
                time.sleep(delay)
            else:
                raise

def process_event_log():
    try:
        # Fetch all events from the event log table
        cursor.execute("SELECT id, event_type, col1, col2, last_modified FROM event_log")
        events = cursor.fetchall()  # Fetch all results to clear the cursor

        # Get all existing records from Google Sheets in one go
        sheet_data = sheet.get_all_records()
        rows_to_update = []
        rows_to_append = []
        rows_to_delete = []

        for event in events:
            event_id, event_type, col1, col2, last_modified = event
            matching_row = None

            if event_type == 'INSERT' or event_type == 'UPDATE':
                # Find the matching row in Google Sheets based on 'Col1'
                for i, r in enumerate(sheet_data):
                    if str(r.get('Col1', '')) == str(col1):
                        matching_row = i + 2  # Adjust for header row
                        sheet_last_modified_str = r.get('last_modified', '')
                        try:
                            sheet_last_modified = datetime.strptime(sheet_last_modified_str, '%Y-%m-%d %H:%M:%S')
                        except ValueError:
                            sheet_last_modified = datetime.min  # Set to a default past date if parsing fails

                        # Only update if the MySQL last_modified is newer
                        if last_modified > sheet_last_modified:
                            rows_to_update.append({
                                'row': matching_row,
                                'col2': col2,
                                'last_modified': last_modified.strftime('%Y-%m-%d %H:%M:%S')
                            })
                        break

                # If no matching row found, mark for appending
                if not matching_row:
                    rows_to_append.append([col1, col2, last_modified.strftime('%Y-%m-%d %H:%M:%S')])

            elif event_type == 'DELETE':
                # Find the row in Google Sheets and mark for deletion
                for i, r in enumerate(sheet_data):
                    if str(r.get('Col1', '')) == str(col1):
                        matching_row = i + 2  # Adjust for header row
                        rows_to_delete.append(matching_row)
                        break

            # Remove the processed event from the log
            execute_with_retry("DELETE FROM event_log WHERE id = %s", (event_id,))

        # Batch update rows in Google Sheets
        if rows_to_update:
            cell_updates = []
            for update in rows_to_update:
                cell_updates.append({'range': f'B{update["row"]}', 'values': [[update['col2']]]})
                cell_updates.append({'range': f'C{update["row"]}', 'values': [[update['last_modified']]]})
            sheet.batch_update(cell_updates)

        # Batch append rows
        if rows_to_append:
            sheet.append_rows(rows_to_append)

        # Batch delete rows
        if rows_to_delete:
            for row in sorted(rows_to_delete, reverse=True):
                try:
                    sheet.delete_rows(row)  # Corrected method call
                except Exception as e:
                    print(f"Error deleting row {row} from Google Sheets: {e}")

    except Exception as e:
        print(f"Error processing event log: {e}")

# Continuous poll loop
def continuous_poll():
    try:
        while True:
            process_event_log()
            time.sleep(5)  # Poll every 5 seconds
    except Exception as e:
        print(f"Error in polling loop: {e}")

# Start the continuous polling in a separate thread
def start_polling_thread():
    poll_thread = threading.Thread(target=continuous_poll)
    poll_thread.daemon = True  # Daemonize thread to run in the background
    poll_thread.start()

@app.route('/update_mysql', methods=['POST'])
def update_mysql():
    try:
        # Parse incoming JSON data
        data = request.get_json(force=True)
        if not data or 'col1' not in data or 'col2' not in data:
            return jsonify({'status': 'error', 'message': 'Invalid data format'}), 400

        col1 = data.get('col1')
        col2 = data.get('col2')
        last_modified_str = data.get('last_modified')
        if last_modified_str:
            last_modified = datetime.strptime(last_modified_str, '%Y-%m-%dT%H:%M:%S.%fZ')
        else:
            last_modified = datetime.now()

        # Check if the record exists in MySQL
        cursor.execute("SELECT col1, last_modified FROM superjoin_table WHERE col1 = %s", (col1,))
        existing_record = cursor.fetchone()  # Fetch one row to clear the result set

        # Close the result set completely to avoid "Unread result found"
        cursor.fetchall()  # Fetch all remaining rows, if any, to ensure the cursor is cleared

        if existing_record:
            existing_last_modified = existing_record[1]
            if last_modified > existing_last_modified:
                # Update existing record in MySQL
                execute_with_retry(
                    "UPDATE superjoin_table SET col2 = %s, last_modified = %s WHERE col1 = %s",
                    (col2, last_modified, col1)
                )
                event_type = 'UPDATE'

                # Log the event into the event_log table
                execute_with_retry(
                    "INSERT INTO event_log (event_type, col1, col2, last_modified) VALUES (%s, %s, %s, %s)",
                    (event_type, col1, col2, last_modified)
                )
                return jsonify({'status': 'success', 'message': 'MySQL updated successfully'})
            else:
                return jsonify({'status': 'ignored', 'message': 'Older data, update ignored'})
        else:
            # Insert new record into MySQL
            execute_with_retry(
                "INSERT INTO superjoin_table (col1, col2, last_modified) VALUES (%s, %s, %s)",
                (col1, col2, last_modified)
            )
            event_type = 'INSERT'

            # Log the event into the event_log table
            execute_with_retry(
                "INSERT INTO event_log (event_type, col1, col2, last_modified) VALUES (%s, %s, %s, %s)",
                (event_type, col1, col2, last_modified)
            )
            return jsonify({'status': 'success', 'message': 'MySQL inserted successfully'})
    except Exception as e:
        print(f"Error updating MySQL: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Start the Flask app and the polling thread
if __name__ == '__main__':
    start_polling_thread()  # Start polling before Flask runs
    app.run(debug=True, host='0.0.0.0', port=5000)