# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from datetime import datetime


class ActionHelloWorld(Action):

    def name(self) -> Text:
        return "action_search_coin"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        msg = {
            "intent": {
                "name": tracker.get_intent_of_latest_message()
            },
            "slots": {
                "coins": tracker.get_slot('coin')
            },
            "timestamp": datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        }
        dispatcher.utter_message(json_message=msg)
        return []
