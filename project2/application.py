import os

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)


@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

channel_list = {}

@app.route("/channels", methods=["GET", "POST"])
def channels():
    """Create a new channel"""

    channel_name = None
    channel_name = request.form.get("channel_name")

    if channel_name != None:
        try:
            channel_list[channel_name]
            return render_template("channels.html", message="That channel already exists. Please enter a different channel name.", channel_list=channel_list)
        except:
            channel_list[channel_name] = []
            return render_template("channels.html", message="Channel created.", channel_list=channel_list)

    return render_template("channels.html", message="Create a new channel.", channel_list=channel_list)

@app.route("/channels/<channel>", methods=["GET", "POST"])
def channel(channel):
    return render_template("channel.html", channel_name=channel)

@app.route('/posts', methods=["POST"])
def posts():
    channel = request.form.get("channel")
    return jsonify(channel_list[channel])


@socketio.on("submit message")
def message(data):

    channel = data["channel"]
    new_message = data["new_message"]
    time = data["time"]
    displayname = data["displayname"]

    if len(channel_list[channel]) == 10:
        channel_list[channel].pop(0)
    channel_list[channel].append([new_message, time, displayname])

    emit("channel messages", [new_message, time, displayname], broadcast=True)

@socketio.on("delete message")
def delete_message(msg_data):
    channel = msg_data["channel"]
    postid = msg_data["postid"]
    del channel_list[channel][postid]
    print("postid: ", postid)
    print("channel list: ", channel_list[channel])

    emit("removed message", postid, broadcast=True)

