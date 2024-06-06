from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, join_room, leave_room, emit

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # JSON 응답에서 ASCII 대신 UTF-8을 사용하도록 설정
socketio = SocketIO(app)

# 방 목록과 채팅 기록을 유지하기 위한 전역 변수
rooms = []
chat_history = {}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/rooms", methods=["GET"])
def get_rooms():
    return jsonify(rooms)

@app.route("/room/<room_name>")
def room(room_name):
    return render_template("room.html", room_name=room_name)

@socketio.on("create_room")
def create_room(room_name):
    room_name = room_name.encode('latin1').decode('utf-8')  # 인코딩 수정
    if room_name not in rooms:
        rooms.append(room_name)
        chat_history[room_name] = []
        emit("room_created", room_name, broadcast=True)
    print(f"Room created: {room_name}")

@socketio.on("join")
def on_join(data):
    room = data["room"].encode('latin1').decode('utf-8')  # 인코딩 수정
    nickname = data["nickname"].encode('latin1').decode('utf-8')  # 인코딩 수정
    join_room(room)
    print(f"{nickname} joined {room}")
    if room in chat_history:
        print(f"Sending chat history for {room}: {chat_history[room]}")
        emit("chat_history", chat_history[room], room=request.sid)

@socketio.on("chat")
def event_handler(json):
    room = json["room"].encode('latin1').decode('utf-8')  # 인코딩 수정
    nickname = json["nickname"].encode('latin1').decode('utf-8')  # 인코딩 수정
    message = json["message"].encode('latin1').decode('utf-8')  # 인코딩 수정
    chat_record = {"nickname": nickname, "message": message}
    if room in chat_history:
        chat_history[room].append(chat_record)
    print(f"Received chat message in {room}: {chat_record}")
    emit("response", chat_record, room=room)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=14000, debug=True)
