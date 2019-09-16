import json
import requests
from adapt.intent import IntentBuilder
from mycroft import MycroftSkill, intent_handler

class RasaSkill(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    def initialize(self):
        # Set the address of your Rasa's REST endpoint
        self.RASA_API = "http://localhost:5005/webhooks/rest/webhook"
        self.messages = []

    def query_rasa(self, prompt=None):
        if self.conversation_active == False:
            return
        if prompt is None and len(self.messages) > 0:
            prompt = self.messages[-1]
        # Speak message to user and save the response
        msg = self.get_response(prompt)
        # If user doesn't respond, quietly stop, allowing user to resume later
        if msg is None:
            return
        # Else reset messages
        self.messages = []
        # Send post requests to said endpoint using the below format.
        # "sender" is used to keep track of dialog streams for different users
        data = requests.post(
            self.RASA_API, json = {"message" : msg, "sender" : "mycroftUser"}
        )
        # A JSON Array Object is returned: each element has a user field along
        # with a text, image, or other resource field signifying the output
        # print(json.dumps(data.json(), indent=2))
        for nextResponse in data.json():
            if "text" in nextResponse:
                self.messages.append(nextResponse["text"])

        # Output all but one of the Rasa dialogs
        if len(self.messages) > 1:
            for rasa_message in self.messages[:-1]:
                print(rasa_message)
        if len(self.messages) == 0:
            self.messages = ["no response from rasa"]
            return
        # Use the last dialog from Rasa to prompt for next input from the user
        prompt = self.messages[-1]
        return self.query_rasa(prompt)

    @intent_handler(IntentBuilder("StartChat").require("Chatwithrasa"))
    def handle_talk_to_rasa_intent(self, message):
        self.conversation_active = True
        prompt = "start"
        self.query_rasa(prompt)

    @intent_handler(IntentBuilder("ResumeChat").require("Resume"))
    def handle_resume_chat(self, message):
        self.conversation_active = True
        self.query_rasa()

    def stop(self):
        self.conversation_active = False

def create_skill():
    return RasaSkill()
