# RemindMeServer
Server for synchronizing reminders on phone

## Environment
- Python 3.11
- Postgresql

## How to install
1. Download repository and change directory to new folder with its name
2. Setup PostgreSQL
3. Copy config file from example `config.toml.example` and rename it to config.toml
4. Put format connection string to database with your credentials and other parameters
5. Run server using `python -m src`
6. Check if application is working on http://localhost:8900