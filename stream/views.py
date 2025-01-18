from django.shortcuts import render, redirect, get_object_or_404
from .models import VidStream
from .forms import VidUploadForm
from django.views.generic import DetailView, DeleteView, UpdateView, ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User

from django.http import FileResponse, HttpResponseForbidden
import os
from django.conf import settings


class VideoDetailView(LoginRequiredMixin, DetailView):
    template_name = "stream/video-detail.html"
    model = VidStream

class GeneralVideoListView(LoginRequiredMixin, ListView):
    model = VidStream
    template_name = 'stream/video-list.html'
    context_object_name = 'videos'
    ordering = ['-upload_date']

def search(request):
    if request.method == "POST":
        query = request.POST.get('title', None)
        if query:
            results = VidStream.objects.filter(title__contains=query)
            return render(request, 'stream/search.html', {'videos': results})
    return render(request, 'stream/search.html')

class VideoCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = VidStream
    success_url = "/"
    template_name = 'stream/post-video.html'
    fields = ['title', 'description', 'video']

    # Ensure the logged-in user is the one uploading the content
    def form_valid(self, form):
        form.instance.streamer = self.request.user
        return super().form_valid(form)

    # Restrict video creation to admin users only
    def test_func(self):
        return self.request.user.is_superuser

class VideoUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = VidStream
    template_name = 'stream/post-video.html'
    success_url = "/"
    fields = ['title', 'description', 'video']

    # Ensure the logged-in user is the one updating the content
    def form_valid(self, form):
        form.instance.streamer = self.request.user
        return super().form_valid(form)

    # Prevent other users from updating the videos
    def test_func(self):
        video = self.get_object()
        if self.request.user == video.streamer:
            return True
        return False

class VideoDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    template_name = "stream/video-confirm-delete.html"
    success_url = "/"
    model = VidStream

    def test_func(self):
        video = self.get_object()
        if self.request.user == video.streamer:
            return True
        return False

class UserVideoListView(ListView):
    model = VidStream
    template_name = "stream/user_videos.html"
    context_object_name = 'videos'

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return VidStream.objects.filter(streamer=user).order_by('-upload_date')


from django.conf import settings
from django.http import FileResponse, HttpResponseForbidden
import os

def serve_secure_media(request, path):
    if not request.user.is_authenticated:
        return HttpResponseForbidden("You must be logged in to view this media.")

    media_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(media_path):
        return FileResponse(open(media_path, 'rb'), content_type='video/mp4')
    return HttpResponseForbidden("File not found or access restricted.")
