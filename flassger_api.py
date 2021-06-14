import requests


def send_message(role,message):
    url = "https://api.careersinplay.umd.edu/api/v1/header/messages"
    message_data = {"message_subject": role, "game_position": "1", 'message_text': message}

    response = requests.post(url,data=message_data)
    print(response)
    return response
