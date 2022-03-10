import sqlite3
import pandas as pd

con = sqlite3.connect('Portfolios.db')
cur = con.cursor()

df = pd.read_sql_query("SELECT * from Portfolio1", con)
print(df)

print('yay it works')
