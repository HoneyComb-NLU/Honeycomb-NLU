import sqlite3
from ruamel.yaml import YAML
from collections import OrderedDict
from ruamel.yaml.comments import CommentedMap as OrderedDict
import sys

yaml = YAML()
con = sqlite3.connect("database.db")
cur = con.cursor()
alla = [a for a in cur.execute("SELECT id, symbol, name FROM coin_list")]
coin_ids = []
coin_symbol = []
coin_names = []
for i in alla:
    coin_ids.append(i[0].replace('-', ' '))
    coin_symbol.append(i[1])
    coin_names.append(i[2])

# for i, j, k in zip(coin_ids, coin_symbol, coin_names):
#     print(i, j, k)

file_coins = open('coins.yml', "r")
file_coinsym = open('coin_syn.yml', "r", encoding = 'utf-8')
stream_coins = yaml.load(file_coins)
stream_coinsym = yaml.load(file_coinsym)
print(stream_coinsym)
for i, j, k in zip(coin_ids, coin_symbol, coin_names):
    d = OrderedDict([('synonym', i),
        ('examples', [j, k])])
    stream_coinsym['nlu'].append(d)
yaml.representer.ignore_aliases = lambda *data: True
file_coins.close()
file_coinsym.close()
file_coinsym_write = open('coin_syn.yml', 'w', encoding='utf-8')
yaml.dump(stream_coinsym, file_coinsym_write)
cur.close()