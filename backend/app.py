from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO
from bot import run_bot, message_queue, Session, Message
import threading
import queue
import os

template_folder = os.path.abspath('frontend/build')

app = Flask(__name__, static_folder='../frontend/build', static_url_path='/', template_folder=template_folder)
app.config['SECRET_KEY'] = 'will_be_set_later'

socketio = SocketIO(app)

@app.route('/')
def index():
    session = Session()
    messages = session.query(Message).all()
    session.close()

    # Convert messages to a list of dictionaries
    messages_data = [{'amount': msg.amount, 'author': msg.author, 'latestTimeStamp': msg.latestTimeStamp} for msg in messages]

    return render_template('index.html', initial_messages=messages_data)

@app.route('/initial-messages')
def get_initial_messages():
    session = Session()
    leaderboard = session.query(Message).order_by(Message.amount.desc()).all()
    session.close()

    leaderboard_data = [{'author': msg.author, 'amount': msg.amount, 'latestTimeStamp': msg.latestTimeStamp} for msg in leaderboard]
    return jsonify(leaderboard_data)

def emit_messages():
    while True:
        try:
            data = message_queue.get(timeout=1)
            if 'leaderboard' in data:
                socketio.emit('leaderboard_update', data['leaderboard'])
        except queue.Empty:
            continue

if __name__ == '__main__':
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()

    emitter_thread = threading.Thread(target=emit_messages)
    emitter_thread.start()

    socketio.run(app, debug=False)  # Consider disabling debug mode in production
