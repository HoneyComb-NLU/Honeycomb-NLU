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
from rasa_sdk.events import SlotSet
# import sqlite3
from ruamel.yaml import YAML
from thefuzz import fuzz, process
from ruamel.yaml.comments import CommentedMap as OrderedDict
import requests

### UPDATION AND INITIALIZATION
#   ===========================   #
# con = sqlite3.connect("database.db")
# cur = con.cursor()
# all_coins = [a for a in cur.execute("SELECT id, symbol, name FROM coin_list")]
all_coins = requests.get("https://api.coingecko.com/api/v3/coins/list").json()
currencies = requests.get("https://api.coingecko.com/api/v3/simple/supported_vs_currencies").json()
coin_ids = []
coin_symbol = []
coin_names = []
for i in all_coins:
    if (i['id'] != "" and i['symbol'] != "" and i['name'] != ""): 
        coin_ids.append(i['id'])
        coin_symbol.append(i['symbol'])
        coin_names.append(i['name'].lower())
currencies = [a for a in currencies]

yaml = YAML()
stream = open("./data/coins.yml", "r", encoding = 'utf-8')
stream1 = open("./data/currencies.yml", "r",encoding = 'utf-8')

ste = yaml.load(stream)
ste1 = yaml.load(stream1)

stream.close()
stream1.close()

stream = open("./data/coins.yml", "w", encoding = 'utf-8')
stream1 = open("./data/currencies.yml", "w", encoding = 'utf-8')

ste["nlu"][0]['examples'] = '- ' + '\n- '.join([i.replace('-', ' ') for i in coin_ids] + coin_names)
ste1["nlu"][0]['examples'] = '- ' + '\n- '.join(currencies)

yaml.dump(ste, stream)
yaml.dump(ste1, stream1)

stream.close()
stream1.close()

#   ===========================   #


### HELPER FUNCTION FOR FUZZY MATCHING
#   ===========================   #
def find_valid_options(coins, currency = None):
    if (coins == None):
        coins = []
    if (currency == None):
        currency = []
    valid_coins = []
    valid_currencies = []
    
    for i in coins:
        if i.replace(' ', '-') in coin_ids:
            print(f"Match in ids found!: {i}")
            valid_coins.append(i.replace(' ', '-'))
        elif i in coin_names:
            print(f"Match in names found!: {i}")
            valid_coins.append(coin_ids[coin_names.index(i)])
            print(coin_ids[coin_names.index(i)])
        else:
            ids = process.extractOne(i.replace(' ', '-'), coin_ids, scorer = fuzz.WRatio)[0]
            print(f"Closest id match: {ids}")
            names = process.extractOne(i, coin_names, scorer = fuzz.WRatio)[0]
            print(f"Closest name match: {names}")
            if (coin_ids.index(ids) != coin_names.index(names)):
                valid_coins.append(coin_ids[coin_names.index(names)])
            valid_coins.append(ids)
    for i in currency:
        if i in currencies:
            valid_currencies.append(i)
        else:
            c = process.extractOne(i, currencies, scorer = fuzz.WRatio)[0]
            valid_currencies.append(c)
        
    return {"coins" : valid_coins, "currencies" : valid_currencies}
 
#   ===========================   #


class ActionSearchCoin(Action):

    def name(self) -> Text:
        return "action_search_coin"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        msg = tracker.get_slot('coin')
        if not msg:
            coins = []
        else:
            coins = msg[0].lower()
            choices = find_valid_options(coins)['coins']
            print(choices)
        msg = {
            "intent": tracker.get_intent_of_latest_message(),
            "slots": {
                "coins": choices,
                "currencies": [],
                "time" : ""
            },
            "timestamp": datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        }
        dispatcher.utter_message(json_message=msg)
        return [SlotSet("coin", None)]
    


