from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import random

app = Flask(__name__)
socketio = SocketIO(app)

# Store waiting users for random pairing
waiting_users = set()

@app.route('/')
def index():
    return render_template('index.html')

# Random Chat Connection
@socketio.on('join_random')
def handle_join_random():
    global waiting_users
    if len(waiting_users) > 0:
        # Pair with a waiting user
        partner = waiting_users.pop()
        room = f"random_{random.randint(1000, 9999)}"
        join_room(room)
        emit('join_room', room, to=request.sid)
        emit('join_room', room, to=partner)
    else:
        # No one waiting, add to waiting list
        waiting_users.add(request.sid)

@socketio.on('leave_random')
def handle_leave_random():
    waiting_users.discard(request.sid)

# Room-based Chat Connection
@socketio.on('join_room')
def handle_join_room(room):
    join_room(room)
    emit('message', f"User {request.sid} has joined the room {room}.", to=room)

@socketio.on('leave_room')
def handle_leave_room(room):
    leave_room(room)
    emit('message', f"User {request.sid} has left the room {room}.", to=room)

# WebRTC signaling
@socketio.on('offer')
def handle_offer(data):
    emit('offer', data, to=data['room'])

@socketio.on('answer')
def handle_answer(data):
    emit('answer', data, to=data['room'])

@socketio.on('ice_candidate')
def handle_ice_candidate(data):
    emit('ice_candidate', data, to=data['room'])

if __name__ == '__main__':
    socketio.run(app, debug=True)
