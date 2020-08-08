# classifies tweets based on sentiment val
from api import fetchTweets


def Classify():
	# establish query
	query = "SELECT * FROM AmazonTweets"
	df = fetchTweets(query)
	# initiate empty dictionary used to store occurances of pos, neg, neutral tweets
	dct = {}
	Pos = 0
	Neg = 0
	Neu = 0
	for num in df.sentiment:
		if num > 0:
			Pos += 1
		elif num == 0:
			Neu += 1
		else:
			Neg += 1
	dct['Pos'] = Pos
	dct['Ng'] = Neg
	dct['Nu'] = Neu
	return dct

