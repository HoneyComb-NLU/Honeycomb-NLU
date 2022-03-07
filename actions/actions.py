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
import sqlite3
from ruamel.yaml import YAML
from thefuzz import fuzz, process
from ruamel.yaml.comments import CommentedMap as OrderedDict

### COIN UPDATE
con = sqlite3.connect("database.db")
cur = con.cursor()
all_coins = [a for a in cur.execute("SELECT id, symbol, name FROM coin_list")]
coin_ids = []
coin_symbol = []
coin_names = []
for i in all_coins:
    coin_ids.append(i[0].replace('-', ' '))
    coin_symbol.append(i[1])
    coin_names.append(i[2])
currencies = [a[0] for a in cur.execute("SELECT id FROM supported_currencies")]

yaml = YAML()
stream = open("./data/coins.yml", "r", encoding = 'utf-8')
stream1 = open("./data/currencies.yml", "r",encoding = 'utf-8')
# stream2 = open("./data/coin_syn.yml", "r", encoding = 'utf-8')
ste = yaml.load(stream)
ste1 = yaml.load(stream1)
# ste2 = yaml.load(stream2)
stream.close()
stream1.close()
# stream2.close()

stream = open("./data/coins.yml", "w", encoding = 'utf-8')
stream1 = open("./data/currencies.yml", "w", encoding = 'utf-8')
# stream2 = open("./data/coin_syn.yml", "w", encoding = 'utf-8')

ste["nlu"][0]['examples'] = '- ' + '\n- '.join(coin_ids + coin_names)
ste1["nlu"][0]['examples'] = '- ' + '\n- '.join(currencies)
# num = 0
# ste2['nlu'] = []
# for i, j, k in zip(coin_ids, coin_symbol, coin_names):
#     num = num + 1
#     d = OrderedDict([('synonym', i),
#         ('examples', f'- {j}\n- {k}')])
#     ste2['nlu'].append(d)

# print(num)

yaml.dump(ste, stream)
yaml.dump(ste1, stream1)
# yaml.representer.ignore_aliases = lambda *data: True
# yaml.dump(ste2, stream2)

stream.close()
stream1.close()
# stream2.close()

# def match_fuzzwuzz(coins, currency = None):
#     matched_coins = []
#     matched_currencies = []
#     coins = [i.lower() for i in coins]
#     currency = [i.lower() for i in currency]

#     # FOR COINS
#     if coins:
#         if len(coins) == 1:
#             if (coins[0]) not in coin_ids:
#                 similar = process.extract(coins[0], coin_ids, scorer = fuzz.WRatio, limit = 5)
#                 for i in similar:
#                     matched_coins.append(i[0].replace(' ', '-'))
#             else:
#                 matched_coins = coins
#         else:
#             for i in coins:
#                 if i not in coin_ids:
#                     c = process.extractOne(i, coin_ids, scorer = fuzz.WRatio)[0]
#                     matched_coins.append(c.replace(' ', '-'))
#                 else:
#                     matched_coins.append(i)
    
#     # FOR CURRENCIES
#     if currency:
#         if len(currency) == 1:
#             if currency[0] not in currencies:
#                 similar = process.extract(currency[0], currencies, scorer = fuzz.WRatio, limit = 2)
#                 for i in similar:
#                     matched_currencies.append(i[0])
#             else:
#                 matched_currencies = currency
#         else:
#             for i in currency:
#                 if i not in currencies:
#                     c = process.extractOne(i, currencies, scorer = fuzz.WRatio)[0]
#                     matched_currencies.append(c)
#                 else:
#                     matched_currencies.append(i)
                    
#     return {"coins" : matched_coins, "currencies" : matched_currencies}

        


class ActionSearchCoin(Action):

    def name(self) -> Text:
        return "action_search_coin"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        msg = tracker.get_slot('coin')[0].lower()
        print(msg)
        ### If id directly available
        # if msg in coin_ids:
        #     choices = [msg.replace(' ', '-')]
        # else:
        #     dispatcher.utter_message("We could not find an exact match. Please check the ones below.")
        #     similar = process.extract(msg, coin_ids, limit = 5, scorer = fuzz.WRatio)
        #     choices = []
        #     for match in similar:
        #         choices.append(match[0].replace(' ', '-'))
        # choices = match_fuzzwuzz(msg)['coins']
        # print(choices)
        msg = {
            "intent": {
                "name": tracker.get_intent_of_latest_message()
            },
            "slots": {
                "coins": msg
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
        coins = list(set(tracker.get_slot("coin")))
        print(coins)
        currencies = list(set(tracker.get_slot("currency")))
        print(currencies)
            # choices = match_fuzzwuzz(coins, currencies)
            # coins = choices['coins']
            # currencies = choices['currencies']
        intent = tracker.get_intent_of_latest_message()
        msg = {
            "intent": {
                "name": intent
            },
            "slots": {
                "coins": coins,
                "currencies": currencies
            },
            "timestamp": datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        }
        dispatcher.utter_message(json_message=msg)
        return [SlotSet("coin", None), SlotSet("currency", None)]