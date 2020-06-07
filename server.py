import os
from PIL import Image
from flask import Flask, request, Response, render_template, url_for, session, redirect, escape
from flask_login import logout_user, LoginManager
from flask import send_file
from flask_mail import Mail, Message
from flask_pymongo import PyMongo
import bcrypt
import requests
from flask_socketio import SocketIO
import json
import numpy as np
from datetime import datetime

app = Flask(__name__)
socketio = SocketIO(app)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USERNAME'] = 'xalex1200@gmail.com'
app.config['MAIL_PASSWORD'] = 'Gj6MzmaI'
mail = Mail(app)

app.config['MONGO_DBNAME'] = 'detector'
app.config['MONGO_URI'] = 'mongodb+srv://CN2019:CN2019@cluster0-iklun.gcp.mongodb.net/detector?retryWrites=true&w=majority'

mongo = PyMongo(app)


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST')
    return response


@app.route('/')
def index():
    if 'username' in session:
        user = mongo.db.users.find_one({'username': session['username']})
        return render_template('index.html', username = user['name'])
    else:
        return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    users = mongo.db.users
    login_user = users.find_one({'username': request.form['username']})
    if login_user:
        if bcrypt.hashpw(request.form['pass'].encode('utf-8'), login_user['password'].encode('utf-8')) == login_user['password'].encode('utf-8'):
            session['username'] = request.form['username']
            return redirect(url_for('index'))
    return 'Invalid username or password'


@app.route('/detector')
def detector():
    return render_template('detector.html')


@app.route('/events')
def events():
    detects = mongo.db.detects.find({'username': session['username']})
    events = []
    for item in detects:
        print(str(item['datetime']))
        item['datetime'] = str(item['datetime']).split('.')[0]
        events.append(item)
    return render_template('events.html', events = events)


@app.route('/detection', methods=['POST'])
def detection():
    image_bytes = request.files['image'].read()
    sessionID = request.files['sessionID'].read().decode('utf-8')
    now = datetime.now()

    print("SUBIENDO DATOS")
    detects = mongo.db.detects
    image = np.fromstring(image_bytes, dtype=np.uint8).reshape(720, 1280, 3)
    img = Image.fromarray(image)
    imageTitle = formatTitle(sessionID + str(now))
    img.save('static/detections/' + imageTitle + '.jpg', 'JPEG')
    post = {'username': sessionID, 'datetime': now, 'image': imageTitle + '.jpg'}
    detects.insert_one(post)
    sendMail(sessionID, img)
    return 'ok'


@app.route('/logout')
def logout():
    session.pop(session['username'], None)
    return render_template('login.html')

def formatTitle(title):
    title = title.replace(':', '')
    title = title.replace('.', '')
    title = title.replace(' ', '')
    return title

def sendMail(sessionID, img):
    email = mongo.db.users.find_one({'username': sessionID})['email']
    msg = Message('¡Intruso detectado!', sender="xalex1200@gmail.com", recipients=[email])
    msg.body = 'Se ha detectado un intruso.'
    mail.send(msg)


@socketio.on('mensaje')
def handle_image(mensaje):
    url = 'http://localhost:3000/image'
    image_file = mensaje
    files = {'image': image_file, 'sessionID': session['username']}
    response = requests.post(url, files = files)
    boxes = response.content.decode('utf-8')
    socketio.emit('response', boxes)


if __name__ == '__main__':
    app.secret_key = 'secret'
    socketio.run(app)