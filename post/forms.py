from django import forms
from post.models import Post, Story

class NewPostform(forms.ModelForm):
    # content = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required=True)
    
    picture = forms.ImageField(required=True)
    caption = forms.CharField(widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Caption'}), required=False)
    tags = forms.CharField(widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Tags | Seperate with comma'}), required=False)

    class Meta:
        model = Post
        fields = ['picture', 'caption', 'tags']


# class PostForm(forms.ModelForm):
#     class Meta:
#         model = Post
#         fields = ['image', 'caption']
        
    
class StoryForm(forms.ModelForm):
    class Meta:
        model = Story
        fields = ['image']
