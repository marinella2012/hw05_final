import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Group, Post, User


@override_settings(MEDIA_ROOT=tempfile.mktemp(dir=settings.BASE_DIR))
class StaticURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cache.clear()
        cls.group = Group.objects.create(
            title='Заголовок',
            description='123',
            slug='test-slug',
        )
        cls.group2 = Group.objects.create(
            title='Заголовок2',
            description='1234',
            slug='test-slug2',
        )
        cls.user = User.objects.create(username='Marina')
        small_pic = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_pic,
            content_type='image/gif'
        )
        for _ in range(15):
            cls.post = Post.objects.create(
                author=cls.user,
                text='Текст',
                image=cls.uploaded,
                group=Group.objects.get(slug='test-slug')
            )
        cls.user2 = User.objects.create(username='Petro')

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.user2)
        site = Site.objects.get(pk=1)
        self.flat_about = FlatPage.objects.create(
            url='/about-author/',
            title='about me',
            content='<b>content</b>'
        )
        self.flat_tech = FlatPage.objects.create(
            url='/about-spec/',
            title='about my tech',
            content='<b>content</b>'
        )
        self.flat_about.sites.add(site)
        self.flat_tech.sites.add(site)

    def test_static_pages_uses_correct_context(self):
        """Шаблоны flatpages сформированы с правильным контекстом."""
        self.static_pages = {
            self.flat_about: 'about-author',
            self.flat_tech: 'spec'
        }
        for flat_page, url in self.static_pages.items():
            with self.subTest():
                response = self.guest_client.get(reverse(url))
                response_flat = response.context.get('flatpage')
                self.assertEqual(response_flat.title, flat_page.title)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            'index.html': reverse('index'),
            'new_post.html': reverse('new_post'),
            'group.html': (
                reverse('group', kwargs={'slug': self.group.slug})
            ),
        }
        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом
        и с правильным количеством постов"""
        response = self.authorized_client.get(reverse('index'))
        page1 = response.context.get('page')
        page_range = response.context.get('paginator').page_range
        self.assertEqual(len(page1), 10)
        self.assertEqual(len(page_range), 2)
        self.assertIsNotNone(page1[0].image)

    def test_new_page_show_correct_context(self):
        """Шаблон new сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('new_post'))
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
            'image': forms.fields.ImageField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_group_show_correct_context(self):
        """Шаблон group сформирован с правильным контекстом
        и пост попал в нужную группу"""
        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': self.group.slug})
        )
        response_group = response.context.get('group')
        response_group2 = response.context.get('group2')
        page1 = response.context.get('page')
        self.assertIsNotNone(page1[0].image)
        self.assertEqual(response_group.title, self.group.title)
        self.assertEqual(response_group.description, self.group.description)
        self.assertEqual(response_group.slug, self.group.slug)
        self.assertIsNone(response_group2, msg=None)

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('profile', kwargs={'username': self.user.username})
        )
        response_prof = response.context.get('author')
        page1 = response.context.get('page')
        self.assertIsNotNone(page1[0].image)
        self.assertEqual(response_prof.username, self.user.username)

    def test_post_show_correct_context(self):
        """Шаблон post сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'post',
                kwargs={
                    'post_id': self.post.id,
                    'username': self.user.username
                }
            )
        )
        response_post = response.context.get('post')
        post1 = response.context.get('post')
        self.assertIsNotNone(post1.image)
        self.assertEqual(response_post.id, self.post.id)
        self.assertEqual(response_post.author.username, self.user.username)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'post_edit',
                kwargs={
                    'post_id': self.post.id,
                    'username': self.user.username
                }
            )
        )
        response_post = response.context.get('post')
        self.assertEqual(response_post.id, self.post.id)
        self.assertEqual(response_post.author.username, self.user.username)

    def test_no_image(self):
        """Защита от загрузки не графических файлов"""
        form_data = {
            'group': self.group.id,
            'text': self.post.text,
            'image': self.uploaded,
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertFalse(response.context.get('page')[0].image)

    def test_follow_page_access_for_follower(self):
        """Проверка доступности страницы /follow/ подписчику"""
        self.authorized_client2.get(
            reverse(
                'profile_follow', args=(self.user.username,)
            )
        )
        response = self.authorized_client2.get(reverse('follow_index'))
        follow_post = response.context.get('page')[0]
        self.assertEqual(follow_post.text, self.post.text)
        self.assertEqual(follow_post.author, self.user)
        self.assertEqual(follow_post.group, self.group)

    def test_follow_page_access_for_anonimous(self):
        """Проверка доступности страницы /follow/ анон.пользователю"""
        response = self.guest_client.get(reverse('follow_index'))
        self.assertEqual(response.status_code, 302)

    def test_image_tag_in_page(self):
        """Тег img присутствует на странице"""
        Post.objects.all().delete()
        cache.clear()
        response = self.authorized_client.get(reverse('index'))
        img_count = response.content.decode().count('<img')
        Post.objects.create(
            author=self.user,
            text='self.text',
            image=self.uploaded
        )
        cache.clear()
        response = self.authorized_client.get(reverse('index'))
        img_count2 = response.content.decode().count('<img')
        self.assertGreater(img_count2, img_count)
