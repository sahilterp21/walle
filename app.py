from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, join_room, leave_room, close_room
import time

from db import get_messages, save_message
from flassger_api import send_message

app = Flask(__name__)
socketio = SocketIO(app)

roles ={
    "DS": "Data Scientist",
    "PW": "Public Works",
    "PH": "Public Health",
    "PIO": "Public Information Officer"
}

announcement_data = {
    "username": "",
    "role": ""
}

nicknames = []
socket_id = []

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api_response')
def api_response():
    return roles

@app.route("/invalid_role")
def invalid_role():
    return render_template('invalid_role_selection.html')

@app.route("/chat")
def chat():
    team_id = request.args.get("team_id").upper()
    role = request.args.get("role").upper()

    if team_id and role:
        time.sleep(1)
        if role+team_id not in nicknames:
            messages = get_messages(role, team_id)

            return render_template('chat.html', team_id = team_id, role = role, role_display = roles[role.upper()], messages=messages)


        elif role+team_id in nicknames:
            #return redirect(url_for('invalid_role'))

            return render_template('invalid_role_selection.html', team_id=team_id, role=role)

    else:
        return redirect(url_for('home'))

@socketio.on('join_role')
def handle_join_role(data):
    app.logger.info("{} has joined team-{}".format(data['role'], data['team_id']))
    print(data['team_id'])
    print(request.sid)
    join_room(data['team_id'])
    announcement_data['role'] = roles[data['role'].upper()]
    socket_id.append(request.sid)
    nicknames.append(data['role']+data['team_id'])
    print(socket_id,"\n", nicknames)
    socketio.emit('join_room_announcement', announcement_data, room=request.sid)

@socketio.on('send_message')
def handle_send_message(data):
     #app.logger.info("{} has sent a message to role {}: {}".format(data['username'],data['role'], data['message']))
    message = data['message']
    print(data)
    msg_list = message.split()
    print(msg_list)
    receiver =message.split(' ',1)[0].replace("@","").upper()
    sender = data['role']+ data['team_id']
    if receiver+data['team_id'] in nicknames:

        index_dest = nicknames.index(receiver + data['team_id'])
        index_src = nicknames.index(sender)
        dest = socket_id[index_dest]
        src = socket_id[index_src]
        #data['message'] = message.split(' ',1)[1]
        #save_message(data['role'],data['message'],receiver,data['team_id'])
        #send_message(data['role'],data['message']) ##make changes if needed for POST
        socketio.emit('receive_message', data, room=dest)
        socketio.emit('receive_message', data, room=src)


    elif receiver == "ALL":
        role_temp = ["DS", "PIO", "PW", "PH"]
        #data['message'] = message.split(' ',1)[1]
        #print(message)
        for temp in role_temp:
            if temp+data['team_id'] in nicknames:
                index_dest = nicknames.index(temp + data['team_id'])
                dest = socket_id[index_dest]
                #send_message(data['role'], data['message'])  ##make changes if needed for POST
                socketio.emit('receive_message', data, room=dest) ##
            else:
                pass
        ##save_message(data['role'],data['message'],receiver,data['team_id'])


    else:
        index_src = nicknames.index(sender)
        src = socket_id[index_src]
        data['message'] = 'Destination Unreachable or Message Format Incorrect'
        data['role'] = 'Server Response'
        socketio.emit('receive_message', data,room=src)




@socketio.on('leave_room')
def handle_leave_room_event(data):
    app.logger.info("{} has left the team- {}".format(data['role'], data['team_id']))
    leave_room(data['team_id'])
    print(nicknames)
    print(socket_id)
    leaver_index = nicknames.index(data['role']+data['team_id'])
    socket_id.remove(socket_id[leaver_index])
    nicknames.remove(data['role']+data['team_id'])
    print(nicknames)
    print(socket_id)
    #socketio.emit('leave_room_announcement', data, room=data['room'])


if __name__ == '__main__':
    socketio.run(app, debug = True)

