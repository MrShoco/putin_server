from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.views.decorators.http import require_POST
from jfu.http import upload_receive, UploadResponse, JFUResponse
from django.conf import settings
from time import sleep
import json
import os
from django.http import JsonResponse

from .utils.putin_face_recognition.putin_face_finder import find_putin


def track_uploaded(request, email, file_ids):
    try:
        user = User.objects.get(username=email)
        profile = user.profile
        user.save()
    except User.DoesNotExist:
        user = User(username=email)
        user.save()
        profile = Profile()
        profile.total_distance = 0
        profile.user = user
    profile.save()
    login(request, user)
    find_putin(File.objects.get(id=file_ids[0]))
    #for id in file_ids:
    #    try:
    #        find_putin()
    #    except File.DoesNotExist:
    #        pass


@require_POST
def upload( request ):
    file = upload_receive( request )

    instance = File(file = file)
    instance.save()

    basename = os.path.basename( instance.file.path )

    file_dict = {
        'name' : basename,
        'size' : file.size,
        'url': settings.MEDIA_URL + 'track/' + basename,
        'deleteUrl': reverse('jfu_delete', kwargs = {'pk': instance.pk }),
        'id': instance.pk,
        'deleteType': 'POST',
    }
    sleep(0.1)
    return UploadResponse( request, file_dict )


@require_POST
def upload_delete(request, pk):
    success = True
    try:
        instance = File.objects.get(pk=pk)
        os.unlink(instance.file.path)
        instance.delete()
    except File.DoesNotExist:
        success = False
    return JFUResponse(request, success)


@require_POST
def send(request):
    email = request.POST["email"]
    files = list(map(int, request.POST["file-ids"].split(",")))
    track_uploaded(request, email, files)
    return HttpResponseRedirect("/")


def index(request):
    context = {}
    return render(request, 'index.html', context=context)
