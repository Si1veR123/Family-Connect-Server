from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from channels.layers import get_channel_layer
from . models import *
import json
import random

WORDS = [
    "hotdog",
    "burger",
    "fruit",
    "pizza",
    "chicken",
    "egg",
    "fries",
    "chips",
    "salad",
    "steak",
    "cheese",
    "pasta",
    "bread",
    "cookie",
    "pie"
]


def get_alexa_response(ssml: str):
    return {
        "response": {
            "outputSpeech": {
                "type": "SSML",
                "ssml": f"<speak>{ssml}</speak>"
            },
            "shouldEndSession": True
        },
        "version": "1.0",
    }


def generate_code_speech(code: str = None):
    if code is None:
        while True:
            # TODO keep looping until unique code in future
            code = random.choice(WORDS) + str(random.randint(0, 99))
            break

    return {"code": code, "ssml": f"""
Hello, this device isn\'t recognised. 
I will help you register. Your code is 
<break time="1s"/>
<prosody rate="slow">
<say-as interpret-as="spell-out">{code}</say-as>
</prosody>
That is
<break time="1s"/>
<prosody rate="slow">
<say-as interpret-as="spell-out">{code}</say-as>
</prosody>
Enter this on the Family Connect app.
"""}


CHANNEL_LAYER = get_channel_layer()


@require_POST
@csrf_exempt
def alexa(r):
    data = json.loads(r.read())

    # check that the requestor is the alexa skill
    if data["session"]["application"]["applicationId"] != "amzn1.ask.skill.5904720e-83aa-4aac-8347-a14b06887456":
        return JsonResponse({"error": "Skill doesn't match ID"})

    # check if alexa account is part of a family, if not, create and send back code
    amazon_id_request = data["session"]["user"]["userId"]
    try:
        family = Family.objects.get(amazon_id=amazon_id_request)
    except Family.DoesNotExist:
        # new family
        code = generate_code_speech()
        Family.objects.create(amazon_id=data["session"]["user"]["userId"], setup_code=code["code"])
        return JsonResponse(get_alexa_response(code["ssml"]))

    # if it is an intent request (not launch, cancel etc.)
    if data["request"]["type"] == "IntentRequest":
        # get intent name
        intent = data["request"]["intent"]["name"]
        # notify intent has 2 slots, who and what. The what is sent to the who as a message through a websocket connection
        if intent == "notify":
            # get name from data
            who = data["request"]["intent"]["slots"]["who"]["value"]
            # get all family members
            family_members = App.objects.filter(family=family.id)

            # check that it isnt empty, or return no devices registered
            if len(family_members) == 0:
                return JsonResponse(get_alexa_response("No devices are registered"))

            # if it is all, recipents are all members
            if who.lower() == "all":
                family_recipents = family_members
            else:
                # filter the queryset to names
                family_recipents = family_members.filter(name=who.lower())

            # check that there are any recipents
            if len(family_recipents) == 0:
                return JsonResponse(get_alexa_response("Can't find name of family member"))

            message = data["request"]["intent"]["slots"]["what"]["value"]
            message_sent = False

            # send data to all recipents
            for r in family_recipents.iterator():
                # if channel name of recipent is Null/None, app is not connected
                if r["channel_name"] is not None:
                    CHANNEL_LAYER.send(r["channel_name"], {
                        "type": "notification",
                        "text": message
                    })
                    message_sent = True

            if message_sent:
                return JsonResponse(get_alexa_response("Message sent"))

            return JsonResponse(get_alexa_response("No messages were sent. Likely that no family computers are connected."))

        # another intent is asking to get the setup code, returns code
        elif intent == "setupCode":
            return JsonResponse(get_alexa_response(generate_code_speech(family.setup_code)["ssml"]))
    else:
        # anything else (launch etc.) just send a preset message
        return JsonResponse(get_alexa_response("This is Family Connect"))
