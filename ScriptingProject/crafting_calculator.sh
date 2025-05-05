#!/bin/bash

echo "Launching Crafting Calculator..."

# Navigate to the directory where your Python file is (adjust path if needed)
cd "$(dirname "$0")"

# Run the Python script
python3 ScriptingProject/ScriptingProject/ScriptingProject.py

# Pause (wait for user input)
read -p "Press Enter to continue..."
