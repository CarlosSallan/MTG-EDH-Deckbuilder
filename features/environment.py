import os
import django
from splinter import Browser

def before_all(context):
    context.browser = Browser()
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MTG_EDH_BUILDER.settings")
    django.setup()

def before_feature(context, feature):
    if feature.name == "Login":
        context.browser.cookies.delete()