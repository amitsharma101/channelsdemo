# chat/views.py
from django.shortcuts import render

from channels_presence.models import Room, Presence

from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework.authtoken.models import Token



def index(request):
    return render(request, 'chat/index.html')

def room(request, room_name):
    return render(request, 'chat/room.html', {
        'room_name': room_name
    })

def clientList(request):
    roomsList = Room.objects.all()
    # print(roomsList)
    return render(request, 'clients/clients.html', {
        "rooms":roomsList
    })

def client(request, room_hash):
    room_name, room_id = room_hash.split('+')
    connectedClients = Presence.objects.filter(room_id=room_id)
    return render(request, 'clients/client.html', {
        "connectedclients":connectedClients
    })   

@csrf_exempt
@api_view(['POST'])
@permission_classes((AllowAny,))
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username,password=password)
    if not user:
        return Response({'error':'Invalid Credentials'},status=400)
    
    token, _ = Token.objects.get_or_create(user=user)
    return Response({'token':token.key},status=200)

