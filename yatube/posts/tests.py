from django.test import TestCase, Client
from . models import User, Post

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

        self.client.force_login(self.username)                                            # Логинимся и создаем пост
        self.client.post("/new/", {"text": 'Another post'})
        post = Post.objects.filter(author=self.username, text='Another post').first()     # Ищем пост
        self.assertIsNotNone(post, msg='Im here 2')                                       # Проверяем, не пуст ли post

    def test_new_post_unauth(self):
        response = self.client.post("/new/", {"text": 'Mamba #5'})
        self.assertRedirects(response, '/auth/login/?next=/new/')                         # Проверяем, есть ли редирект на страницу авторизации

    def test_post_search(self):
        post_text = 'Another post'
        self.client.force_login(self.username)
        self.client.post("/new/", {"text": post_text})                                    # Логинимся, создаем пост
        post = Post.objects.filter(author=self.username, text=post_text).first()
        response = self.client.get('/')
        self.assertContains(response, post_text)                                          # Ищем пост в index
        response = self.client.get(f'/{self.username}/')
        self.assertContains(response, post_text)                                          # Ищем пост на странице пользователя
        response = self.client.get(f'/{self.username}/{post.pk}/')
        self.assertContains(response, post_text)                                          # Ищем пост на странице поста

    def test_post_edit(self):
        post_text = 'Is this love that Im feeling; Is this the love that Ive been searching for; Is this love or am I dreaming; This must be love: Cause its really got a hold on me; A hold on me'
        self.client.force_login(self.username)
        self.client.post("/new/", {"text": post_text})                                    # Логинимся и создаем пост
        post = Post.objects.filter(author=self.username, text=post_text).first()
        edit_post_text = 'Is this love that Im feeling; Is this the love that Ive been searching for; Is this love or am I dreaming;'
        self.client.post(f'/{self.username}/{post.pk}/edit', {"text": edit_post_text})    # Изменяем текст поста
        response = self.client.get('/')
        self.assertContains(response, edit_post_text)                                     # Ищем измененный пост в index
        response = self.client.get(f'/{self.username}/')
        self.assertContains(response, edit_post_text)                                     # Ищем измененный пост на странице пользователя
        response = self.client.get(f'/{self.username}/{post.pk}/')
        self.assertContains(response, edit_post_text)                                     # Ищем измененный пост на странице поста

class handler_pages_tests(TestCase):
    def setUp(self):
        self.client = Client()
        self.username = User.objects.create_user(username="DavidMustaine")
    #Тестируем 404 страницу
    def test_404(self):
        self.client.force_login(self.username)
        response = self.client.get(f'/{self.username}/999/edit')
        self.assertEqual(response.status_code, 404)

class img_tests(TestCase):
    def setUp(self):
        self.client = Client()
        self.username = User.objects.create_user(username="DavidCoverdale")
        self.client.force_login(self.username)

    def test_img_in_post_page(self):
        with open('IMG_1504.jpg', mode = 'rb') as img:
            self.client.post("/new/", {"text": 'is this love?', "image": img})
        post = Post.objects.get(text = 'is this love?')
        response = self.client.get(f'/{self.username}/{post.pk}/')
        self.assertContains(response, "img")

    def test_not_image_load(self):
        # Пробуем создать пост, где изображение не изображение
        with open('media/13.txt', 'rb') as test_file:
            self.client.post("/new/", {'text': 'that Im feeling', 'image': test_file})
        #Поскольку,в теории, должна вылезти ошибка в момент добавления не картинки, то пост не создастся
        post = Post.objects.last()
        #Проверяем, что последний(и единственный из возможных) пост пуст
        self.assertEqual(post, None)





