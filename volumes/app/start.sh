#!/bin/bash
cd /app
if [ -f /app/timesheet_app.py ]; then
    echo "Starting timesheet app from data volume..."
    exec python /app/timesheet_app.py
else
    echo "Error: timesheet_app.py not found in /app/data/"
    echo "Please ensure timesheet_app.py is in the data volume."
    exit 1
fi


