#!/bin/bash

# Build the first image to install dependencies
echo "Building the base image with dependencies..."
docker build -f DockerfileRequirements -t image-requirements .

# Check if the first build was successful
if [ $? -eq 0 ]; then
  echo "Base image built successfully."
else
  echo "Failed to build the base image."
  exit 1
fi

# Build the second image based on the first image
echo "Building the app image..."
docker build -f Dockerfile -t backend-app .

# Check if the second build was successful
if [ $? -eq 0 ]; then
  echo "App image built successfully."
else
  echo "Failed to build the app image."
  exit 1
fi
