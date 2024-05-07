#!/bin/bash

# Check if Homebrew is installed, otherwise install it
if ! command -v brew &>/dev/null; then
    echo "Homebrew is not installed. Proceeding with the installation of Homebrew."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

echo "Updating Homebrew..."
brew update

# Install Python 3 if not installed
if ! command -v python3 &>/dev/null; then
    echo "Installing Python 3..."
    brew install python3
fi

# Install Docker if not installed
if ! command -v docker &>/dev/null; then
    echo "Installing Docker..."
    brew install --cask docker
fi

# Start Docker if not running
if (! docker stats --no-stream ); then
  # Start Docker service if not running
  open /Applications/Docker.app
  # Wait for Docker to properly start before continuing
  while (! docker stats --no-stream ); do
    echo "Waiting for Docker to start..."
    sleep 5
  done
fi

# Download the Redis image in Docker
echo "Downloading the Redis image in Docker..."
docker pull redis:latest

# Install jq if not installed
if ! command -v jq &>/dev/null; then
    echo "Installing jq..."
    brew install jq
fi

# Install MySQL if not installed
if ! command -v mysql &>/dev/null; then
    echo "Installing MySQL..."
    brew install mysql
fi

# Install Python dependencies specified in the requirements.txt file
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

echo "All dependencies have been installed."
