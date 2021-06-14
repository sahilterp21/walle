import requests
import json
import random
import pandas as pd
import time
'My Drive'

'CareersInPlay/Game Technology/Test Data'
# import os
# from pathlib import Path
# from dotenv import load_dotenv
# env_path = Path(".") / ".env"
# load_dotenv(dotenv_path=env_path)

webhook_ds = 'https://hooks.slack.com/services/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'
webhook_pio = 'https://hooks.slack.com/services/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'  # os.environ['SUPRV_PIO_WH']
webhook_ph = 'https://hooks.slack.com/services/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'
webhook_pw = 'https://hooks.slack.com/services/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'
required_agent = {
    "in": " Inspector is needed to respond to the situation.",
    "re": ' Reporter is needed for the job.',
    "po": " Police Bus needed at the spot.",
    "am": " Please call an Ambulance.",
    "wt": " Work Truck is required at the location.",
    "ft": "Fire Truck is needed at the earliest."
}

token_selection = {
    "am": webhook_ph,
    "re": webhook_pio,
    "wt": webhook_pw,
    "in": webhook_ds,
    "ft": webhook_ph,
    "po": webhook_pw,
    "ds": webhook_ds,
    "pio": webhook_pio,
    "pw": webhook_pw,
    "ph": webhook_ph
}


# ===============================================================================================================

def getmessages(token, location):
    location_caselets = caselets[caselets["Neighborhood"] == int(location)]
    if token.lower() == "in":  # data scientist
        relevant_caselets = (
                    location_caselets[location_caselets["IN"] == "X"]["Description"] + required_agent[token]).to_list()
    elif token.lower() == "re":  # pio
        relevant_caselets = (
                    location_caselets[location_caselets["RE"] == "X"]["Description"] + required_agent[token]).to_list()
    elif token.lower() == "wt":  # public works
        relevant_caselets = (
                    location_caselets[location_caselets["WT"] == "X"]["Description"] + required_agent[token]).to_list()
    elif token.lower() == "po":  # public works
        relevant_caselets = (
                    location_caselets[location_caselets["PO"] == "X"]["Description"] + required_agent[token]).to_list()
        # relevant_caselets = (location_caselets[(location_caselets["PO"] == "X") | (location_caselets["WT"] == "X")]["Description"]+ required_agent[token]).to_list()
    elif token.lower() == "am":  # public health
        relevant_caselets = (
                    location_caselets[location_caselets["AM"] == "X"]["Description"] + required_agent[token]).to_list()
    elif token.lower() == "ft":  # public health
        relevant_caselets = (
                    location_caselets[location_caselets["FT"] == "X"]["Description"] + required_agent[token]).to_list()
    else:
        print("INVALID token:", token)
    return relevant_caselets


def asset_neigh_message(token, location):
    token_id = token.upper()
    ident = []
    location_identifier = caselets[caselets["Neighborhood"] == int(location)]
    rel_message = (location_identifier[location_identifier[token_id] == "X"]["Description"]).to_list()
    for i in range(len(rel_message)):
        id_list = caselets[caselets["Description"] == rel_message[i]]
        form_id = id_list["Asset Code"].to_list()
        ident.append(form_id[0])
    # print(ident)
    return ident


def getassetmessages(token, location):
    agnt_slct = ["AM", "RE", "WT", "IN", "FT", "PO"]
    location_caselets = caselets[caselets["Asset Code"] == location]["Description"].to_list()
    for i in range(len(agnt_slct)):
        for j in range(0, len(location_caselets)):
            testlist = caselets[caselets["Description"] == location_caselets[j]]
            test_token = (testlist[agnt_slct[i]]).to_list()
            if test_token:
                if test_token[0] == "X":
                    token_sel = agnt_slct[i].lower()
                    loc_caselets = (caselets[caselets["Asset Code"] == location]["Description"] + required_agent[
                        token_sel]).to_list()
                    return loc_caselets
            else:
                return location_caselets

            # else:
            # print("No relevant messages for the given asset")

    # loc_caselets =  (caselets[caselets["Asset Code"] == location]["Description"]+required_agent[token_sel]).to_list()
    # testlist = caselets[caselets["Description"] == location_caselets[0]]
    # print("test List: ", str(testlist["AM"]))
    # print(type(str(testlist["AM"])))


