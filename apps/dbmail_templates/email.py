from dbmail import send_db_mail
from djoser.email import ActivationEmail, ConfirmationEmail, PasswordResetEmail
from templated_mail.mail import BaseEmailMessage

from apps.main.utils import send_mail


class DBMailEmail(BaseEmailMessage):
    """
    In this class we overrode the send method to send mail via dbmail
    """
    def send(self, to, *args, **kwargs):
        # super(DBMailEmail, self).send()
        context = self.get_context_data()
        send_mail(self.template_name, to, context)

    def get_context_data(self):
        context = super(DBMailEmail, self).get_context_data()
        context.pop('view')
        return context


class ActivationDBMailEmail(DBMailEmail, ActivationEmail):
    template_name = 'account_activate'


class ConfirmationDBMailEmail(DBMailEmail, ConfirmationEmail):
    template_name = 'account_confirmation'


class PasswordResetDBMailEmail(DBMailEmail, PasswordResetEmail):
    template_name = 'account_password_reset'
