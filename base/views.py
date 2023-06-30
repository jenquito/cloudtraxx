from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm, MyUserCreationForm
from django.core.paginator import Paginator
from . models import Song

# Create your views here.

#rooms = [
#    {'id' : 1, 'name':'Lets learn python!'},
#    {'id' : 2, 'name':'Design with me'},
#    {'id' : 3, 'name':'Frontend Developers'},
#]

def loginPage(request):

    page = 'login'

    if request.user.is_authenticated:
        return redirect('Home')

    if request.method == 'POST':
        email=request.POST.get('email').lower()
        password=request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, 'User does not exist')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('Home')
        else:
            messages.error(request, 'Username OR password does not exist')

    context = {'page' : page}
    return render(request, 'base/login_register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('Home')


def registerPage(request):
    form = MyUserCreationForm()

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)        #commit to false to access the user created and access that said user right away
            user.username = user.username.lower() #clean user data to be lowecase regardless of its creation
            user.save()
            login(request,user)                   #log in user after creation
            return redirect('Home')               #send them to home page
        else:                                     #flash message when an error had been thrown
            messages.error(request, 'An error has occurred during registration') 

    return render(request, 'base/login_register.html', {'form' : form})

def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q) 
    )

    topics = Topic.objects.all()
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))

    context = {'rooms' : rooms, 'topics' : topics, 'room_count' : room_count, 'room_messages' : room_messages}
    return render(request, 'base/home.html', context)

@login_required(login_url='login')                  #login or register to view
def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by('-created')
    participants = room.participants.all()

    if request.method == 'POST':
        message = Message.objects.create(
            user = request.user,
            room = room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('Room', pk=room.id)

    context = {'room' : room, 'room_messages' : room_messages, 'participants' : participants}
    return render(request, 'base/room.html', context)

def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user' : user , 'rooms' : rooms, 
               'room_messages' : room_messages, 'topics' : topics}
    return render(request, 'base/profile.html', context)


@login_required(login_url='login')                  #login or register to access
def createRoom(request):                            #create room for content
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == "POST":
       topic_name=request.POST.get('topic')
       topic, created = Topic.objects.get_or_create(name = topic_name)
       
       Room.objects.create(
           host=request.user,
           topic=topic,
           name=request.POST.get('name'),
           description=request.POST.get('description'),
       )
       return redirect('Home')
    
    context = {'form' : form, 'topics' : topics }
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')                  #login or register to access
def updateRoom(request,pk):                         #update content of the room
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    if request.user != room.host:
        return HttpResponse('Invalid Room Request')

    if request.method == 'POST':
        topic_name=request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name = topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('Home')

    context = {'form':form, 'topics':topics, 'room':room}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')                  #login or register to access
def deleteRoom(request,pk):                         #delete room when logged in
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('Invalid Room Request')

    if request.method == 'POST':
        room.delete()
        return redirect('Home')
    return render(request, 'base/delete.html', {'obj':room})

@login_required(login_url='login')                  #login or register to access
def deleteMessage(request,pk):                         #delete room when logged in
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse('Invalid Request')

    if request.method == 'POST':
        message.delete()
        return redirect('Home')
    return render(request, 'base/delete.html', {'obj':message})

@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST' :
        form = UserForm(request.POST, request.FILES, instance = user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)

    return render(request, 'base/update-user.html', {'form':form})

@login_required(login_url='login')
def index(request):
    paginator= Paginator(Song.objects.all(),1)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context={"page_obj":page_obj}
    return render(request,"index.html",context)