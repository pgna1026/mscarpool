from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, join_room, leave_room, emit
from werkzeug.utils import secure_filename
import os
import uuid
import numpy as np
from sklearn.cluster import KMeans

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['JSON_AS_ASCII'] = False  # JSON 응답에서 ASCII 대신 UTF-8을 사용하도록 설정
socketio = SocketIO(app)

# 방 목록, 채팅 기록, 프로필 이미지, 카풀 정보
rooms = []
chat_history = {}
profile_images = {}
carpool_info = {}

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/rooms", methods=["GET"])
def get_rooms():
    return jsonify(rooms)

@app.route("/room/<room_name>")
def room(room_name):
    return render_template("room.html", room_name=room_name)

@app.route("/upload_profile", methods=["POST"])
def upload_profile():
    room_name = request.form['room_name']
    file = request.files['file']
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        profile_images[room_name] = filepath
        return jsonify({"status": "success", "filepath": filepath})
    return jsonify({"status": "failure"})

@socketio.on("create_room")
def create_room(data):
    room_name = data["roomName"].encode('latin1').decode('utf-8')
    departure = data["departure"].encode('latin1').decode('utf-8')
    destination = data["destination"].encode('latin1').decode('utf-8')
    room = {"roomName": room_name, "departure": departure, "destination": destination}
    if room not in rooms:
        rooms.append(room)
        chat_history[room_name] = []
        carpool_info[room_name] = []
        emit("room_created", room, broadcast=True)
    print(f"Room created: {room}")

@socketio.on("join")
def on_join(data):
    room = data["room"].encode('latin1').decode('utf-8')
    nickname = data["nickname"].encode('latin1').decode('utf-8')
    join_room(room)
    print(f"{nickname} joined {room}")
    if room in chat_history:
        print(f"Sending chat history for {room}: {chat_history[room]}")
        emit("chat_history", chat_history[room], room=request.sid)
    if room in profile_images:
        emit("profile_image", profile_images[room], room=request.sid)
    if room in carpool_info:
        emit("carpool_info", carpool_info[room], room=request.sid)

@socketio.on("chat")
def event_handler(json):
    room = json["room"].encode('latin1').decode('utf-8')
    nickname = json["nickname"].encode('latin1').decode('utf-8')
    message = json["message"].encode('latin1').decode('utf-8')
    message_id = str(uuid.uuid4())
    chat_record = {"nickname": nickname, "message": message, "id": message_id}
    if room in chat_history:
        chat_history[room].append(chat_record)
    print(f"Received chat message in {room}: {chat_record}")
    emit("response", chat_record, room=room)

@socketio.on("delete_message")
def delete_message(data):
    room = data["room"].encode('latin1').decode('utf-8')
    message_id = data["id"]
    print(f"Delete request for message id {message_id} in room {room}")  # 디버깅 로그
    if room in chat_history:
        chat_history[room] = [msg for msg in chat_history[room] if msg["id"] != message_id]
        emit("delete_message", message_id, room=room)

@socketio.on("add_carpool_info")
def add_carpool_info(data):
    room = data["room"].encode('latin1').decode('utf-8')
    message_id = data["id"]
    if room in chat_history:
        message = next((msg for msg in chat_history[room] if msg["id"] == message_id), None)
        if message:
            carpool_info[room].append(message)
            emit("carpool_info", carpool_info[room], room=room)

@socketio.on("remove_carpool_info")
def remove_carpool_info(data):
    room = data["room"].encode('latin1').decode('utf-8')
    message_id = data["id"]
    if room in carpool_info:
        carpool_info[room] = [msg for msg in carpool_info[room] if msg["id"] != message_id]
        emit("carpool_info", carpool_info[room], room=room)

@socketio.on("request_match")
def request_match():
    coordinates = []
    room_names = []
    for room in rooms:
        dep_coords = list(map(float, room['departure'].split(',')))
        des_coords = list(map(float, room['destination'].split(',')))
        coordinates.append(dep_coords)
        coordinates.append(des_coords)
        room_names.append(room['roomName'])
        room_names.append(room['roomName'])

    coordinates = np.array(coordinates)
    kmeans = KMeans(n_clusters=max(1, len(coordinates) // 4), random_state=0).fit(coordinates)
    labels = kmeans.labels_

    groups = {}
    for label, room_name in zip(labels, room_names):
        if label not in groups:
            groups[label] = []
        groups[label].append(room_name)

    results = [group for group in groups.values()]
    socketio.emit("match_results", results)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=14000, debug=True)
