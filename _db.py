import json
import sqlite3
from datetime import datetime, timedelta

with open("config.json") as f:
    config = json.load(f)

db = config["database"]

def select_all_from(table, conditions:str, data):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute(f"SELECT * FROM {table} WHERE {conditions}", data)
    tmp = c.fetchall()
    c.close()
    conn.close()
    return tmp

def select_one_from(table, conditions:str, data):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute(f"SELECT * FROM {table} WHERE {conditions}", data)
    tmp = c.fetchone()
    c.close()
    conn.close()
    return tmp

def insert_into(table, data):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    conditions = '?,'*len(data)
    conditions = conditions[:-1]
    query = f"INSERT INTO {table} VALUES ({conditions})"
    c.execute(query, data)
    c.close()
    conn.commit()
    conn.close()

def update(table, set_cond:str, where_cond:str, data):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute(f"UPDATE {table} SET {set_cond} WHERE {where_cond}", data).rowcount
    c.close()
    conn.commit()
    conn.close()

def add_coins_to(discordID:int, coins:int):
    data = (coins, discordID)
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute(f"UPDATE bot_member SET money = money + ? WHERE discordID = ?", data).rowcount
    c.close()
    conn.commit()
    conn.close()

def delete_from(table, conditions:str, data):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute(f'DELETE FROM {table} WHERE {conditions}', data)
    conn.commit()
    c.close()
    conn.close()

def delete_tables_content(table):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    query = 'DELETE FROM {}'.format(table)
    
    c.execute(query)
    conn.commit()
    c.close()
    conn.close()

def isNumber(number):
    try:
        float(number)
        return True
    except ValueError as identifier:
        return False

def isCorrect(betType, arr):
    if ((betType != 'SH') and (betType != 'GT')):
        return False

    if (len(arr) < 2) or (len(arr)%2 == 1):
        return False

    for i in range(0, len(arr)-1, 2):

        if (not isNumber(arr[i])) or (not isNumber(arr[i+1])):
            return False

        if (len(arr[i]) != 2):
            return False

        if (int(arr[i])) < 0 or (int(arr[i])) > 99:
            return False
            
        if (float(arr[i+1]) < 1000 or (float(arr[i+1]) > 50000)):
            return False

    return True
