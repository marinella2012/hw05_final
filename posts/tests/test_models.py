from django.test import TestCase

from posts.models import Group, Post, User


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Заголовок',
            description='Ж'*100,
            slug='test-slug'
        )
        cls.user = User.objects.create(username='Marina')

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        group = GroupModelTest.group
        field_verboses = {
            'title': 'Название группы',
            'slug': 'Адрес для страницы группы',
            'description': 'Описание группы',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        group = GroupModelTest.group
        field_help_texts = {
            'title': 'Дайте короткое название группы',
            'slug': (
                'Укажите адрес для страницы группы. Используйте только '
                'латиницу, цифры, дефисы и знаки подчёркивания'
            ),
            'description': 'Дайте короткое описание группы',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).help_text, expected)

    def test_object_name_is_title_fild(self):
        """В поле __str__  объекта group записано значение поля group.title."""
        group = GroupModelTest.group
        expected_object_name = group.title
        self.assertEquals(expected_object_name, str(group))


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='Marina')
        cls.post = Post.objects.create(
            text='Заголовок',
            author=cls.user,
        )

    def test_object_name_is_text_fild(self):
        """В поле __str__  объекта group записано значение поля post.text."""
        post = PostModelTest.post
        expected_object_name = post.text
        self.assertEquals(expected_object_name, str(post))
