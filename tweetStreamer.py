# import packages
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener

import json
import time
import sqlite3

from textblob import TextBlob
from unidecode import unidecode

# keywords to look out for
keyword = ['#Amazon']

# ----------Twitter credentials for authentication------------#
consumer_key = "IpkgiGh6OYKI7lLEIOV00aJ9h"
consumer_secret = "7FTOQRuun5WDvA90Icuu9Dfvl4ijgQaLz46ANZC8giAodAlFaj"
access_token = "2627438079-Rf6fd3PoC5xqMFbGjujIth8nVSTr2Vmt8ddK4W8"
access_token_secret = "InjiQeeGpdYhPB6D8DApchE3Ll9d71Ob1BdyrgI8uJ9YZ"

# ------------creating table to store tweet data---------------- #
conn = sqlite3.connect('StreamingDB.db')
c = conn.cursor()

def create_table():
	try:
		c.execute('''CREATE TABLE IF NOT EXISTS AmazonTweets
					(unix REAL, tweet TEXT, sentiment REAL)''')
		c.execute('''CREATE INDEX fast_unix ON AmazonTweets(unix)''')
		c.execute('''CREATE INDEX fast_tweet ON AmazonTweets(tweet)''')
		c.execute('''CREATE INDEX fast_sentiment ON AmazonTweets(sentiment)''')
		conn.commit()
	except Exception as e:
		print(str(e))

create_table()


# ------------Streaming tweets into sqlite table-----------------#
class Listener(StreamListener):

	def on_data(self, data):
		try:
			data = json.loads(data)  # json lib loads in tweet
			tweet = unidecode(data['text'])  # sanitizing tweet w unidecode
			time_ms = data['timestamp_ms']  # grabs timestamp

			analysis = TextBlob(tweet)
			sentiment = analysis.sentiment.polarity

			print(time_ms, tweet, sentiment)
			c.execute('''INSERT INTO AmazonTweets (unix, tweet, sentiment) VALUES (?, ?, ?)''', (time_ms, tweet, sentiment))
			conn.commit()

		except KeyError as e:
			print(str(e))
		return(True)


	def on_error(self, status):
		print(status)


# --------------------creating stream object--------------------#
while True:
	try:
		auth = OAuthHandler(consumer_key, consumer_secret)
		auth.set_access_token(access_token, access_token_secret)
		twitterStream = Stream(auth, Listener())
		twitterStream.filter(languages=["en"], track=keyword)
	except Exception as e:
		print(str(e))
		time.sleep(5)


