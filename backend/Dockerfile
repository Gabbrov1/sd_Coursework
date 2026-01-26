FROM mcr.microsoft.com/mssql/server:2022-latest

# Install Python and pip
RUN apt-get update && apt-get install -y python3 python3-pip python3-dev unixodbc-dev

# Set working directory
WORKDIR /app

# Copy requirements and install Python packages
COPY requirements.txt .


# Copy the rest of your app
COPY . .


# Install Python dependencies
RUN pip3 install -r requirements.txt

# Expose Flask port
EXPOSE 5000

# Start Flask app
CMD ["python3", "app.py"]
