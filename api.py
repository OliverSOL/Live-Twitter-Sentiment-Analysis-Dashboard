#SOLyktv
# fetches tweets from DB

import sqlite3
import pandas as pd

def fetchTweets(query):

	conn = sqlite3.connect('StreamingDB.db')
	c = conn.cursor()
	df = pd.read_sql(query, conn)
	return df
	
