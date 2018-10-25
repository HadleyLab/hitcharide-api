import shutil
import tempfile
import errno

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test.utils import override_settings
from rest_framework.test import APITestCase as BaseAPITestCase
from rest_framework import status

from apps.accounts.factories import UserFactory


class APITestCase(BaseAPITestCase):
    def setUp(self):
        super(APITestCase, self).setUp()
        self.username = 'user@test.test'
        self.password = 'password'
        self.user = UserFactory.create(
            phone='12345678900',
            is_phone_validated=True,
            email=self.username,
            password=self.password)

    def authenticate_as(self, username, password):
        self.assertTrue(self.client.login(username=username, password=password))

    def authenticate(self):
        self.authenticate_as(self.username, self.password)

    def assertSuccessResponse(self, resp):
        if resp.status_code not in range(200, 300):
            raise self.failureException(
                'Response status is not success. '
                'Response data is:\n{0}'.format(getattr(resp, 'data', 'None')))

    def assertNotAllowed(self, resp):
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def assertBadRequest(self, resp):
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def assertUnauthorized(self, resp):
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def assertForbidden(self, resp):
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def assertNotFound(self, resp):
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def assertInternalServerError(self, resp):
        self.assertEqual(
            resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
