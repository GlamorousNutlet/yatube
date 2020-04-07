from django.forms import ModelForm
from .models import Post, Comment
from django import forms

class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['text', 'group', 'image']

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text']



