from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, DetailView, DeleteView
from .models import Story
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils import timezone

# Create your views here.

class AddStoryView(LoginRequiredMixin, CreateView):
    model = Story
    fields = ['content']
    template_name = 'storyapp/add_story.html'
    success_url = reverse_lazy('index') # Redirect to home or profile after upload

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class StoryDetailView(LoginRequiredMixin, DetailView):
    model = Story
    template_name = 'storyapp/story_detail.html'
    context_object_name = 'story'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if self.request.user != obj.user and self.request.user not in obj.viewed_by.all():
            obj.viewed_by.add(self.request.user)
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        story = self.get_object()
        context['viewed_by_users'] = story.viewed_by.all()
        return context

class DeleteStoryView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Story
    template_name = 'storyapp/delete_story.html'
    success_url = reverse_lazy('index') # Redirect after deletion

    def test_func(self):
        story = self.get_object()
        return self.request.user == story.user
