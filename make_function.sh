#!/bin/bash

# Creates a Google Cloud Function-compatible archive.

git diff-index --quiet HEAD
RESULT=$?
if [ $RESULT -eq 1 ]; then
  echo "ERR: There are changes to be committed. Unable to create reproducible archive from commit hash."
  exit 1
fi

set -ef

STARTING_DIR="$(pwd)"
BUILD_DIR="${STARTING_DIR}/build"
DIST_DIR="${STARTING_DIR}/dist"
CURRENT_HASH="$(git log --pretty=format:'%H' -n 1)"
ARCHIVE_FILENAME="${DIST_DIR}/function-${CURRENT_HASH}.zip"

# Create new dir for function
mkdir -p ${BUILD_DIR} ${BUILD_DIR}/monzo_to_ynab dist

# Copy files and install requirements in function dir
cp -r {main.py,requirements.txt} ${BUILD_DIR}
find monzo_to_ynab -name "*.py" -exec cp {} ${BUILD_DIR}/monzo_to_ynab \;

# Archive required files
cd ${BUILD_DIR}
zip -r9 ${ARCHIVE_FILENAME} .

# Clean up build directory
cd ${STARTING_DIR}
rm -rf ${BUILD_DIR}

# Done
echo "Created function ZIP archive at ${ARCHIVE_FILENAME}"
