# Instructions
## Usage
This project aims to automatize downloading pdf files from secmail mails into suiting directories. It allows to specify a period of time to automatically check for new secmail mails. Currently it's required that you don't open mails from secmail in your inbox, otherwise the emailbot won't notice them. 

## Requirements
- Python 3.11
- local google chromium installation
- dependency management tool poetry: <code>pipx install poetry</code>

## Getting started
- cd into cloned folder
- rename .env.example to .env and initialize variables
- run <code>poetry install</code> to create a virtual environment and install needed dependencies
- run <code>poetry shell</code> to start the created virtual environment
- finally enter <code>poetry run python emailbot/code/main.py</code>

