import os
import django
from splinter import Browser

username = "testuser"
password = "testpass123"

def before_all(context):
    context.browser = Browser()
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MTG_EDH_BUILDER.settings")
    django.setup()
    context.browser.cookies.delete()

def before_feature(context, feature):
    if feature.name == "Logout":
        log_in(context)

def log_in(context):
    from django.contrib.auth.models import User
    """
    Create a user if it doesn't exist
    """
    if not User.objects.filter(username=username).exists():
        User.objects.create_user(
            username=username,
            password=password,
        )

    """
    Log in
    """
    context.browser.visit("http://127.0.0.1:8002/accounts/login/")
    context.browser.fill("username", username)
    context.browser.fill("password", password)

    context.browser.find_by_id("login-submit").click()