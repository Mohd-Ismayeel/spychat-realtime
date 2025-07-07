from flask import Flask, render_template, request, redirect, url_for, session, flash
from utils import encode_message, decode_message
from metadata import encrypt_metadata, identify_cipher_from_metadata
from functools import wraps
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.secret_key = 'spychat-secret-key'
socketio = SocketIO(app)

users = {'spy1': 'pass', 'spy2': 'pass'}
messages = []

# ---------- Decorator ----------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ---------- Routes ----------
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
            session['username'] = username
            return redirect(url_for('chat'))
        else:
            flash("Invalid username or password")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users:
            flash("Username already exists")
        else:
            users[username] = password
            flash("Registration successful! Please login.")
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("Logged out successfully.")
    return redirect(url_for('login'))

@app.route('/chat')
@login_required
def chat():
    return render_template('chat.html', username=session['username'], messages=messages)

@app.route('/encode', methods=['POST'])
@login_required
def encode():
    message = request.form['message']
    method = request.form['method']
    encoded = encode_message(method, message)
    metadata_hash, display_code = encrypt_metadata(method)
    full_message = f"{metadata_hash}:: {encoded}"
    return render_template(
        'chat.html',
        username=session['username'],
        messages=messages,
        preview_message=full_message,
        metadata_preview=metadata_hash,
        preview_code=display_code
    )

@app.route('/send', methods=['POST'])
@login_required
def send():
    full_message = request.form['encoded']
    sender = session['username']
    if '::' not in full_message:
        flash("Invalid message format.")
        return redirect(url_for('chat'))

    metadata, encoded_msg = full_message.split('::', 1)
    cipher_method, display_code = identify_cipher_from_metadata(metadata.strip())

    msg_data = {
        'sender': sender,
        'encoded': encoded_msg.strip(),
        'metadata': metadata.strip(),
        'cipher_method': cipher_method,
        'display_code': display_code,
        'decoded': ''
    }
    messages.append(msg_data)
    socketio.emit('receive_message', msg_data, broadcast=True)
    return redirect(url_for('chat'))

@app.route('/decode', methods=['POST'])
@login_required
def decode():
    encoded_msg = request.form['encoded']
    method = request.form['method']
    try:
        decoded_msg = decode_message(method, encoded_msg)
    except Exception as e:
        decoded_msg = f"[Error: {str(e)}]"

    for msg in messages:
        if msg['encoded'] == encoded_msg:
            msg['decoded'] = decoded_msg
            break

    return redirect(url_for('chat'))

@socketio.on('send_message')
def handle_send_message(data):
    print(f"[{data['sender']}] {data['encoded']}")
    emit('receive_message', data, broadcast=True)

import os
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

