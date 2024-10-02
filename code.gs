function onEditTrigger(e) {
  try {
    // Retrieve the edited range and sheet
    Logger.log('Trigger initiated.');
    var range = e.range;
    var sheet = range.getSheet();
    Logger.log('Edited sheet: ' + sheet.getName());
    
    // Exit if the edited sheet is not the one we're monitoring
    if (sheet.getName() !== 'Sheet1') { // Adjust if your sheet has a different name
      Logger.log('Edited sheet is not Sheet1, exiting function.');
      return;
    }
    
    // Get the values of the entire edited row
    var rowNumber = range.getRow();
    var lastColumn = sheet.getLastColumn();
    var rowData = sheet.getRange(rowNumber, 1, 1, lastColumn).getValues()[0];
    Logger.log('Edited row data: ' + JSON.stringify(rowData));
    
    // Check if 'col1' and 'col2' are present
    var col1 = rowData[0]; // Assuming 'col1' is in the first column
    var col2 = rowData[1]; // Assuming 'col2' is in the second column
    var last_modified = rowData[2]; // Assuming 'last_modified' is in the third column
    Logger.log('col1: ' + col1 + ', col2: ' + col2 + ', last_modified: ' + last_modified);
    
    if (col1 === '' && col2 === '') {
      // If both columns are empty, do nothing
      Logger.log('Both col1 and col2 are empty, exiting function.');
      return;
    }
    
    // If 'last_modified' is empty or the edited cell is not 'last_modified' column
    if (range.getColumn() !== 3 || !last_modified) {
      Logger.log('Updating last_modified timestamp.');
      // Set 'last_modified' to current timestamp
      last_modified = new Date();
      sheet.getRange(rowNumber, 3).setValue(last_modified.toISOString());
      Logger.log('last_modified set to: ' + last_modified.toISOString());
    } else {
      last_modified = new Date(last_modified);
      Logger.log('last_modified already set: ' + last_modified.toISOString());
    }
    
    // Create a JSON object with the row data
    var data = {
      col1: col1.toString(),  // Convert to string in case of numbers
      col2: col2.toString(),  // Convert to string in case of numbers
      last_modified: last_modified.toISOString()
    };
    Logger.log('JSON data to be sent: ' + JSON.stringify(data));
    
    // Set up the POST request options
    var options = {
      method: 'POST',
      contentType: 'application/json',
      payload: JSON.stringify(data),
      muteHttpExceptions: true
    };
    Logger.log('POST request options: ' + JSON.stringify(options));
    
    // Replace with your Flask app's correct public IP and endpoint
    var url = 'http://44.211.142.254:5000/update_mysql'; // Use your actual Flask app's public IP and endpoint
    Logger.log('Sending POST request to URL: ' + url);
    
    // Send the data to the Flask app
    var response = UrlFetchApp.fetch(url, options);
    Logger.log('POST request sent successfully: ' + response.getContentText());
    
  } catch (error) {
    Logger.log('Error in onEditTrigger function: ' + error.message);
  }
}
