from django.shortcuts import render
from django.http import HttpResponse
from UserCards import models as user_modules
from Documents import models as documents_models


def signup(request):
    return render(request, 'UserCards/signup.html', {})


def login(request):
    return render(request, 'UserCards/login.html', {'error': False})

def index(request):
    user = user_modules.UserCard.objects.filter(session_id=request.COOKIES['sessionid'])
    if len(user) == 1:
        copies = user[0].documentcopy_set.all()
        return render(request, 'UserCards/index.html', {'user': user[0], 'copies': copies})
    else:
        return HttpResponse("You are not currently logged in")


def make_user(request):
    '''
    Processing signup step
    '''
    username = request.POST.get("Name")
    surname = request.POST.get("Surname")
    email = request.POST.get("Email")
    password = request.POST.get("Password")
    phone = request.POST.get("Phone")
    address = request.POST.get("Address")
    user = user_modules.UserCard(name=username, status="student", email=email,
                                 password=password, phone_number=phone, surname=surname, address=address)
    user.session_id = request.COOKIES['sessionid']
    user.save()
    response = render(request, 'UserCards/index.html', {'user': user, 'copies': ''})
    return response

def identify_user(request):
    '''
    Processing login step
    '''
    user = user_modules.UserCard.objects.filter(email=request.POST.get("Email"), password=request.POST.get("Password"))
    if len(user) == 1:
        user[0].session_id = request.COOKIES['sessionid']
        user[0].save()
        return render(request, 'Documents/index.html', {'documents': documents_models.Document.objects.all()})
    else:
        return render(request, 'UserCards/login.html', {'error': True})

def return_copies(request):
    print(request.POST.keys())
    chosen_copies = [documents_models.DocumentCopy.objects.get(id=int(id)) for id in request.POST.keys() if id.isdigit()]
    if chosen_copies:
        print(chosen_copies)
        for copy in chosen_copies:
            copy.doc.copies += 1
            copy.doc.save()
            try:
                holder = user_modules.UserCard.objects.get(session_id=request.COOKIES['sessionid'])
                print(holder.documentcopy_set.all())
                holder.documentcopy_set.get(id=copy.id).delete()
                return render(request, 'UserCards/index.html', {'user': holder, 'copies': holder.documentcopy_set.all()})
            except:
                return HttpResponse("You are not currently logged in")