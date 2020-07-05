from django.db.models import *


class Family(Model):
    """
    An alexa account. Has foreign keys to it for apps
    """
    # amazon id sent with alexa requests
    amazon_id = TextField()
    # a setup code that computers can enter to join family
    setup_code = CharField(max_length=50)


class App(Model):
    """
    A single app.
    """
    # a uuid for the app
    app_id = CharField(max_length=50)
    # the consumer's channel name, if not connected, is Null
    channel_name = TextField(null=True)
    # the family the device belongs to
    family = ForeignKey(Family, on_delete=CASCADE)
    # name of owner
    name = CharField(max_length=50)
