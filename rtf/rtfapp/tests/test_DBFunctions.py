from django.test import TestCase, Client
import zipfile, StringIO, os

def fromTestingDirToFixturesDir(path):
	""" Return the path from where tests are run to the fixtures dir """
	return "rtfapp/fixtures/" + path

class test_DBFunctions(TestCase):
    """ Test cases for Database Backup and Restore Functions """
    fixtures = ['users.json', 'user_profiles.json']

    def test_download(self):
        #test that db dump works
        c = Client()
        response = c.post('/login/', {'username':'root', 'password': 'toor'})
        response = c.get('http://localhost:8000/downloadDB/')
        file = StringIO.StringIO(response.content)
        test_zip = zipfile.ZipFile(file, 'r')

        self.assertIsNone(test_zip.testzip())
        self.assertIn('user profile.csv', test_zip.namelist())
        test_zip.close()
        file.close()

    def test_upload(self):
        #test that a simple db upload works
        c = Client()
        response = c.post('/login/', {'username':'root', 'password': 'toor'})
        with open(fromTestingDirToFixturesDir('db.zip'), 'rb') as zipfile:
            response = c.post('/uploadDB/', {'dbFile': zipfile})
            #assert that everything went okay
            self.assertEqual(response.status_code, 200)


