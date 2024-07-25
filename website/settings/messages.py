from django.contrib.messages import constants as message_constants

from .env import DEBUG

# Messages
# https://docs.djangoproject.com/en/stable/ref/settings/#messages
MESSAGE_LEVEL = message_constants.DEBUG if DEBUG else message_constants.INFO
MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"
