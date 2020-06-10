import structlog
from django import forms
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import FormView
from sesame import utils

from main.models.user import User

logger = structlog.get_logger(__name__)


class EmailForm(forms.Form):
    email = forms.EmailField()


class Signup(FormView):
    form_class = EmailForm
    template_name = "signup.html"

    def get_success_url(self):
        return reverse("signup") + "?sent=1"

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        user, created = User.objects.get_or_create(email=email)
        login_token = utils.get_query_string(user)

        logo_url = "/static/images/logo-vertical.png"
        logo_src = "http://{}{}".format(self.request.get_host(), logo_url)
        login_link = "http://{}/{}".format(self.request.get_host(), login_token)

        html_message = render_to_string(
            "email/magiclink_login_message.html",
            {"login_link": login_link, "logo_src": logo_src},
        )

        send_mail(
            "Hospital Aid Login Link",
            html_message,
            "admin@domain.com",
            [email],
            fail_silently=False,
            html_message=html_message,
        )

        logger.info("Signup requested. Sent email.", email=email)
        return super().form_valid(form)
