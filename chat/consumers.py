# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async
import time
from urllib.parse import parse_qs
from rest_framework.authtoken.models import Token


def current_milli_time():
    return round(time.time() * 1000)


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # print(self.scope['query_string'])
        params = parse_qs(self.scope["query_string"].decode())
        token = params['param'][0]
        print(token)

        # tkn = await self.get_token(token)
        try:
            tkn = await self.get_token(token)
            print(tkn)
            user = await self.get_user(tkn)

            print(user)

            if user:
                self.room_group_name = 'chat_%s' % self.room_name

                # Join room group
                await self.channel_layer.group_add(
                    self.room_group_name,
                    self.channel_name
                )

                print("In COnnect")

                await self.accept()
            else:
                print("Token Expired or not found")
        except:
            pass

    @database_sync_to_async
    def get_token(self,token):
        return Token.objects.get(key=token)

    @database_sync_to_async
    def get_user(self,token):
        return token.user

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

        print(message)

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

        params = parse_qs(self.scope["query_string"].decode())
        token = params['token'][0]
        print("Got the Token : "+token)

        try:
            tokenFromDB = await self.get_token(token)
            userFromDB = await self.get_user(tokenFromDB)

            if userFromDB:
                print("User Verified..Connecting...")
                await self.accept()
            else:
                print("Token Expired or not found")
        except:
            pass

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

    @database_sync_to_async
    def get_token(self,token):
        return Token.objects.get(key=token)

    @database_sync_to_async
    def get_user(self,token):
        return token.user

def processLogic(cardId):
    if cardId == "12345":
        return (True,"Card " + cardId + " - Access Granted")
    else : 
        return (False,"Card " + cardId + " - Access Denied")