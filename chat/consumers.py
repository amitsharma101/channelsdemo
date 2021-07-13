# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.consumer import AsyncConsumer

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
    else : 
        return (False,"Card " + cardId + " - Access Denied")