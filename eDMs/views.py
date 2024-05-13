from sqlite3 import IntegrityError
from django.db.models import Q
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, logout, login
from .models import *

# Create your views here.

def index(request):
    return render(request, 'index.html')

def registration(request):
    error = ""
    if request.method == "POST":
        firstName = request.POST.get('firstName')
        lastName = request.POST.get('lastName')
        emailid = request.POST.get('emailid')
        password = request.POST.get('Password')
        mobileNumber = request.POST.get('mobileNumber')

        try:
            # Create user
            user = User.objects.create_user(username=emailid, password=password, first_name=firstName, last_name=lastName)
            # Create associated Signup object
            signup = Signup.objects.create(user=user, mobileNumber=mobileNumber)
            error = "no"
        except IntegrityError:
            error = "yes"
    return render(request, 'registration.html', {'error': error})

def user_login(request):
    error = ""
    if request.method == 'POST':
        email = request.POST.get('emailid')
        password = request.POST.get('password')
        user = authenticate(username=email, password=password)
        if user:
            login(request, user)
            return redirect('user_home')
        else:
            error = "yes"
    return render(request, 'user_login.html', {'error': error})

def user_home(request):
    if not request.user.is_authenticated:
        return redirect('user_login')

    try:
        signup = Signup.objects.get(user=request.user)
        totalcategory = Category.objects.filter(signup=signup).count()
        totalnotes = Notes.objects.filter(signup=signup).count()
        categories = Category.objects.filter(signup=signup)
        notes = Notes.objects.filter(category__in=categories)
    except Signup.DoesNotExist:
        return redirect('registration')  # Redirect to registration if signup info doesn't exist

    return render(request, 'user_home.html', {'totalcategory': totalcategory, 'totalnotes': totalnotes, 'notes': notes})

def manageCategory(request):
    if not request.user.is_authenticated:
        return redirect('user_login')
    user = User.objects.get(id=request.user.id)
    signup = Signup.objects.get(user=user)
    category = Category.objects.filter(signup=signup)

    if request.method == "POST":
        categoryName = request.POST['categoryName']
        try:
            Category.objects.create(signup=signup, categoryName=categoryName)
            error = "no"
        except:
            error = "yes"
    return render(request, 'manageCategory.html', locals())

def editCategory(request,pid):
    if not request.user.is_authenticated:
        return redirect('user_login')
    category = Category.objects.get(id=pid)
    error = ""
    if request.method == "POST":
        categoryName = request.POST['categoryName']

        category.categoryName = categoryName

        try:
            category.save()
            error = "no"
        except:
            error = "yes"
    return render(request, 'editCategory.html', locals())

def deleteCategory(request,pid):
    if not request.user.is_authenticated:
        return redirect('user_login')
    category = Category.objects.get(id=pid)
    category.delete()
    return redirect('manageCategory')

def manageNotes(request):
    if not request.user.is_authenticated:
        return redirect('user_login')
    user = User.objects.get(id=request.user.id)
    signup = Signup.objects.get(user=user)
    category = Category.objects.filter(signup=signup)

    notes = Notes.objects.filter(Q(category__in=category))

    if request.method == "POST":
        cid = request.POST['category']
        categoryid = Category.objects.get(id=cid)

        noteTitle = request.POST['noteTitle']
        noteDescription = request.POST['noteDescription']

        try:
            Notes.objects.create(signup=signup, category=categoryid, noteTitle=noteTitle, noteDescription=noteDescription)
            error = "no"
        except:
            error = "yes"
    return render(request, 'manageNotes.html', locals())

def editNotes(request,pid):
    if not request.user.is_authenticated:
        return redirect('user_login')
    notes = Notes.objects.get(id=pid)
    user = User.objects.get(id=request.user.id)
    signup = Signup.objects.get(user=user)
    category = Category.objects.filter(signup=signup)

    if request.method == "POST":
        cid = request.POST['category']
        categoryid = Category.objects.get(id=cid)

        noteTitle = request.POST['noteTitle']
        noteDescription = request.POST['noteDescription']

        notes.category = categoryid
        notes.noteTitle = noteTitle
        notes.noteDescription = noteDescription

        try:
            notes.save()
            error = "no"
        except:
            error = "yes"
    return render(request, 'editNotes.html', locals())

def viewNotes(request,pid):
    if not request.user.is_authenticated:
        return redirect('user_login')
    notes = Notes.objects.get(id=pid)
    user = User.objects.get(id=request.user.id)
    signup = Signup.objects.get(user=user)

    noteshistory = Noteshistory.objects.filter(signup=signup)

    if request.method == "POST":
        noteDetails = request.POST['noteDetails']

        try:
            Noteshistory.objects.create(note=notes, signup=signup, noteDetails=noteDetails)
            error = "no"
        except:
            error = "yes"
    return render(request, 'viewNotes.html', locals())

def deleteNotesHistory(request,pid):
    noteshistory = Noteshistory.objects.get(id=pid)
    noteshistory.delete()
    return redirect('manageNotes')

def deleteNotes(request,pid):
    if not request.user.is_authenticated:
        return redirect('user_login')
    notes = Notes.objects.get(id=pid)
    notes.delete()
    return redirect('manageNotes')

def searchNotes(request):
    if not request.user.is_authenticated:
        return redirect('user_login')
    user = User.objects.get(id=request.user.id)
    signup = Signup.objects.get(user=user)

    sd = None
    if request.method == 'POST':
        sd = request.POST['search']
    try:
        notes = Notes.objects.filter(Q(noteTitle__icontains=sd))
    except:
        notes = ""
    return render(request, 'searchNotes.html', locals())


def profile(request):
    if not request.user.is_authenticated:
        return redirect('user_login')
    error = ""
    user = User.objects.get(id=request.user.id)
    signup = Signup.objects.get(user=user)

    if request.method == "POST":
        fname = request.POST['firstName']
        lname = request.POST['lastName']
        mob = request.POST['mobileNumber']

        signup.user.first_name = fname
        signup.user.last_name = lname
        signup.mobileNumber = mob

        try:
            signup.save()
            signup.user.save()
            error = "no"
        except:
            error = "yes"
    return render(request, 'profile.html', locals())

def changePassword(request):
    if not request.user.is_authenticated:
        return redirect('user_login')
    error = ""
    user = request.user
    if request.method == "POST":
        o = request.POST['oldpassword']
        n = request.POST['newpassword']
        try:
            u = User.objects.get(id=request.user.id)
            if user.check_password(o):
                u.set_password(n)
                u.save()
                error = "no"
            else:
                error = 'not'
        except:
            error = "yes"
    return render(request, 'changePassword.html', locals())

def Logout(request):
    logout(request)
    return redirect('index')
