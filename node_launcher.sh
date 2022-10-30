#!/bin/sh
# Run the node code

# Define the git repository name
repo="Node"

# Go to the repo's directory
cd /
cd home/pi/$repo

# Try to pull changes from the USB
sh git_update.sh

# Run the code
python3 main.py

# Go back when done
cd /