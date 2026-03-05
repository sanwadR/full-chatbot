FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Expose Chainlit default port
EXPOSE 7860

# Run the Chainlit app
CMD ["chainlit", "run", "app.py", "--host", "0.0.0.0", "--port", "7860"]