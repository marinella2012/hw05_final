from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        'Название группы',
        help_text='Дайте короткое название группы',
        max_length=200
    )
    slug = models.SlugField(
        'Адрес для страницы группы',
        help_text=('Укажите адрес для страницы группы. Используйте только '
                   'латиницу, цифры, дефисы и знаки подчёркивания'),
        max_length=100,
        unique=True
    )
    description = models.TextField(
        'Описание группы',
        help_text='Дайте короткое описание группы',
        max_length=200
    )

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        'Пост',
        help_text='Напишите что-нибудь в посте',
        db_index=True
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        db_index=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        db_index=True
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа',
        db_index=True
    )
    image = models.ImageField(
        upload_to='posts/',
        blank=True,
        null=True,
        db_index=True
    )

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        text_short = self.text[:15]
        return text_short


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        related_name='comments',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        User,
        related_name='comments',
        on_delete=models.CASCADE
    )
    text = models.TextField(
        'Комментарий',
        help_text='Напишите что вы думаете об этом',
        max_length=500
    )
    created = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.text


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Подписка'
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'],
                                    name='unique relationship')]
