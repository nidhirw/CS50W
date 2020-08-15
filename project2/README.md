# Project 2

Web Programming with Python and JavaScript

The project outline and requirements can be found here: https://docs.cs50.net/ocw/web/projects/2/project2.html

This project was essentially to build a messaging platform. You first register a display name, then you can create various chatrooms or "channels" and then send messages to other users within those chatrooms. 

Key things to note in this project:
- Display name for a user is stored local storage and can be changed at any time
- When creating new channels, there's logic to make sure the channel doesn't exist
- When you enter a channel, you can view the last 10 messages sent in that room
- You can delete messages in a channel using the "Delete" button
- Some CSS animation has been introduced when deleting a message
- The page automatically updates with new messages from other users without having to reload the page

This project has been created by using HTML, CSS, Flask, Python & Javascript. 

To run this locally, navigate to the folder and in your terminal run the commands:

pip3 install -r requirements.txt

export FLASK_APP=application.py

flask run
