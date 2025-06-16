from django.contrib.auth.models import User
from comment.models import Comment
from django import forms

class NewCommentForm(forms.ModelForm):
    body = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Write a comment...',
            'rows': 1,
            'style': 'resize: none;'
        }),
        required=True
    )
    
    class Meta:
        model = Comment
        fields = ("body",)