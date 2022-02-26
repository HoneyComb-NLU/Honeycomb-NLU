from ruamel.yaml import YAML
import sys
import sqlite3

con = sqlite3.connect("database.db")
cur = con.cursor()
coin_ids = ["- " + a[0].replace('-', ' ') for a in cur.execute("SELECT id FROM coin_list")]
con.close()

yaml = YAML()

with open('./data/test.yml', "r") as stream:
    ste = yaml.load(stream)
    ste["nlu"][0]['examples'] = '\n'.join(coin_ids)

with open('./data/coins.yml', "w") as stream:
    yaml.dump(ste, stream)


# with open("./data/test.yml", "w") as f:
#     yaml.dump(ste, f)
