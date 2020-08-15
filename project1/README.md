# Project 1

Web Programming with Python and JavaScript

The project outline and requirements can be found here: https://docs.cs50.net/ocw/web/projects/1/project1.html

This project was to essentially build an application that lets a user log-in, search for book details and be able to submit reviews. 

Key things to note in this project: 
- Database integration
- Users can register an account and log-in
- Book details that can be searched have been loaded into the database
    - SQL commands have been included in create.sql that outline the various database tables
    - import.py is a file that has been used to read in book data into the database tables
- Users can view book details and add a review

To run this locally, navigate to the folder and in your terminal run the commands: 
pip3 install -r requirements.txt
export FLASK_APP=application.py
export DATABASE_URL=___ (has been excluded in this README for privacy reasons)
flask run

Some images of the project can be viewed in the 'application photos' folder.
