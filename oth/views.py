from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import models
from django.contrib import messages
from oth import models
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()
from facepy import GraphAPI
import datetime

m_level = 1
f_user = ""


def index(request):
    user = request.user
    if user.is_authenticated():
        player = models.player.objects.get(user_id=request.user.pk)
        try:
            level = models.level.objects.get(l_number=player.max_level)
            return render(request, 'level.html', {'player': player, 'level': level})
        except:
            return render(request, 'finish.html', {'player': player})
    return render(request, 'index_page.html')


@login_required
def display(request):
    player = models.player.objects.get(user_id=request.user.pk)
    return render(request, 'display.html', {'player': player})


def save_profile(backend, user, response, *args, **kwargs):
    if backend.name == 'facebook':
        profile = user
        try:
            player = models.player.objects.get(user=profile)
        except:
            player = models.player(user=profile)
            player.name = response.get('name')
            player.timestamp=datetime.datetime.now()
            player.save()
    elif backend.name == 'google-oauth2':
        profile = user
        try:
            player = models.player.objects.get(user=profile)
        except:
            player = models.player(user=profile)
            player.timestamp=datetime.datetime.now()
            player.name = response.get('name')['givenName'] + " " + response.get('name')['familyName']
            player.save()


@login_required
def answer(request):
    ans = ""
    if request.method == 'POST':
        ans = request.POST.get('ans')
    player = models.player.objects.get(user_id=request.user.pk)
    try:
        level = models.level.objects.get(l_number=player.max_level)
    except:
        return render(request, 'finish.html', {'player': player})
    # print answer
    # print level.answer
    if ans == level.answer:
        #print level.answer
        player.max_level = player.max_level + 1
        player.score = player.score + 10
        player.timestamp = datetime.datetime.now()
        level.numuser = level.numuser + 1
        level.save()
        #print level.numuser
        # print player.max_level
        global m_level
        global f_user
        # print f_user
        # print m_level
        if m_level < player.max_level:
            m_level = player.max_level
            f_user = player.name
        player.save()
        try:
            level = models.level.objects.get(l_number=player.max_level)
            return render(request, 'level.html', {'player': player, 'level': level})
        except:
            return render(request, 'finish.html', {'player': player})
    messages.error(request, "Wrong Answer!, Try Again")
    return render(request, 'level.html', {'player': player, 'level': level})

@login_required()
def lboard(request):
    p= models.player.objects.order_by('-score','timestamp')
    cur_rank = 1
    counter = 0

    for pl in p:
        if counter < 1:
            pl.rank = cur_rank
        else:
            if pl.score == p[counter-1].score:
                pl.rank = cur_rank
            else:
                cur_rank += 1
                pl.rank = cur_rank
        counter += 1


    return render(request, 'lboard.html', {'players': p})

@login_required()
def rules(request):
    return render(request, 'index_page.html')

