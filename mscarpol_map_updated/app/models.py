from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    location = db.Column(db.String(200), nullable=False)

class ChatRoom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    host = db.Column(db.String(20), db.ForeignKey('user.username'), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    members = db.Column(db.Text, nullable=True)  # 새로운 members 필드 추가
    chat_logs = db.relationship('ChatLog', backref='room', lazy=True, cascade="all, delete-orphan")

class ChatLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    room_name = db.Column(db.String(100), db.ForeignKey('chat_room.title'), nullable=False)
    username = db.Column(db.String(20), db.ForeignKey('user.username'), nullable=False)
