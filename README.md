# Instructions
## Usage
This project aims to automatize downloading pdf files from secmail mails into suiting directories. It allows to specify a period of time to automatically check for new secmail mails. Currently it's required that you don't open mails from secmail in your inbox, otherwise the emailbot won't notice them. 

## Requirements
- Python 3.11
- local google <b>chromium</b> installation
- add app password to google account: https://support.google.com/mail/answer/185833?hl=de
- dependency management tool poetry: <code>pipx install poetry</code>

## Getting started
- cd into cloned folder
- rename .env.example to .env and initialize variables
- run <code>poetry install</code> to create a virtual environment and install needed dependencies
- run <code>poetry shell</code> to start the created virtual environment
- finally enter <code>poetry run python emailbot/code/main.py</code>

## Attention
The project was tested with a gmail account. It can't be guaranteed that it will work with other email servers, since this application uses app passwords to sign into email accounts.