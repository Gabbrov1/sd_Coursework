FROM mcr.microsoft.com/mssql/server:2022-latest

# Install Python and pip
RUN apt-get update && apt-get install -y python3 python3-pip python3-dev unixodbc-dev

# Set working directory
WORKDIR /app

# Copy backend code
COPY ./backend /app

# Install Python dependencies
RUN pip3 install -r requirements.txt

# Expose Flask port
EXPOSE 5000

# Start Flask app
CMD ["python3", "app.py"]
