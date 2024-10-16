from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

class UserAuthTests(TestCase):
    def setUp(self):
        # Create a user to test login and access
        self.user = User.objects.create_user(username='testuser', password='testpass')
    
    def test_register_user(self):
        """Test if a user can register"""
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful registration
        self.assertTrue(User.objects.filter(username='newuser').exists())  # Check if user was created
    
    def test_login(self):
        """Test if an existing user can log in"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after login
        self.assertTrue(response.url, reverse('home'))  # Ensure redirect to home page after login

    def test_logout(self):
        """Test if a user can log out successfully"""
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(reverse('logout'))  # Change GET to POST
        self.assertEqual(response.status_code, 302)  # Redirect after logout
        self.assertEqual(response.url, reverse('home'))  # Ensure redirect to home page after logout


    def test_protected_view_redirect(self):
        """Test that protected views redirect to login for unauthenticated users"""
        response = self.client.get(reverse('create_workout_plan'))  # Accessing a protected view
        self.assertEqual(response.status_code, 302)  # Should redirect to login
        self.assertIn(reverse('login'), response.url)  # Check if it redirects to the login page

    def test_protected_view_access(self):
        """Test that logged-in users can access protected views"""
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('create_workout_plan'))
        self.assertEqual(response.status_code, 200)  # Logged in users should be able to access this view

    def test_login_redirect(self):
        """Test if the user is redirected to the correct page after login"""
        login_url = reverse('login') + '?next=' + reverse('create_workout_plan')
        response = self.client.post(login_url, {
            'username': 'testuser',
            'password': 'testpass'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('create_workout_plan'))  # Should redirect to protected page
