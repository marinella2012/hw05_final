
import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Group, Post, User

TEMP_DIR = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=(TEMP_DIR + '/media'))
class PostFormTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Заголовок',
            description='123',
            slug='test-slug',
        )
        cls.user = User.objects.create(username='Marina')
        cls.small_pic = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_pic,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текст',
            image=cls.uploaded,
            group=Group.objects.get(slug='test-slug')
        )
        cls.user2 = User.objects.create(username='Petro')
        cls.authorized_client = Client()
        cls.authorized_client2 = Client()
        cls.authorized_client.force_login(cls.user)
        cls.authorized_client2.force_login(cls.user2)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_create_post_with_image(self):
        """Проверяем форму создания записи c картинкой
        и сохранения ее в базе данных"""
        posts_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=self.small_pic,
            content_type='image/gif'
        )
        form = {
            'author': self.user,
            'text': self.post.text,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form,
            follow=True
        )
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertIsNotNone(Post.objects.first().image)

    def test_edit_form_post(self):
        """Проверяем форму редактирования записи и
        сохранения ее в базе данных"""
        form_data = {
            'group': self.group.id,
            'text': self.post.text
        }
        response = self.authorized_client.post(
            reverse(
                'post_edit',
                kwargs={
                    'username': self.user.username,
                    'post_id': self.post.id
                }
            ),
            data=form_data,
            follow=True
        )
        with self.subTest(
            msg='нет переадресации',
            code=response.status_code
        ):
            self.assertRedirects(
                response,
                reverse(
                    'post',
                    kwargs={
                        'username': self.user.username,
                        'post_id': self.post.id
                    }
                )
            )

    def test_create_comment(self):
        """Проверяем форму создания комментария"""
        form_data = {
            'author': self.user.username,
            'post': self.post.id,
            'text': 'comment',
        }
        response = self.authorized_client.post(
            reverse(
                'add_comment',
                kwargs={
                    'post_id': self.post.id,
                    'username': self.user.username
                }
            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'post',
            kwargs={
                'post_id': self.post.id,
                'username': self.user.username
                }
            )
        )
        response_comment = response.context['comments'].count()
        self.assertEqual(response_comment, 1)
