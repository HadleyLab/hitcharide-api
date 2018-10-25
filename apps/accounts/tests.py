from unittest import mock
from config.tests import APITestCase

from apps.accounts.factories import UserFactory
from apps.accounts.models import User
from apps.main.test_utils import assert_mock_called_with


class RegistrationTestCase(APITestCase):
    @mock.patch('apps.dbmail_templates.email.send_mail')
    def test_registration(self, mock_send_mail):
        data = {
            'email': 'test@test.test',
            'password': '123'
        }

        resp = self.client.post('/accounts/register/', data, format='json')
        self.assertSuccessResponse(resp)
        assert_mock_called_with(
            mock_send_mail,
            'email_user_account_activation', ['test@test.test'],
            lambda value: self.assertEqual(
                value['user'].email,
                'test@test.test')
        )

        user = User.objects.get(pk=resp.data['pk'])
        self.assertTrue(user.check_password('123'))
        self.assertEqual(user.email, 'test@test.test')
        self.assertEqual(user.username, 'test@test.test')
        self.assertEqual(user.is_active, False)

    def test_registration_min_params_set(self):
        data = {
            'email': 'test@test.test',
            'password': '123',
        }

        resp = self.client.post('/accounts/register/', data, format='json')
        self.assertEqual(resp.status_code, 201)

    def test_registration_existing_email(self):
        user = UserFactory.create()
        data = {
            'email': user.email,
            'password': '123'
        }

        resp = self.client.post('/accounts/register/', data, format='json')
        self.assertBadRequest(resp)

    def test_login_jwt(self):
        resp = self.client.post('/accounts/login/', {
            'username': self.user.username,
            'password': self.password
        }, format='json')
        self.assertSuccessResponse(resp)
        token = resp.data['token']

        self.client.credentials(
            HTTP_AUTHORIZATION='JWT {0}'.format(token)
        )

        resp = self.client.get('/accounts/my/', format='json')
        self.assertSuccessResponse(resp)

        user = resp.data
        self.assertEqual(user['email'], self.user.email)
        self.assertEqual(user['first_name'], self.user.first_name)
        self.assertEqual(user['last_name'], self.user.last_name)

    def test_get_my_unauthorized(self):
        resp = self.client.get('/accounts/my/')
        self.assertUnauthorized(resp)

    def test_put_my_unauthorized(self):
        resp = self.client.put('/accounts/my/', {
            'phone': '+7 123 456 7890'
        })
        self.assertUnauthorized(resp)

    def test_my(self):
        self.authenticate()
        resp = self.client.get('/accounts/my/')
        self.assertSuccessResponse(resp)
        self.assertEqual(resp.data['pk'], str(self.user.pk))
        self.assertEqual(resp.data['email'], self.user.email)
        self.assertEqual(resp.data['first_name'], self.user.first_name)
        self.assertEqual(resp.data['last_name'], self.user.last_name)

    def test_put_my(self):
        self.authenticate()
        resp = self.client.put('/accounts/my/', {
            'phone': '+71234567890',
            'first_name': 'new first name',
            'last_name': 'last',
        })
        self.assertSuccessResponse(resp)

        self.user.refresh_from_db()
        self.assertEqual(self.user.phone, '71234567890')
        self.assertEqual(self.user.first_name, 'new first name')

        resp = self.client.put('/accounts/my/', {
            'phone': '71234567890',
            'first_name': 'new first name',
            'last_name': 'last',
            'paypal_account': 'teeest@test.test'
        })
        self.assertSuccessResponse(resp)
        self.user.refresh_from_db()
        self.assertEqual(self.user.paypal_account, 'teeest@test.test')

    def test_put_my_not_filled(self):
        self.authenticate()
        self.user.phone = None
        self.user.first_name = ''
        self.user.last_name = ''
        self.user.save()

        resp = self.client.put('/accounts/my/', {
            'first_name': 'new first name'
        })
        self.assertBadRequest(resp)

        resp = self.client.put('/accounts/my/', {
            'first_name': 'new first name',
            'last_name': 'new last name',
            'phone': ''
        })
        self.assertBadRequest(resp)

    def test_update(self):
        self.authenticate()
        self.user.phone = '+71111111111'
        self.user.is_phone_validated = True
        self.user.save()

        self.client.put('/accounts/my/', {
            'phone': '+72222222222'
        })

        self.assertEqual(self.user.is_phone_validated, False)


class UserProfileTestCase(APITestCase):
    def setUp(self):
        super(UserProfileTestCase, self).setUp()
        self.destination_user = UserFactory.create(phone='+72222222222')
        self.user.phone = '+71111111111'
        self.user.save()

    @mock.patch('apps.accounts.viewsets.twilio_create_proxy_phone')
    def test_create_proxy_phone_success(self, mock_twilio_create_proxy_phone):
        mock_twilio_create_proxy_phone.return_value = '+10000000000'

        self.authenticate()
        self.user.is_phone_validated = True
        self.user.save()
        self.destination_user.is_phone_validated = True
        self.destination_user.save()

        resp = self.client.post('/accounts/{0}/create_proxy_phone/'.format(
            self.destination_user.pk))
        self.assertSuccessResponse(resp)
        self.assertEqual(resp.data['proxy_phone'], '+10000000000')

    @mock.patch('apps.accounts.viewsets.twilio_create_proxy_phone')
    def test_create_proxy_phone_with_twilio_error_failed(
            self, mock_twilio_create_proxy_phone):
        mock_twilio_create_proxy_phone.return_value = None

        self.authenticate()
        self.user.is_phone_validated = True
        self.user.save()
        self.destination_user.is_phone_validated = True
        self.destination_user.save()

        resp = self.client.post('/accounts/{0}/create_proxy_phone/'.format(
            self.destination_user.pk))
        self.assertInternalServerError(resp)

    @mock.patch('apps.accounts.viewsets.twilio_create_proxy_phone')
    def test_create_proxy_phone_without_source_phone_failed(
            self, mock_twilio_create_proxy_phone):
        mock_twilio_create_proxy_phone.return_value = '+10000000000'

        self.authenticate()
        self.destination_user.is_phone_validated = True
        self.destination_user.save()

        resp = self.client.post('/accounts/{0}/create_proxy_phone/'.format(
            self.destination_user.pk))
        self.assertBadRequest(resp)

    @mock.patch('apps.accounts.viewsets.twilio_create_proxy_phone')
    def test_create_proxy_phone_without_destination_phone_failed(
            self, mock_twilio_create_proxy_phone):
        mock_twilio_create_proxy_phone.return_value = '+10000000000'

        self.authenticate()
        self.user.is_phone_validated = True
        self.user.save()

        resp = self.client.post('/accounts/{0}/create_proxy_phone/'.format(
            self.destination_user.pk))
        self.assertBadRequest(resp)
