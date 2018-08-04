from django.test import TestCase
from django.contrib.auth.models import User
from .models import Project, TMS
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from rest_framework import status


class UserTest(APITestCase):
    def setUp(self):
        # We want to go ahead and originally create a user.
        self.test_user = User.objects.create_user('testuser',
                                                  'test@example.com',
                                                  'testpassword')

    def test_create_user(self):
        """
        Ensure we can create a new user and a valid token is created with it.
        """
        data = {
            'username': 'foobar',
            'email': 'foobar@example.com',
            'password': 'somepassword'
        }

        response = self.client.post('/api/users/', data, format='json')

        # We want to make sure we have two users in the database..
        self.assertEqual(User.objects.count(), 2)
        # And that we're returning a 201 created code.
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Additionally, we want to return the username and email upon
        # successful creation.
        self.assertEqual(response.data['username'], data['username'])
        self.assertEqual(response.data['email'], data['email'])
        self.assertFalse('password' in response.data)


class TMSModelTestCase(TestCase):
    """This class defines the test suite for the tms model."""

    def setUp(self):
        """Define the test client and other test variables."""
        user = User.objects.create(username="kimchi")
        self.endpoint = "https://etabot.atlassian.net"
        self.username = "shanshan@etabot.ai"
        self.password = "password"
        self.type = "JI"
        self.tms = TMS(owner=user, endpoint=self.endpoint,
                       username=self.username, password=self.password,
                       type=self.type)

    def test_model_can_create_a_tms(self):
        """Test the user model can create a tms."""
        old_count = TMS.objects.count()
        self.tms.save()
        new_count = TMS.objects.count()
        self.assertNotEqual(old_count, new_count)


class TMSViewTestCase(TestCase):
    """Test suite for the api TMS views."""

    def setUp(self):
        """Define the TMS test client and other test variables."""
        user = User.objects.create(username="kimchi", email="kimchi@etabot.ai",
                                   password="iloveelie")

        self.client = APIClient()
        self.client.force_authenticate(user=user)

        self.tms_data = {'owner': user.id,
                         'endpoint': 'https://etabot.atlassian.net',
                         'username': 'shanshan@etabot.ai',
                         'password': 'password', 'type': 'JI'}
        self.response = self.client.post('/api/tms/',
                                         self.tms_data,
                                         format="json")

    def test_api_can_create_a_tms(self):
        """Test the api has tms creation capability."""
        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)

    def test_authorization_is_enforced(self):
        """Test that the tms api has user authorization."""
        new_client = APIClient()
        res = new_client.get('/api/tms/', kwargs={'pk': 0}, format="json")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_api_can_get_a_tms(self):
        """Test the api can get a given tms."""
        tms = TMS.objects.get(id=1)
        response = self.client.get(
            '/api/tms/',
            kwargs={'pk': tms.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, tms)

    def test_api_can_update_tms(self):
        """Test the api can update a given tms."""
        tms = TMS.objects.get()
        change_tms = {'password': 'newpassword'}
        url = '{}{}{}'.format('/api/tms/update/', tms.id, '/')
        res = self.client.patch(url,
                                # reverse('details', kwargs={'pk': tms.id}),
                                change_tms, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_api_can_delete_tms(self):
        """Test the api can delete a tms."""
        tms = TMS.objects.get()
        url = '{}{}{}'.format('/api/tms/', tms.id, '/')
        response = self.client.delete(url,
                                      # reverse('details', kwargs={'pk': tms.id}),
                                      format='json',
                                      follow=True)
        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)


class ProjectModelTestCase(TestCase):
    """This class defines the test suite for the project model."""

    def setUp(self):
        """Define the test client and other test variables."""
        user = User.objects.create(username="kimchi")
        self.project_name = "etabot"
        self.project_mode = "scrum"
        self.project_open_status = "ToDo"
        self.project_grace_period = "24"
        self.project_work_hours = "{1:(10,14),2:(16,20), 3:(10,14), 4:(16,18), 5:(20,21), 6:(23,23), 0:(9,10)}"
        self.project_vacation_days = "{('2017-04-21', '2017-04-30'), ('2017-05-16', '2017-05-19'), ('2017-05-24', '2017-05-24'), ('2017-05-29', '2017-05-29')}"
        self.project = Project(owner=user, name=self.project_name,
                               mode=self.project_mode,
                               open_status=self.project_open_status,
                               grace_period=self.project_grace_period,
                               work_hours=self.project_work_hours,
                               vacation_days=self.project_vacation_days)

    def test_model_can_create_a_project(self):
        """Test the user model can create a project."""
        old_count = Project.objects.count()
        self.project.save()
        new_count = Project.objects.count()
        self.assertNotEqual(old_count, new_count)


class ProjectViewTestCase(TestCase):
    """Test suite for the api views."""

    def setUp(self):
        """Define the test client and other test variables."""
        user = User.objects.create_user('testuser', 'test@example.com',
                                        'testpassword')

        self.client = APIClient()
        self.client.force_authenticate(user=user)

        self.project_data = {'owner': user.id, 'name': 'etabot',
                             'mode': 'scrum', 'open_status': 'ToDo',
                             'grace_period': '24', 'work_hours': '1:(10,14)',
                             'vacation_days': '(2017-04-21, 2017-04-30)'}
        self.response = self.client.post('/api/projects/',
                                         # reverse('create'),
                                         self.project_data,
                                         format="json")

    def test_api_can_create_a_project(self):
        """Test the api has user creation capability."""
        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)

    def test_authorization_is_enforced(self):
        """Test that the api has user authorization."""
        new_client = APIClient()
        res = new_client.get('/api/projects/', kwargs={'pk': 0}, format="json")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_api_can_get_a_project(self):
        """Test the api can get a given project."""
        project = Project.objects.get(id=1)
        response = self.client.get(
            '/api/projects/',
            kwargs={'pk': project.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, project)

    def test_api_can_update_project(self):
        """Test the api can update a given project."""
        project = Project.objects.get()
        change_project = {'mode': 'kanban'}
        url = '{}{}{}'.format('/api/projects/', project.id, '/')
        res = self.client.patch(url, change_project, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_api_can_delete_project(self):
        """Test the api can delete a project."""
        project = Project.objects.get()
        url = '{}{}{}'.format('/api/projects/', project.id, '/')
        response = self.client.delete(url, format='json', follow=True)
        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)
