# -*- coding: utf-8 -*-
import json
import pyodbc

with open('config.json') as f:
    config = json.load(f)

driver_sv1 = config['driver_sv2']
server_sv1 = config['server_sv2']
database_sv1 = config['database_sv2']

def select_from(table, ingame:str):
    conn = pyodbc.connect(
            "Driver={};"
            "Server={};"
            "Database={};"
            "Trusted_Connection=yes;".format(driver_sv1,server_sv1,database_sv1)
        )
    conn.setencoding(encoding='utf-8')

    cursor = conn.cursor()
    b1 = cursor.execute(f"Select NickName, money from {table} where NickName=?", ingame.encode('utf-16')).fetchone()
    cursor.close()
    conn.close()
    return b1

# nn = 'Devil'
# print(select_from('Sys_Users_Detail', nn.encode('utf-16')))
