from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Comment, Post


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('group', 'text', 'image')
        labels = {
            'group': _('Группа'),
            'text': _('Текст'),
            'image': _('Картинка'),
        }
        help_texts = {
            'group': _('Выберите группу, но это необязательно:)'),
            'text': _('* поле обязательноe для заполнения'),
            'image': _('загрузите картинку'),
        }


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text', )
        labels = {
            'text': _('расскажите, что думаете об этом')
        }
        help_texts = {
            'text': _('* поле обязательноe для заполнения')
        }
