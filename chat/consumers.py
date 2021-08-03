# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.consumer import AsyncConsumer
import requests
import json

from channels_presence.models import Room
from channels.db import database_sync_to_async
from channels_presence.decorators import touch_presence

from django.core import serializers
from django.http import JsonResponse


CLUB_ID = 53821
CLUB_SECRET = 'CS-53821-CHECKIN7622-PHddNeGxUGVPGJsEHKerITdR3'
API_KEY = '3f5bc58a9b6e11eba64b021b958a09b1'


class PresenceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'client_%s' % self.room_name

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        print("In COnnect")

        await self.registerConnect()
        # print(Room.objects.all())

        await self.accept()
        

    @database_sync_to_async
    def registerConnect(self):
        Room.objects.add(self.room_name, self.channel_name, self.scope["user"])
        self.printObj(Room.objects.all())

    @database_sync_to_async
    def deRegisterConnect(self):
        Room.objects.remove(self.room_name, self.channel_name)
        self.printObj(Room.objects.all())
        

    def printObj(self,querySet):
        [print(a) for a in querySet]

    async def disconnect(self, close_code):
        # Leave room group

        await self.deRegisterConnect()

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    @touch_presence
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
        message = text_data_json['message']

        print()
        print()

        print("Received Card number "+message)
        print("Verifying Card number "+message)

        # Send message to WebSocket
        flag,output = processLogic(message)

        if(flag):
            print("User Verified. Sending data back")
        else:
            print("User Not verified Sending data back")

        print()
        print()

        await self.send(text_data=json.dumps({
            'message': output
        }))

def processLogic(cardId):

    if cardId == "12345":
        return (True,"Card " + cardId + " - Access Granted")

    api_url = "https://virtuagym.com/api/v0/club/"+str(CLUB_ID)+"/devices?club_secret="+CLUB_SECRET+"&api_key="+API_KEY
    body = {"card_id": cardId, "action": "identification", "application": "All right Now Ltd Custom Check-in","version":"1"}
    headers =  {"Content-Type":"application/json"}
    response = requests.put(api_url, data=json.dumps(body), headers=headers)
    
    res = response.json()
    print(response.json())
    print()

    if(res['statuscode'] in range(200,300)):
        access = res['result']['open_relay']
        if access:
            return (True,"Card " + cardId + " - Access Granted")
        else:
            return (False,"Card " + cardId + " - Access Denied")
    else:
        return (False,"API Call Failed")
        