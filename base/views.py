from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User 
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from .models import Room, Topic, Message
from .forms import RoomForm, ProfileUpdateForm

# Create your views here.
def login_user(request):
    page='login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, 'wrong username or password')
    context = {'page':page}
    return render(request, 'base/login_register.html', context)

def logout_user(request):
    logout(request)
    return redirect('home')

def register_user(request):
    form = UserCreationForm()

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "an error occured during registration")
    return render(request, 'base/login_register.html', {'form':form})

def home(request):
    q = request.GET.get('q') if request.GET.get('q') !=None else ''
    rooms = Room.objects.filter(Q(topic__name__icontains=q) | Q(name__icontains=q) | Q(description__icontains=q))
    room_count = rooms.count()
    topics = Topic.objects.all()
    comments = Message.objects.filter(Q(room__topic__name__icontains=q))
    context = {'rooms':rooms, 'topics':topics, 'room_count':room_count, 'room_messages':comments}
    return render(request, 'base/home.html', context)

def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by('-created')
    participants = room.participants.all()

    if request.method == "POST":
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)

    context = {'room':room, 'room_messages':room_messages, 'participants':participants}
    return render(request, 'room.html', context)

@login_required(login_url='login')
def create_room(request):
    form  = RoomForm()
    if request.method == "POST":
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.host = request.user
            form.save()
            return redirect('home')
    context = {'form':form}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def update_room(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)

    if request.user != room.host:
        return HttpResponse("YOU SHALL NOT PASS!!!")

    if request.method == "POST":
        form = RoomForm(request.POST, instance = room)
        if form.is_valid:
            form.save()
            return redirect("home")
    context = {'form': form}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def delete_room(request, pk):
    room = Room.objects.get(id=pk)
    if request.user != room.host:
        return HttpResponse("YOU SHALL NOT PASS!!!")

    if request.method == "POST":
        room.delete()
        return redirect("home")
    return render(request, 'base/delete.html', {'obj':room})

@login_required(login_url='login')
def delete_message(request, pk):
    message = Message.objects.get(id=pk)
    if request.user != message.user:
        return HttpResponse("YOU SHALL NOT PASS!!!")

    if request.method == "POST":
        message.delete()
        return redirect("home")
    return render(request, 'base/delete.html', {'obj':message})

def user_profile(request, pk):
    user = User.objects.get(username=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    return render(request, 'base/profile.html', {"user":user, "rooms":rooms, "room_messages":room_messages, "topics":topics})

@login_required(login_url='login')
def edit_profile(request, pk):
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, instance = request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Updated successfully")
        else:
            messages.error(request, "Something went wrong")
    else:
        form = ProfileUpdateForm(instance = request.user)
    return render(request, 'base/edit_user_profile.html', {"form":form})