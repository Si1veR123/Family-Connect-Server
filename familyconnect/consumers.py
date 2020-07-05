from channels.generic.websocket import WebsocketConsumer
from . models import *
import json
import uuid


class FamilyConnectConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, code):
        try:
            app = App.objects.get(channel_name=self.channel_name)
            app.channel_name = None
            app.save()
        except App.DoesNotExist:
            pass

    def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        if data["type"] == "register":
            # check if id given and exists, or create new app
            id = data["data"].get("id")
            if id and App.objects.filter(app_id=id).exists():
                app = App.objects.get(app_id=id)
                app.channel_name = self.channel_name
                self.send(text_data="{'result': 'success', 'info': 'found existing family'}")
            else:
                # joining new family
                setup_code = data["data"].get("code")
                try:
                    family = Family.objects.get(setup_code=setup_code)
                except Family.DoesNotExist:
                    self.send(text_data="{'result': 'error', 'error': 'Invalid Setup Code'}")
                    return

                while True:
                    app_id = str(uuid.uuid1())[:49]
                    if not App.objects.filter(app_id=app_id).exists():
                        break


                App.objects.create(
                    app_id=app_id,
                    channel_name=self.channel_name,
                    family=family,
                    name=data["data"]["name"]
                )
                self.send(text_data="{'result': 'success', 'info': 'joined new family'}")
