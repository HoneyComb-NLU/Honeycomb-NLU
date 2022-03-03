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
import sqlite3
from ruamel.yaml import YAML
from thefuzz import fuzz, process

### COIN UPDATE
con = sqlite3.connect("database.db")
cur = con.cursor()
coin_ids = [a[0].replace('-', ' ') for a in cur.execute("SELECT id FROM coin_list")]
currencies = [a[0] for a in cur.execute("SELECT id FROM supported_currencies")]

yaml = YAML()
stream = open("./data/coins.yml", "r")
stream1 = open("./data/currencies.yml", "r")
ste = yaml.load(stream)
ste1 = yaml.load(stream1)
stream.close()
stream1.close()

stream = open("./data/coins.yml", "w")
stream1 = open("./data/currencies.yml", "w")

ste["nlu"][0]['examples'] = '- ' + '\n- '.join(coin_ids)
ste1["nlu"][0]['examples'] = '- ' + '\n- '.join(currencies)

yaml.dump(ste, stream)
yaml.dump(ste1, stream1)


class ActionSearchCoin(Action):

    def name(self) -> Text:
        return "action_search_coin"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        msg = tracker.get_slot('coin').lower()
        print(msg)
        ### If id directly available
        if msg in coin_ids:
            choices = [msg]
        else:
            dispatcher.utter_message("We could not find an exact match. Please check the ones below.")
            similar = process.extract(msg, coin_ids, limit = 5, scorer = fuzz.WRatio)
            choices = []
            for match in similar:
                choices.append(match[0])

        print(choices)
        for each in choices:
            coin_all = [a for a in cur.execute(f"SELECT symbol, name FROM coin_list WHERE id = \"{each}\"")][0]
            coin_symbol, coin_name = coin_all[0], coin_all[1]
            dispatcher.utter_message(f"Coin symbol: {coin_symbol}|Coin name: {coin_name}|")
        return []
