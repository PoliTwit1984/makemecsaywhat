#!/bin/bash

# Create and activate virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Set up environment variables
echo "Setting up environment variables..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file from template. Please update with your API keys."
fi

# Initialize database
echo "Initializing database..."
python app.py

echo "Setup complete!"
echo "Next steps:"
echo "1. Update API keys in .env file"
echo "2. Run 'python app.py' to start the server"
echo "3. Access the web interface at http://localhost:8000"