class ActionFetchPrice(Action):
    def name(self) -> Text:
        return "action_fetch_price"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        coin_raw = tracker.get_slot("coin")
        currency_raw = tracker.get_slot("currency")
        SlotSet("coin", None)
        SlotSet("currency", None)
        if not coin_raw:
            coin_raw = []
        elif not currency_raw:
            currency_raw = []

        coins = [i.lower() for i in list(set(coin_raw))]
        print(coins)
        currencies = [i.lower() for i in list(set(currency_raw))]
        print(currencies)
        choices = find_valid_options(coins, currencies)
        coins = choices['coins']
        currencies = choices['currencies']
        print(coins, currencies)
        intent = tracker.get_intent_of_latest_message()
        msg = {
            "intent": intent,
            "slots": {
                "coins": coins,
                "currencies": currencies,
                "time": ""
            },
            "timestamp": datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        }
        dispatcher.utter_message(json_message=msg)
        return []


class ActionGreet(Action):
    def name(self) -> Text:
        return "action_greet"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        intent = tracker.get_intent_of_latest_message()
        msg = {
            "intent": intent,
            "responses": "Hiya!",
            "timestamp": datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        }
        dispatcher.utter_message(json_message=msg)
        return []

class ActionHelp(Action):
    def name(self) -> Text:
        return "action_help"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        intent = tracker.get_intent_of_latest_message()
        msg = {
            "intent": intent,
            "responses": "Hey, I am Honeycomb.\nI am built to be your one-stop solution for all things Crypto. You can query any crypto related information and I will try my level best to provide you with the latest information.",
            "timestamp": datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        }
        dispatcher.utter_message(json_message=msg)
        return []
    
class ActionHappy(Action):
    def name(self) -> Text:
        return "action_happy"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        intent = tracker.get_intent_of_latest_message()
        msg = {
            "intent": intent,
            "responses": "That's great! So happy I could help you.",
            "timestamp": datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        }
        dispatcher.utter_message(json_message=msg)
        return []

class ActionGoodbye(Action):
    def name(self) -> Text:
        return "action_goodbye"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        intent = tracker.get_intent_of_latest_message()
        msg = {
            "intent": intent,
            "responses": "Hope to see you soon!",
            "timestamp": datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        }
        dispatcher.utter_message(json_message=msg)
        return []


class ActionUnhappy(Action):
    def name(self) -> Text:
        return "action_unhappy"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        intent = tracker.get_intent_of_latest_message()
        msg = {
            "intent": intent,
            "responses": "I apologize.",
            "timestamp": datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        }
        dispatcher.utter_message(json_message=msg)
        return []

class ActionBotChallenge(Action):
    def name(self) -> Text:
        return "action_bot_challenge"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        intent = tracker.get_intent_of_latest_message()
        msg = {
            "intent": intent,
            "responses": "Did I actually make you wonder whether I'm a bot or not?",
            "timestamp": datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        }
        dispatcher.utter_message(json_message=msg)
        return []


class ActionChart(Action):

    def name(self) -> Text:
        return "action_chart"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        coin_raw = tracker.get_slot('coin')
        currency_raw = tracker.get_slot('currency')
        time_raw = tracker.get_slot('time')
        chart_type = tracker.get_slot('chart_type')
        SlotSet("coin", None)
        SlotSet("currency", None)
        SlotSet("time", None)
        SlotSet("chart_type", None)
        if not coin_raw:
            coin_raw = []
        if not currency_raw:
            currency_raw = []
        if time_raw['to'] == None:
            time_raw['to'] = ""
        if time_raw['from'] == None:
            time_raw['from'] = ""
        if chart_type == None:
            chart_type = "price"
        coins = [i.lower() for i in list(set(coin_raw))]
        print(coins)
        currencies = [i.lower() for i in list(set(currency_raw))]
        print(currencies)
        choices = find_valid_options(coins, currencies)

        coins = choices['coins']
        currencies = choices['currencies']
        print(coins, currencies)

        intent = tracker.get_intent_of_latest_message()
        msg = {
            "intent": intent,
            "slots": {
                "coins": coins,
                "currencies": currencies,
                "time": time_raw,
                "chart_type": chart_type
            },
            "timestamp": datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        }
        dispatcher.utter_message(json_message=msg)
        return []
    
