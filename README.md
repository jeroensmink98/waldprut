# Waldnet News Scraper

A simple Python script that scrapes news items and their reactions from waldnet.nl.

## Features

- Fetches news items from waldnet.nl
- Extracts news titles, categories, and images
- Retrieves reactions and nested reactions for each news item
- Includes user information and reaction counts
- Respects server load with request delays

## Requirements

- Python 3.x
- requests
- beautifulsoup4

## Usage

create a virtual environment and install the requirements:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Run the script with:

```bash
python main.py
```

The script will fetch the latest news items and their reactions, displaying them in a formatted output.

## Note

This script is for educational purposes only. Please respect the website's terms of service and robots.txt when using this script.
