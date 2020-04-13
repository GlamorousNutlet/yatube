from django.test import TestCase, Client, override_settings
from . models import User, Post, Follow
from yatube import settings
import time


class Cash_test(TestCase):
    def setUp(self):
        self.client = Client()
        self.username = User.objects.create_user(username="TommyCash")
        self.client.force_login(self.username)
        self.client.get('/')                                             # Делаем запрос к главной, чтобы запустить таймер

    def test_using_cache(self):
        self.client.post('/new/', {'text': 'Guess whos back?'})          # Создаем пост
        response_before = self.client.get('/')                           # Получаем главную
        self.assertNotContains(response_before, 'Guess whos back?')      # Проверяем, отобразился ли наш пост раньше времени
        time.sleep(20)                                                   # Ждем, пока в кэш попадет новая страница
        response_after = self.client.get('/')                            # Еще раз запрашиваем
        self.assertContains(response_after, 'Guess whos back?')          # Смотрим, есть ли пост

class ProfileTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.username = User.objects.create_user(username="DavidCoverdale")

    def test_profile(self):
        # формируем GET-запрос к странице сайта
        response = self.client.get("/DavidCoverdale/")
        # проверяем что страница найдена
        self.assertEqual(response.status_code, 200, msg="i'm here")

    def test_new_post_auth(self):
        # Логинимся и создаем пост
        self.client.force_login(self.username)
        self.client.post("/new/", {"text": 'Another post'})
        # Ищем пост
        post = Post.objects.filter(author=self.username, text='Another post').first()
        # Проверяем, не пуст ли post
        self.assertIsNotNone(post, msg='Im here 2')

    def test_new_post_unauth(self):
        response = self.client.post("/new/", {"text": 'Mamba #5'})
        # Проверяем, есть ли редирект на страницу авторизации
        self.assertRedirects(response, '/auth/login/?next=/new/')

    @override_settings(CACHES=settings.TEST_CACHES)
    def test_post_search(self):
        post_text = 'Another post'
        # Логинимся, создаем пост
        self.client.force_login(self.username)
        self.client.post("/new/", {"text": post_text})
        post = Post.objects.filter(author=self.username, text=post_text).first()
        response = self.client.get('/')
        # Ищем пост в index
        self.assertContains(response, post_text)
        response = self.client.get(f'/{self.username}/')
        # Ищем пост на странице пользователя
        self.assertContains(response, post_text)
        response = self.client.get(f'/{self.username}/{post.pk}/')
        # Ищем пост на странице profile
        self.assertContains(response, post_text)

    @override_settings(CACHES=settings.TEST_CACHES)
    def test_post_edit(self):
        post_text = 'Is this love that Im feeling; Is this the love that Ive been searching for; '
        # Логинимся и создаем пост
        self.client.force_login(self.username)
        self.client.post("/new/", {"text": post_text})
        post = Post.objects.filter(author=self.username, text=post_text).first()
        # Изменяем текст поста
        edit_post_text = 'Is this love that Im feeling; Is this the love that Ive been searching for; Is this love or am I dreaming;'
        self.client.post(f'/{self.username}/{post.pk}/edit', {"text": edit_post_text})
        response = self.client.get('/')
        # Ищем измененный пост в index
        self.assertContains(response, edit_post_text)
        response = self.client.get(f'/{self.username}/')
        # Ищем измененный пост на странице пользователя
        self.assertContains(response, edit_post_text)
        response = self.client.get(f'/{self.username}/{post.pk}/')
        # Ищем измененный пост на странице поста
        self.assertContains(response, edit_post_text)


class handler_pages_tests(TestCase):
    def setUp(self):
        self.client = Client()
        self.username = User.objects.create_user(username="DavidMustaine")

    def test_404(self):
        self.client.force_login(self.username)
        response = self.client.get(f'/{self.username}/999/edit/')
        self.assertEqual(response.status_code, 404)

class img_tests(TestCase):
    def setUp(self):
        self.client = Client()
        self.username = User.objects.create_user(username="DavidCoverdale")
        self.client.force_login(self.username)

    def test_img_in_post_page(self):
        # создаем пост с картинкой
        with open('IMG_1504.jpg', mode = 'rb') as img:
            self.client.post("/new/", {"text": 'is this love?', "image": img})
        # ищем этот пост
        post = Post.objects.get(text = 'is this love?')
        response = self.client.get(f'/{self.username}/{post.pk}/')
        # проверяем на упоминание "img"
        self.assertContains(response, "img")

    def test_not_image_load(self):
        # Пробуем создать пост, где изображение не изображение
        with open('media/13.txt', 'rb') as test_file:
            self.client.post("/new/", {'text': 'that Im feeling', 'image': test_file})
        #Поскольку,в теории, должна вылезти ошибка в момент добавления не картинки, то пост не создастся
        post = Post.objects.last()
        #Проверяем, что последний(и единственный из возможных) пост пуст
        self.assertEqual(post, None)

class social_tests(TestCase):
    def setUp(self):
        self.client = Client()
        self.username = User.objects.create_user(username="DavidCoverdale")
        self.followin_1 = User.objects.create_user(username="JamesHetfield")
        self.client.force_login(self.username)
        self.client.post("/new/", {"text": 'Another post'})

    def test_auth_user_comment(self):
        post = Post.objects.filter(author=self.username, text='Another post').first()     # Ищем пост
        self.client.logout()
        # После logout-а пробуем создать коммент
        self.client.post(f'/{self.username}/{post.pk}/comment/', {"text": 'Yeah'})
        response = self.client.get(f'/{self.username}/{post.pk}/')
        # Убеждаемся, что коммент не создался
        self.assertNotContains(response, 'Yeah')
        # Теперь логинимся и снова пробуем создать коммент
        self.client.force_login(self.username)
        self.client.post(f'/{self.username}/{post.pk}/comment/', {"text": 'Yeah'})
        response = self.client.get(f'/{self.username}/{post.pk}/')
        # Проверяем, что коммент создался
        self.assertContains(response, 'Yeah')

    def test_auth_user_follow(self):
        # Создали юзера, подписали нас на другого юзера
        self.client.get(f'/{self.followin_1}/follow/')
        # Проверяем, что подписка есть
        self.assertTrue(Follow.objects.filter(user = self.username, author = self.followin_1).exists())
        # Отписываемся и проверяем, что подписки больше нет
        self.client.get(f'/{self.followin_1}/unfollow/')
        self.assertFalse(Follow.objects.filter(user=self.username, author=self.followin_1).exists())

    def test_follow_page_test(self):
        self.client.logout()
        # Заходим под пользователем, создаем пост, идем на страничку follow и ищем там пост
        self.client.force_login(self.followin_1)
        self.client.post("/new/", {"text": 'post_text'})
        self.client.force_login(self.followin_1)
        response = self.client.get('/follow/')
        self.assertNotContains(response, 'post_text')
        # перезаходим под другим пользователем, кидаем подписку, на страничке follow ищем пост этого автора
        self.client.logout()
        self.client.force_login(self.username)
        self.client.get(f'/{self.followin_1}/follow/')
        response = self.client.get('/follow/')
        self.assertContains(response, 'post_text')










