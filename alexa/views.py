from django.http.response import JsonResponse

# Create your views here.
def notify_computer(r):
    print(r.POST)
    return JsonResponse(
        {
            "response": {
                "outputSpeech": {
                    "type": "SSML",
                    "ssml": "<speak>I GOT THE MESSAGE</speak>"
                },
                "shouldEndSession": True
            },
            "version": "1.0",
        }
    )
