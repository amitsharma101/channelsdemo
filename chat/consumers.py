# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.consumer import AsyncConsumer
import requests
import json

CLUB_ID = 53821
CLUB_SECRET = 'CS-53821-CHECKIN7622-PHddNeGxUGVPGJsEHKerITdR3'
API_KEY = '3f5bc58a9b6e11eba64b021b958a09b1'

PGYM_CLIENT_ID = "0eb8ea928d354ea18ee78ad0d2879c9c"
PGYM_CLIENT_SECRET = "5b144aee8d604fb893d00971f391d74be0548432c8d14d70b8299b5d86329cb5"
PGYM_BASE_URL = "https://presentation.perfectgym.pl/"

cache = {}

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        print("In COnnect")

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))


class PingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)

        print(type(text_data_json))
        print(text_data_json)

        message = text_data_json['message']

        print(type(message))
        print(message)
        
        

        print()
        print()

        print("Received Card number "+str(message['memberId']))
        print("Verifying Card number "+str(message['memberId']))

        # Send message to WebSocket
        flag,output,outputToSend = processLogic(message)

        if(flag):
            print("User Verified. Sending data back")
        else:
            print("User Not verified Sending data back")

        print()
        print()

       
        await self.send(text_data=json.dumps({
            'message': outputToSend,'canEnter':flag,"memberId": message['memberId']
        }))

# def processLogic(cardId):
#     if cardId == "12345" or cardId == "8901207019234":
#         return (True,"Card " + cardId + " - Access Granted")

#     api_url = "https://virtuagym.com/api/v0/club/"+str(CLUB_ID)+"/devices?club_secret="+CLUB_SECRET+"&api_key="+API_KEY
#     body = {"card_id": cardId, "action": "identification", "application": "All right Now Ltd Custom Check-in","version":"1"}
#     headers =  {"Content-Type":"application/json"}
#     response = requests.put(api_url, data=json.dumps(body), headers=headers)
    
#     res = response.json()
#     print(response.json())
#     print()

#     if(res['statuscode'] in range(200,300)):
#         access = res['result']['open_relay']
#         if access:
#             return (True,"Card " + cardId + " - Access Granted")
#         else:
#             return (False,"Card " + cardId + " - Access Denied")
#     else:
#         return (False,"API Call Failed")




def processLogic(messageJson):
    # messageJson = json.loads(messageJson)

    memberId = messageJson['memberId']
    clubId = messageJson['clubId']

    try:
        acc = cache[(memberId,clubId)]
        if acc:
            return (True,"Card " + str(memberId) + " - Access Granted","Access Granted")
        else:
            return (False,"Card " + str(memberId) + " - Access Denied","Access Denied")
    except:
        pass

    api_url = PGYM_BASE_URL+"api/v2/AccessControl/ValidateMemberVisit"
    body = messageJson
    headers =  {"Content-Type":"application/json","X-Client-Id":PGYM_CLIENT_ID,"X-Client-Secret":PGYM_CLIENT_SECRET}
    response = requests.post(api_url, data=json.dumps(body), headers=headers)
    
    res = response.json()
    print(response.json())
    print()

    if(response.status_code in range(200,300)):
        access = res['canEnter']
        cache[(memberId,clubId)] = access
        if access:
            return (True,"Card " + str(memberId) + " - Access Granted","Access Granted")
        else:
            return (False,"Card " + str(memberId) + " - Access Denied","Access Denied")
    else:
        return (False,"API Call Failed")
        