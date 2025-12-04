#!/bin/bash

echo "Setting up Docker environment..."

# Create users.db if it doesn't exist
if [ ! -f users.db ]; then
    echo "Creating users.db..."
    touch users.db
else
    echo "users.db already exists."
fi

# Create .env if it doesn't exist (copy from example)
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        echo "Creating .env from .env.example..."
        cp .env.example .env
        # Generate a random secret key
        SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
        echo "" >> .env
        echo "SECRET_KEY=$SECRET" >> .env
        echo "Generated new SECRET_KEY in .env"
    else
        echo "WARNING: .env.example not found. Please create .env manually."
    fi
else
    echo ".env already exists."
fi

echo "Setup complete. You can now run: docker compose up --build"