def specialmessage(input):
    if input[1] not in Specialmessages:
        print("Malformed special message request")
        return
    messages = Specialmessages[input[1]]
    recipientinf = input[1].split("-")
    for message in messages:
        data = {"text": message}
        print("MESSAGE FOR: ", recipientinf[0], "=", message)
        print(requests.post(token_selection[recipientinf[0]], json.dumps(data)))


def playermove(token, location):
    if location.isnumeric():
        messagelist = getmessages(token, location)
        for i in range(len(messagelist)):
            asset_loc = asset_neigh_message(token, location)
            # print(asset_messages)
            data = {
                "text": "Neighborhood: " + location + ". " + messagelist[i] + " Location identified as: " + asset_loc[i]
                # asset added to role's messages
            }
            print(requests.post(token_selection[token], json.dumps(data)))
            time.sleep(1)
        # Call the API HERE <<<<<<
        othertokens = Tokens
        othertokens.remove(token)  # list of tokens not including the one that moved
        messagelist = getmessages(random.choice(othertokens), location)
        for i in range(len(messagelist)):  # --Messages for other roles
            data = {
                "text": messagelist[i]
            }
            print(requests.post(token_selection[token], json.dumps(data)))
            time.sleep(1)
    else:
        asset_messages = getassetmessages(token, location)
        if asset_messages:
            for i in range(len(asset_messages)):
                if type(asset_messages[i]) == str:
                    data = {
                        "text": location + ": " + asset_messages[i]
                    }
                    print(requests.post(token_selection[token], json.dumps(data)))
        else:
            print("Message not found!!")


def loadlocations():
    filename = "Locations.csv"
    try:
        file = open(filename, 'r')
    except:
        print('Error: file not found', file_name)
        return
    try:
        fileData = file.read().split()
    except:
        print('Error: file cannot be read: ', file_name)
    return fileData


def loadspecialmessages():
    filename = "specialmessages.csv"
    try:
        file = open("specialmessages.csv", encoding='utf-8')
    except:
        print('Error: file not found: ', filename)
        return
    try:
        filelines = file.readlines()
    except Exception as e:
        print('Error: file cannot be read: ', filename)
        print('Error: file cannot be read: ', e)
    fileData = {}
    for line in filelines:
        lineparts = line.split(",")
        linekey = lineparts[0]
        if linekey not in fileData:
            msglist = []
            msglist.append(lineparts[2])
            fileData[linekey] = msglist
        else:
            msglist = fileData[linekey]
            msglist.append(lineparts[2])
            fileData[linekey] = msglist
    return fileData


def resolvecaselet(location, token):
    indexes = caselets.index[caselets['Asset Code'] == location].tolist()
    # indexes=caselets.index[caselets['Asset Code'] == location & caselets['AM']=='X'].tolist()
    for index in indexes:
        caselets.at[index, 'Resolved'] = 'X'


# ===================================================================================================================


Tokens = ["am", "re", "wt", "in", "ft", "po"]
Locations = loadlocations()
Specialmessages = loadspecialmessages()
caselets = pd.read_csv('Playtest 3-Caselets - Design Test.csv')
# print(caselets[caselets["Neighborhood"]])
# residents = pd.read_csv('New Bronze Falls Asset Details - Residents.csv')
# messages = pd.read_csv('CIP_Message_templates.csv')
# msglist=messages['msgtext'].to_list()

# print(caselets)
# ----loop through random iterations
# pio_feed = caselets["Description"].dropna().to_list()
# pio_del = []


Tokens = ["am", "re", "wt", "in", "ft", "po"]

while True:

  userinput = input("Enter Token code/location for move or done to end: ")
  if userinput.lower() == "done":
    break
  print('-----------------------')
  if   "/" not in userinput:
    print("invalid input, XX/loc for move, loc/XX for resolution")
    break
  usercommand = userinput.split("/")
  if  usercommand[0].lower() in Tokens: #This is a player move
    print("valid token move")
    if usercommand[1].lower() in Locations:
      playermove(usercommand[0].lower(), usercommand[1].lower())
    else:
      print("Invalid location, try again:", usercommand[1].lower())
      continue
  elif usercommand[1].lower() in Tokens: #This is a case resolution
    print("valid token resolve")
    if usercommand[0].lower() in Locations:
      print ("resolution")
    else:
      print("Invalid location, try again:", usercommand[0].lower())
      continue
  elif usercommand[0] == "*": #special messages
      specialmessage(usercommand)
  else:
    print ("invalid option:", userinput," ", usercommand)
    continue
caselets.to_csv(r'gamefile-Design Test.csv', index = False)
print("DEMO FINISHED")