#!/bin/bash

# Creates a Google Cloud Function-compatible archive.

set -ef

TARGET_DIRECTORY=$(pwd)

# Delete old function stuff
rm -rf function function.zip

# Create new dir for function
mkdir function

# Copy files and install requirements in function dir
cp -r {main.py,requirements.txt} function

# Archive required files
cd function
zip -r9 ${TARGET_DIRECTORY}/function.zip .

# Clean up build directory
cd ${TARGET_DIRECTORY}
rm -rf function

# Done
cd ${TARGET_DIRECTORY}
echo "Created function ZIP archive at ./function.zip"
