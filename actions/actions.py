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
import asyncio
import random

### UPDATION AND INITIALIZATION
#   ===========================   #
# con = sqlite3.connect("database.db")
# cur = con.cursor()
# all_coins = [a for a in cur.execute("SELECT id, symbol, name FROM coin_list")]
all_coins = requests.get("https://api.coingecko.com/api/v3/coins/list").json()
currencies = requests.get("https://api.coingecko.com/api/v3/simple/supported_vs_currencies").json()
responses = {"greet": ["Hi", "Hey there!", "Hello thereeeee", "ayo waddup boi", "wazaaaaaaaaaaaaaaaaap", "Hiya!"],
"affirm" : ["That's great!", "That is good to hear.", "who tf asked bro", "no shit bitch", "I'm so glad :D"],
"goodbye" : ["Wish I never see you again.", "Hope to see you again!", "so happy to see you go", "Byeeeeeeeeee.", "SIKE YEET"],
"deny" : ["well, not my problem", "looks like a `you` problem dude", "Awww ;-; Hope I can do better next time", "Get yourself a cuppa coffee and chill out!"],
"bot_challenge" : ["Did I actually make you wonder if I was a human?", "Dude. Get a life.", "Hey, that's creepy and invasive, please.", "No, I'm a real and sentient being and I'm getting your address right now so I can come pay you a visit :D"],
"chit_chat" : ["Dude, I'm a crypto chatbot, do you understand?", "Wow, you got thick skin up there asking me that.", "I know the answer to that but I'm not in the mood to answer that."],
"nlu_fallback" : ["I'm sorry, I don't understand what you mean by that.", "The answer to this is not in my scope.", "Oi, plenty of other bots out there who can answer that."]}
coin_ids = []
coin_symbols = []
coin_names = []
for i in all_coins:
    if (i['id'] != "" and i['symbol'] != "" and i['name'] != ""): 
        coin_ids.append(i['id'])
        coin_symbols.append(i['symbol'])
        coin_names.append(i['name'].lower())
currencies = [a for a in currencies]

yaml = YAML()
# stream = open("./data/coins.yml", "r", encoding = 'utf-8')
stream1 = open("./data/currencies.yml", "r",encoding = 'utf-8')

# ste = yaml.load(stream)
ste1 = yaml.load(stream1)

# stream.close()
stream1.close()

# stream = open("./data/coins.yml", "w", encoding = 'utf-8')
stream1 = open("./data/currencies.yml", "w", encoding = 'utf-8')

# ste["nlu"][0]['examples'] = '- ' + '\n- '.join([i.replace('-', ' ') for i in coin_ids] + coin_names)
ste1["nlu"][0]['examples'] = '- ' + '\n- '.join(currencies)

# yaml.dump(ste, stream)
yaml.dump(ste1, stream1)

# stream.close()
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
    print("===================================================")
    print(f"Searching for valid coins; Original: {coins}")
    for i in coins:
        if i.replace(' ', '-') in coin_ids:
            print(f"Match in ids found!: {i}")
            valid_coins.append(i.replace(' ', '-'))
        elif i in coin_names:
            print(f"Match in names found!: {i}")
            valid_coins.append(coin_ids[coin_names.index(i)])
        elif i.replace(' ', '') in coin_symbols:
            print(f"Match in symbols found!: {i}")
            ls = [x for x, y in enumerate(coin_symbols) if y == i.replace(' ', '')]
            valid_coins.extend([coin_ids[i] for i in ls])
        else:
            ids = process.extractOne(i.replace(' ', '-'), coin_ids)[0]
            print(f"Closest id match: {ids}")
            names = process.extractOne(i, coin_names)[0]
            print(f"Closest name match: {names}")
            if (coin_ids.index(ids) != coin_names.index(names)):
                valid_coins.append(coin_ids[coin_names.index(names)])
            valid_coins.append(ids)
    print(f"Searching for valid currencies; Original: {currency}")
    for i in currency:
        if i in currencies:
            valid_currencies.append(i)
        else:
            c = process.extractOne(i, currencies, scorer = fuzz.WRatio)[0]
            valid_currencies.append(c)
    print("===================================================")
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
            coins = list()
        else:
            coins = [msg[0].lower()]
        choices = find_valid_options(coins)['coins']
        print("***********************************************")
        print(f"Search coin intent: choices are {choices}")
        msg = {
            "intent": tracker.get_intent_of_latest_message(),
            "slots": {
                "coins": choices,
                "currencies": [],
                "time" : {},
                "chart_type" : ""
            },
            "timestamp": datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        }
        print("***********************************************")
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
        if not coin_raw:
            coin_raw = list()
        if not currency_raw:
            currency_raw = list()

        coins = [i.lower() for i in list(set(coin_raw))]
        currencies = [i.lower() for i in list(set(currency_raw))]
        choices = find_valid_options(coins, currencies)
        coins = choices['coins']
        currencies = choices['currencies']
        print("***********************************************")
        print(f"Price intent: Coins {coins}, currencies {currencies}")
        intent = tracker.get_intent_of_latest_message()
        msg = {
            "intent": intent,
            "slots": {
                "coins": coins,
                "currencies": currencies,
                "time": {},
                "chart_type" : ""
            },
            "timestamp": datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        }
        print("***********************************************")
        dispatcher.utter_message(json_message=msg)
        return [SlotSet("coin", None),
        SlotSet("currency", None)]


