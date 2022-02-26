import sqlite3


con = sqlite3.connect("database.db")
cur = con.cursor()
alla = [a for a in cur.execute("SELECT symbol, name FROM coin_list WHERE id = \"bitcoin\"")][0]
coin_s, coin_n = alla
print(coin_s, coin_n)
cur.close()