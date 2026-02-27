This is a Recipe Managment Project using HTML, CSS AND JS for frontend and for backend we are using flask and for database SQLite.

A2Z Application – Quick Setup (New PC)

1. Install SQL Server

Install Microsoft SQL Server
Enable Database Engine
Use Windows Authentication

2. Create SQL Instance

Instance name must be:

WINCC

Server format:

DESKTOP-9G39B01\WINCC

(Replace DESKTOP-9G39B01 with your PC name if different)

3. Create Database

In SQL Server Management Studio (SSMS):

New Database name:

A2Z_DB


4. Run Application

Run the A2Z EXE (preferably as Administrator)

On first run:

Connects to A2Z_DB
Automatically creates all tables

5. Done

Verify in SSMS:

A2Z_DB → Tables

If this fails, Please Check:
✔ SQL service running
✔ Correct instance name
✔ Database name exactly A2Z_DB


Command to create exe file - python -m PyInstaller --onefile --icon=static/N-LOG.ico --add-data "templates;templates" --add-data "static;static" --name flask_app final.py