class ActionGreet(Action):
    def name(self) -> Text:
        return "action_greet"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        intent = tracker.get_intent_of_latest_message()
        response = random.choice(responses["greet"])
        msg = {
            "intent": intent,
            "responses": response,
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
        response = random.choice(responses["affirm"])
        msg = {
            "intent": intent,
            "responses": response,
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
        response = random.choice(responses["goodbye"])
        msg = {
            "intent": intent,
            "responses": response,
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
        response = random.choice(responses["deny"])
        msg = {
            "intent": intent,
            "responses": response,
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
        response = random.choice(responses["bot_challenge"])
        msg = {
            "intent": intent,
            "responses": response,
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
        if not coin_raw:
            coin_raw = list()
        print(currency_raw)
        if not currency_raw:
            currency_raw = list()
        if time_raw == None:
            time_raw = ""
        if chart_type == None:
            chart_type = "price"
        coins = [i.lower() for i in list(set(coin_raw))]
        currencies = [i.lower() for i in list(set(currency_raw))]
        choices = find_valid_options(coins, currencies)

        coins = choices['coins']
        currencies = choices['currencies']
        print("***********************************************")
        print(f"Chart intent: Coins {coins}, currencies {currencies}, chart type {chart_type}")
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
        print("***********************************************")
        dispatcher.utter_message(json_message=msg)
        return [SlotSet("coin", None),
        SlotSet("currency", None),
        SlotSet("time", None),
        SlotSet("chart_type", None)]
    

class ActionCoinData(Action):
    def name(self) -> Text:
        return "action_coin_data"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        coin_raw = tracker.get_slot("coin")
        currency_raw = tracker.get_slot("currency")
        if not coin_raw:
            coin_raw = list()
        if not currency_raw:
            currency_raw = list()

        coins = [i.lower() for i in list(set(coin_raw))]
        currencies = [i.lower() for i in list(set(currency_raw))]
        choices = find_valid_options(coins, currencies)
        coins = choices['coins']
        currencies = choices['currencies']
        print("***********************************************")
        print(f"Coin data intent: Coins {coins}, currencies {currencies}")
        intent = tracker.get_intent_of_latest_message()
        msg = {
            "intent": intent,
            "slots": {
                "coins": coins,
                "currencies": currencies,
                "time": {},
                "chart_type" : ""
            },
            "timestamp": datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        }
        print("***********************************************")
        dispatcher.utter_message(json_message=msg)
        return [SlotSet("coin", None),
        SlotSet("currency", None)]


class ActionChitChat(Action):
    def name(self) -> Text:
        return "action_chit_chat"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        intent = tracker.get_intent_of_latest_message()
        response = random.choice(responses["chit_chat"])
        msg = {
            "intent": intent,
            "responses": response,
            "timestamp": datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        }
        dispatcher.utter_message(json_message=msg)
        return []

class ActionFallback(Action):
    def name(self) -> Text:
        return "action_fallback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        intent = tracker.get_intent_of_latest_message()
        response = random.choice(responses["nlu_fallback"])
        msg = {
            "intent": intent,
            "responses": response,
            "timestamp": datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        }
        dispatcher.utter_message(json_message=msg)
        return []

class ActionGlobalHoldings(Action):

    def name(self) -> Text:
        return "action_global_holdings"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        msg = tracker.get_slot('coin')
        if not msg:
            coins = list()
        else:
            coins = [msg[0].lower()]
        choices = [i for i in find_valid_options(coins)['coins'] if i == "bitcoin" or i == "ethereum"]
        print("***********************************************")
        print(f"Search coin intent: choices are {choices}")
        msg = {
            "intent": tracker.get_intent_of_latest_message(),
            "slots": {
                "coins": choices,
                "currencies": [],
                "time" : {},
                "chart_type" : ""
            },
            "timestamp": datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        }
        print("***********************************************")
        dispatcher.utter_message(json_message=msg)
        return [SlotSet("coin", None)]
    