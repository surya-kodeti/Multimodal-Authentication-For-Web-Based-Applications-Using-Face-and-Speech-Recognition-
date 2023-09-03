from flask import Flask, Response, json, render_template, request
import os
import cv2
from camera import VideoCamera
from save import VideoCameraSave
import sqlite3
from webbot import Browser 

app = Flask(__name__)

got_names = []


def addDetails(fname, lname, email, username, password, question, answer):
    con = sqlite3.connect("myData.db")
    cur = con.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS Details(fname TEXT, lname TEXT, email TEXT, question TEXT, answer TEXT, username TEXT, password TEXT)')
    cur.execute("INSERT INTO Details VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (fname, lname, email, question, answer, username, password))
    con.commit()
    con.close()

def getDetails(username):
    con = sqlite3.connect("myData.db")
    cur = con.cursor()
    username = str(username)
    result = cur.execute("SELECT question, answer FROM Details WHERE username == '%s'" % username)
    for ques, ans in result:
        print(ques, ans)
        return ques, ans
    return "No Question", "No"


def gen(camera):
    while True:
        frame, names = camera.get_frame()
        global got_names
        flag = 0
        present_list = got_names
        for name in names:
            if "Unknown" in name: 
                continue
            for i in present_list:
                if name in i:
                    flag = 1
                    break
            if flag == 0:
        #         got_names.append({"name": name, "status": "Present"})
                got_names.append(name)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/api/names')
def send_names():
    global got_names
    data = json.dumps(got_names)
    return data

def newEntry(camera, name):
    while True:
        frame = camera.newMember(name)
        yield(b'--frame\r\n'
              b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/add_new', methods=["GET"])
def add_new():
    name = request.args.get('name')
    return Response(newEntry(VideoCameraSave(), name),
    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/welcome', methods=["GET"]) 
def welcome():
    name = request.args.get("userName")
    print(name)
    global got_names
    print(got_names)
    if name in got_names:
        ques, ans = getDetails(name)
        return render_template('welcome.html', name=name, question=ques, answer=ans)
    else:
        return render_template('reject.html')


@app.route('/resetLogin')
def resetLogin():
    global got_names
    got_names = []
    return render_template('login.html')


@app.route('/logout')
def reset_state():
    global got_names
    got_names = []
    return render_template('index.html')


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/storeData', methods=["GET"])
def store():
    fname = str(request.args.get("fname"))
    lname = str(request.args.get("lname"))
    email = str(request.args.get("password"))
    username = str(request.args.get("username"))
    password = str(request.args.get("password"))
    question = str(request.args.get("question"))
    answer = str(request.args.get("answer"))
    addDetails(fname, lname, email, username, password, question, answer)
    return render_template("register_success.html", name=username)

@app.route('/registration_success')
def reg_success():
    return render_template('reg_success.html')


@app.route('/details')
def final_success():
    web = Browser()
    web.go_to('https://livesql.oracle.com/apex/f?p=590:1000') 
    web.click('Sign In')
    web.type('markprom1412@gmail.com' , into='Username')

    web.type('Suryavamsi@888' , into='Password' , id='ssopassword') # specific selection
    web.click('Sign in')
    return render_template('details.html')


@app.route('/fail')
def fail():
    return render_template('reject.html')

@app.route('/')
def index():
    return render_template('index.html')


if __name__ == "__main__":
    from waitress import serve
    serve(app,host='0.0.0.0', port=5050)
