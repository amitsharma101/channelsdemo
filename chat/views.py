# chat/views.py
from django.shortcuts import render
from channels_presence.models import Room, Presence

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