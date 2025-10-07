from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()  # Usa tu modelo personalizado


class RegistroTest(TestCase):
    def test_crear_usuario(self):
        usuario = User.objects.create_user(
            email="liz@mail.com",
            password="clave123",
            nombre="Lizeth",
            apellido="Jimenez"
        )
        self.assertEqual(usuario.email, "liz@mail.com")
        self.assertTrue(usuario.check_password("clave123"))
        self.assertEqual(User.objects.count(), 1)


class LoginTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="liz@mail.com",
            password="clave123",
            nombre="Lizeth",
            apellido="Jimenez"
        )

    def test_login_correcto(self):
        login = self.client.login(email="liz@mail.com", password="clave123")
        self.assertTrue(login)

    def test_login_incorrecto(self):
        login = self.client.login(email="liz@mail.com", password="malaClave")
        self.assertFalse(login)


class LoginViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="liz@mail.com",
            password="clave123",
            nombre="Lizeth",
            apellido="Jimenez"
        )

    def test_login_view_correcto(self):
        response = self.client.post('/login/', {
            'email': 'liz@mail.com',
            'password': 'clave123'
        })
        self.assertEqual(response.status_code, 302)  # Redirección tras login correcto

    def test_login_view_incorrecto(self):
        response = self.client.post('/login/', {
            'email': 'liz@mail.com',
            'password': 'wrong'
        })
        self.assertEqual(response.status_code, 200)  # Se queda en login
        self.assertContains(response, "Usuario o contraseña incorrectos")
