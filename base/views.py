from django.shortcuts import render
from django.http import HttpResponse
from .models import Room

room = [
    {'id':1, 'name':"python"},
    {'id':2, 'name':"js"},
    {'id':3, 'name':"django"},

]

# Create your views here.
def home(request):
    rooms = Room.objects.all()
    context = {'rooms':rooms}
    return render(request, 'base/home.html', context)

def room(request, pk):
    room = Room.objects.get(id=pk)
    context = {'room':room}
    return render(request, 'room.html', context)

def create_room(request):
    context = {}
    return render(request, 'base/room_form.html', context)