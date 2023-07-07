#!/bin/bash

# Check if the python3 virtual environment exists
if [ -d "./venv" ]; then
    echo "Python3 virtual environment found."
    # Activate the virtual environment
    source ./venv/bin/activate
else
    echo "Python3 virtual environment not found. Running with system default Python3."
fi

# Check Python3 version
python_version=($(python3 -c 'import sys; print(sys.version_info[0], sys.version_info[1])'))
required_version=(3 9)

if (( ${python_version[0]} < ${required_version[0]} || (${python_version[0]} == ${required_version[0]} && ${python_version[1]} < ${required_version[1]}) )); then
    echo "Python3 version 3.9 or higher is required. Terminating script."
    exit 1

elif [ -z "$discord_token" ]; then
    echo "Discord token not set. Terminating script."
    exit 1
elif [ -z "$telegram_token" ]; then
    echo "Telegram token not set. Running Discord bot only..."
    python3 bot/src/app.py
else
    echo "Running Discord bot and Telegram bot..."
    python3 bot/src/app.py & python3 bot/src/telegram_util.py
fi
