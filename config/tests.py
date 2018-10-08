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

    def fake_media(self):
        tmp_dir = tempfile.mkdtemp()

        try:
            return override_settings(MEDIA_ROOT=tmp_dir)
        finally:
            try:
                shutil.rmtree(tmp_dir)
            except OSError as e:
                # Reraise unless ENOENT: No such file or directory
                # (ok if directory has already been deleted)
                if e.errno != errno.ENOENT:
                    raise

    def get_sample_file(self, name, content=b'*'):
        with tempfile.NamedTemporaryFile() as tf:
            tf.file.write(content)
            tf.file.seek(0)
            return SimpleUploadedFile(name, tf.file.read())

    def get_sample_image_file(self, name='photo.png'):
        return self.get_sample_file(
            name,
            content=b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00'
                    b'\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00'
                    b'\x0fIDAT\x08\x1d\x01\x04\x00\xfb\xff\x00\xff\xff\xff\x05'
                    b'\xfe\x02\xfe\x03}\x19\xc6\x00\x00\x00\x00IEND\xaeB`\x82')
