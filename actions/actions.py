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

yaml = YAML()

with open('./data/coins.yml', "r") as stream:
    ste = yaml.load(stream)
    ste["nlu"][0]['examples'] = '- ' + '\n- '.join(coin_ids)

with open('./data/coins.yml', "w") as stream:
    yaml.dump(ste, stream)


class ActionHelloWorld(Action):

    def name(self) -> Text:
        return "action_search_coin"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        msg = lower(tracker.get_slot('coin'))
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
