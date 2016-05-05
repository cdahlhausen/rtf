from django.test import TestCase, Client
from django.contrib.auth.models import User

class LoginTests(TestCase):
	fixtures = ['users.json', 'user_profiles.json']

	def setUp(self):
		pass

	def test_login(self):
		#ensure the login form works
		c = Client()
		response = c.post('/login/', {'username':'root', 'password': 'toor'})
		self.assertTrue("Invalid" not in response.content)

	def test_admin_access(self):
		#ensure access to admin-side homepage works for logged in users
		c = Client()
		response = c.post('/login/', {'username':'root', 'password': 'toor'})
		response = c.get('/administration/')
		self.assertEqual(response.status_code, 200)

	def test_bad_login(self):
		#test that bad logins are rejected with the correct error page
		c = Client()
		response = c.post('/login/', {'username':'test_root', 'password': 'badpass'})
		self.assertTrue("Invalid" in response.content)

	def test_logout(self):
		#test that users are properly logged out
		c = Client()
		response = c.post('/login/', {'username':'root', 'password': 'toor'})
		if "Invalid" not in response.content:
			response = c.post('/logout/')
			self.assertEqual(response.status_code, 200)
		else:
			#fail spectacularly
			raise AssertionError

	def test_index_logged_in(self):
		#test that logged in users are redirected to the admin page
		c = Client()
		response = c.post('/login/', {'username':'root', 'password': 'toor'})
		response = c.get('/administration/')
		self.assertTrue('rtfapp/administration.html' in response.templates[0].name)
		self.assertTrue(response.status_code == 200)

	def test_index_not_logged_in(self):
		#test that not logged in users are redirected to the login page
		c = Client()
		response = c.get('/')
		self.assertTrue('rtfapp/index.html' in response.templates[0].name)
		self.assertTrue(response.status_code == 200)

	def tearDown(self):
		pass

class AdminTests(TestCase):
	fixtures = ['users.json', 'user_profiles.json']

	def test_placemarks(self):
		#test that placemark map is loaded properly
		c = Client()
		response = c.post('/login/', {'username':'root', 'password': 'toor'})
		response = c.get('/administration/')
		self.assertTrue("<title>Admin | Rivanna Trails Foundation</title>" in response.content)

class EditTests(TestCase):
	def setUp(self):
		pass

	#The following three tests make sure each field of the edit profile page work
	def test_edit_email(self):
		c = Client()
		response = c.post('/edit_profile/', {'email':'very_testy@test.de'})
		if response.status_code == 200:
			response = c.get('/edit_profile/')
			self.assertTrue("very_testy" in response.context['email'])

	def test_edit_phone(self):
		c = Client()
		response = c.post('/edit_profile/', {'phone_number': '555-555-5557'})
		if response.status_code == 200:
			response = c.get('/edit_profile/')
			self.assertTrue("5557" in response.context['phone_number'])

	def test_edit_name(self):
		c = Client()
		response = c.post('/edit_profile/', {'username': 'very_testy_2'})
		if response.status_code == 200:
			response = c.get('/edit_profile/')
			self.assertTrue("very_testy_2" in response.context['username'])

	def test_no_profile(self):
		#test error handling code (if a user is created with no profile, create one on the fly)
		c = Client()
		User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
		response = c.post('/login/', {'username':'john', 'password': 'johnpassword'})
		response = c.get('/edit_profile/')
		self.assertTrue(response.status_code, 200)