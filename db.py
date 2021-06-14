from bson import ObjectId
from pymongo import MongoClient

client = MongoClient("api link")

chat_db = client.get_database("chatDB")
user_messages = chat_db.get_collection('messages')


def save_message(sender, message_text, receiver, team_id):
    user_messages.insert_one({"receiver":receiver,"sender": sender,"message_text":message_text,'team_id':team_id})


def get_messages(receiver,team_id):
    messages = list(user_messages.find({'$or': [{'sender': receiver,'team_id':team_id}, {'receiver': receiver,'team_id':team_id}]}))
    return messages


