import numpy as np
from sklearn.cluster import KMeans
from flask import render_template, url_for, flash, redirect, request, jsonify
from app import app, db, socketio
from app.forms import RegistrationForm, LoginForm
from app.models import User, ChatRoom, ChatLog
from flask_login import login_user, current_user, logout_user, login_required
from flask_socketio import send, join_room, leave_room, emit

@app.route('/')
@app.route('/index')
def index():
    filtered_rooms = []
    if current_user.is_authenticated and current_user.location:
        user_location = list(map(float, current_user.location.split(',')))
        rooms = ChatRoom.query.all()
        for room in rooms:
            room_location = list(map(float, room.location.split(',')))
            if np.linalg.norm(np.array(user_location) - np.array(room_location)) < 0.5:  # 위치 차이 기준을 0.5로 설정
                filtered_rooms.append(room)
    else:
        filtered_rooms = ChatRoom.query.all() if current_user.is_authenticated else []

    return render_template('index.html', rooms=filtered_rooms)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, password=form.password.data, location=form.location.data)
        db.session.add(user)
        db.session.commit()
        flash('회원가입이 완료되었습니다!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            next_page = request.args.get('next')
            flash('로그인에 성공했습니다.', 'success')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('로그인에 실패했습니다. 아이디와 비밀번호를 확인해주세요.', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash('로그아웃되었습니다.', 'info')
    return redirect(url_for('index'))

@app.route('/create_room', methods=['GET', 'POST'])
@login_required
def create_room():
    if request.method == 'POST':
        title = request.form['title']
        location = current_user.location
        room = ChatRoom(title=title, host=current_user.username, location=location, members=current_user.username)
        db.session.add(room)
        db.session.commit()
        flash('채팅방이 생성되었습니다!', 'success')
        return redirect(url_for('index'))
    return render_template('create_room.html')

@app.route('/chat/<int:room_id>')
@login_required
def chat_room(room_id):
    room = ChatRoom.query.get_or_404(room_id)
    if room:
        if current_user.username not in room.members.split(','):
            room.members += f",{current_user.username}"
            db.session.commit()
        return render_template('chat_room.html', room=room)
    else:
        flash('채팅방을 찾을 수 없습니다.', 'danger')
        return redirect(url_for('index'))

@app.route('/search', methods=['GET'])
@login_required
def search():
    query = request.args.get('query')
    rooms = ChatRoom.query.filter(ChatRoom.title.contains(query)).all()
    return render_template('search_results.html', rooms=rooms)

@socketio.on('send_message')
def handle_send_message(data):
    room = ChatRoom.query.filter_by(title=data['room']).first()
    if room:
        msg = data['msg']
        chat_log = ChatLog(content=msg, room_name=room.title, username=current_user.username)
        db.session.add(chat_log)
        db.session.commit()
        emit('receive_message', {'msg': f"{current_user.username}: {msg}"}, room=room.title)

@socketio.on('join')
def on_join(data):
    room = data['room']
    join_room(room)
    # 방에 입장할 때 채팅 기록 전송
    room_obj = ChatRoom.query.filter_by(title=room).first()
    chat_logs = [{'username': log.username, 'content': log.content} for log in room_obj.chat_logs]
    emit('load_chat_logs', chat_logs, room=room)

@socketio.on('leave')
def on_leave(data):
    room = data['room']
    leave_room(room)

@app.route('/delete_room/<int:room_id>', methods=['POST'])
@login_required
def delete_room(room_id):
    room = ChatRoom.query.get_or_404(room_id)
    if room.host == current_user.username:
        db.session.delete(room)
        db.session.commit()
        flash('채팅방이 삭제되었습니다.', 'success')
    else:
        flash('채팅방을 삭제할 권한이 없습니다.', 'danger')
    return redirect(url_for('index'))

@app.route('/auto_match', methods=['POST'])
@login_required
def auto_match():
    users = User.query.all()
    locations = []
    user_ids = []

    for user in users:
        if user.location:
            lat, lon = map(float, user.location.split(','))
            locations.append([lat, lon])
            user_ids.append(user.id)

    if len(locations) < 2:
        flash('매칭을 위한 사용자가 부족합니다.', 'warning')
        return jsonify({'success': False, 'message': '매칭을 위한 사용자가 부족합니다.'})

    kmeans = KMeans(n_clusters=2).fit(locations)
    labels = kmeans.labels_

    matched_users = []
    for label in set(labels):
        group = [user_ids[i] for i in range(len(user_ids)) if labels[i] == label]
        if current_user.id in group:
            distances = [np.linalg.norm(np.array(locations[i]) - np.array([float(x) for x in current_user.location.split(',')])) for i in range(len(user_ids)) if labels[i] == label]
            sorted_users = sorted(zip(distances, group))[:4]
            matched_users = [user for _, user in sorted_users]
            break

    if len(matched_users) < 2:
        flash('적절한 매칭을 찾지 못했습니다.', 'info')
        return jsonify({'success': False, 'message': '적절한 매칭을 찾지 못했습니다.'})

    # 채팅방 생성
    room_title = f"{current_user.username}의 자동 매칭 방"
    matched_usernames = [User.query.get(uid).username for uid in matched_users]
    members = ",".join(matched_usernames)
    new_room = ChatRoom(title=room_title, host=current_user.username, location=current_user.location, members=members)
    db.session.add(new_room)
    db.session.commit()

    flash(f'새로운 채팅방이 생성되었습니다: {room_title}', 'success')
    return jsonify({'success': True, 'redirect_url': url_for('chat_room', room_id=new_room.id)})

@app.route('/edit_room_title/<int:room_id>', methods=['POST'])
@login_required
def edit_room_title(room_id):
    room = ChatRoom.query.get_or_404(room_id)
    if room.host == current_user.username:
        new_title = request.form['new_title']
        room.title = new_title
        db.session.commit()
        flash('채팅방 제목이 변경되었습니다.', 'success')
    else:
        flash('채팅방 제목을 변경할 권한이 없습니다.', 'danger')
    return redirect(url_for('chat_room', room_id=room_id))
