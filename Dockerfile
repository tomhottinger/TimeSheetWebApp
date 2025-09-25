# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create directories
RUN mkdir -p /app/data /app/templates

# Set environment variables
ENV PYTHONPATH=/app/data
ENV DATABASE_PATH=/app/data/timesheet.db
ENV FLASK_ENV=production

# Create a startup script that runs the app from the data volume
RUN echo '#!/bin/bash\n\
cd /app\n\
if [ -f /app/data/timesheet_app.py ]; then\n\
    echo "Starting timesheet app from data volume..."\n\
    exec python /app/data/timesheet_app.py\n\
else\n\
    echo "Error: timesheet_app.py not found in /app/data/"\n\
    echo "Please ensure timesheet_app.py is in the data volume."\n\
    exit 1\n\
fi' > /app/start.sh && chmod +x /app/start.sh

# Expose port
EXPOSE 5000

# Use the startup script
CMD ["/app/start.sh"]
