FROM python:3.12-slim-bookworm

# We will be working on this folder
WORKDIR /home/pyuser/code

# Copy wheel into the container
#COPY Chassis/dist/microservice_chassis-0.3.0-py3-none-any.whl ./Chassis/dist/

# Copy the new chassis source and install it in editable mode
COPY Chassis /chassis
RUN pip install --no-cache-dir -e /chassis

# Copy requirements
COPY Client/client_app/requirements.txt .

#COPY requirements.txt /requirements.txt
# Install dependencies
# Install dependencies
RUN apt-get update && apt-get install -y git && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Create a non root user
RUN useradd -u 1000 -d /home/pyuser -m pyuser && \
    chown -R pyuser:pyuser /home/pyuser

 # Copy entrypoint and app
COPY Client/client_app/entrypoint.sh .
RUN chmod +x entrypoint.sh
COPY Client/client_app/app ./app

# Switch to non-root user
USER pyuser

# Run the application
ENTRYPOINT ["./entrypoint.sh"]


