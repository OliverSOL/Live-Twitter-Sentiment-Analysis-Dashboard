
# import packages
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

import os
import re
import plotly
import plotly.graph_objs as go
import pandas as pd

from classifer import Classify
from api import fetchTweets
from collections import Counter
import nltk

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords


stops = stopwords.words('english')
stops.append('https')
# app color
app_color = {
    "graph_bg": "rgb(221, 236, 255)",
    "graph_line": "rgb(8, 70, 151)",
    "graph_font":"rgb(2, 29, 65)"}


#--------------Configuring Dash App---------------------------------#
app = dash.Dash(__name__)

#------------------------Layout------------------------------#
app.layout = html.Div(
	#className='container',
	children=[
			# header

			html.Div(
				className="app__header row",
				children=[
					html.A(
			                className="div-logo",
			                children=[
			                	html.Img(
			                    	className="logo", src=app.get_asset_url("dash-logo-new.png")
			                	)
			                ]
			            ),
				#title
					html.Div(
						className='study-browser-banner',
						children=[
						html.H2('Analyzing Amazon'),
						html.P('''Taking a deeper look into what Twitter users are saying about Amazon in real time.''')
						]	
					)
            	]
        	),
            html.Div(
            	className='container',
            	children=[
            		html.Div(
            			
            			children=[

				            # Left side
				            html.Div(
				            	className='seven columns ',
				            	children=[
								#-------------graph-----------------#
									html.Div([
										dcc.Graph(
											id='live-graph',
											animate=False,
											
										),
										dcc.Interval(
											id='graph-update',
											interval=1*10000,  # in milliseconds
											n_intervals=0,
											)
										]
									),
								# ----------------Live Twitter Feed----------------#
									html.Div([
										html.H6('Live Twitter Feed'),
										html.Div(id='update_text'),
										dcc.Interval(
											id='feed-update',
											interval=1*10000,
											n_intervals=0,
											)
										]
									),
								]
							),
							#-----------------------Right side: bar plot and pie chart-------------------#
							html.Div(
								className='five columns',
								children=[
								# -------------------------pie chart----------------------#
									html.Div([
										#html.H6('Sentiment by the Percentages'),
										dcc.Interval(
											id='pie_update',
											interval=1*10000,
											n_intervals=0),
										dcc.Graph(id='pie_chart'
											),
										]
									),
									# ------------------------word count bar chart---------------#
									html.Div([
										dcc.Interval(
											id='bar-update',
											interval=1*10000,
											n_intervals=0,
											),
										dcc.Graph(
											id='word_count',
											animate=False,
											),
										]
									),
								]
							),
						],
					)
        			],		
			)
		]	
	)

@app.callback(Output('live-graph', 'figure'),
	[Input('graph-update', 'n_intervals')])

# ---------------------update graph--------------------------------#
def update_graph_sentiment(n):
	try:
		query = "SELECT * FROM AmazonTweets ORDER BY unix DESC LIMIT 1000"
		df = fetchTweets(query)

		df.sort_values('unix', inplace=True)
		df['date'] = pd.to_datetime(df['unix'], unit='ms')
		df.set_index('date', inplace=True)
		df['smoothed_sentiment'] = df['sentiment'].rolling(int(len(df)/5)).mean()
		df.dropna(inplace=True)
		df = df.resample('100s').mean()

		X = df.index[-100:]
		Y = df.smoothed_sentiment.values[-100:]

		data = go.Scatter(
				x=list(X),
				y=list(Y),
				name='Scatter',
				mode='lines+markers',
				opacity=0.5,
				marker=dict(color='rgb(57,106,177,0.5)')
				)
		layout = go.Layout(
			xaxis=dict(title_text='Date', range=[min(X), max(X)]),
			yaxis=dict(title_text='Polarity', range=[min(Y),max(Y)]),
			title='Polarity of Tweets'.format(n),
			plot_bgcolor=app_color["graph_bg"],
			paper_bgcolor=app_color["graph_bg"])

		return {'data': [data], 'layout': layout}

	except Exception as e:
		with open('errors.txt', 'a') as f:
			f.write(str(e))
			f.write('\n')

#-----------------------------pie chart----------------------------#
@app.callback(Output('pie_chart', 'figure'),
				[Input('pie_update', 'n_intervals')])


def update_pie(interval):
	try:
		# fetch dictionary with num of pos, neg, and neutral tweets
		vals = Classify()
		# establish data needed for pie chart
		labels = ['Positive', 'Negative', 'Neutral']
		vals_sent = [vals['Pos'], vals['Ng'], vals['Nu']]

		data = go.Pie(labels=labels, values=vals_sent, hole=.3, pull=[0,0,0])
		layout = go.Layout(
						title='Sentiment by the Percentages'.format(),
						autosize=True,
						margin=go.layout.Margin(
							l=75,
							r=30,
							b=70,
							t=40,
							pad=4),
						plot_bgcolor=app_color["graph_bg"],
						paper_bgcolor=app_color["graph_bg"])

		return go.Figure(data=[data], layout=layout)
			
	except Exception as e:
		with open('errors.txt', 'a') as f:
			f.write(str(e))
			f.write('\n')

#--------------------------barchart word count------------------#
def bag_of_words(series):
	document = ' '.join([row for row in series])

	# lowercasing, tokenization, and keep only alphabetical tokens
	tokens = [word for word in word_tokenize(document.lower()) if word.isalpha()]

	# filtering out tokens that are not all alphabetical
	tokens = [word for word in re.findall(r'[A-Za-z]+', ' '.join(tokens))]

	# remove all stopwords
	no_stop = [word for word in tokens if word not in stops]

	return Counter(no_stop)

@app.callback(Output('word_count', 'figure'),
			[Input('bar-update', 'n_intervals')])


def update_graph_bar(interval):
	try:
		query = "SELECT * FROM AmazonTweets"
		df = fetchTweets(query)
		# get the counter for all the tokens
		word_counter = bag_of_words(df.tweet)

		# get the most common n tokens
		# n is specified by the slider
		top_n = word_counter.most_common(10)[::-1]

		# get the x and y values
		X = [cnt for word, cnt in top_n]
		Y = [word for word, cnt in top_n]

		 # plot the bar chart
		bar_chart = go.Bar(
			x=X, y=Y,
			name='Word Counts',
			orientation='h',
			)

		layout = go.Layout(
			title='Word Count',
			height=250,
			width=400,
			autosize=True,
			plot_bgcolor=app_color["graph_bg"],
			paper_bgcolor=app_color['graph_bg'],
			margin=go.layout.Margin(
				l=75, 
				r=25, 
				b=30, 
				t=30, 
				pad=4),
			xaxis=dict(title_text='Frequency'))

		return go.Figure(data=bar_chart, layout=layout)

	except Exception as e:
			with open('errors.txt', 'a') as f:
				f.write(str(e))
				f.write('\n')


#----------------update twitter feed-------------------------#
@app.callback(Output('update_text', 'children'),
			 [Input('feed-update', 'n_intervals')])

def update_tweet(tweets):
	try:
		tweetquery = "SELECT * FROM AmazonTweets WHERE tweet NOT LIKE 'RT %' ORDER BY unix DESC"
		tweetdf = fetchTweets(tweetquery)

		return html.Div([
			html.P(tweetdf['tweet'][0]),
			html.P(tweetdf['tweet'][1]),
			html.P(tweetdf['tweet'][2])
	        ])
	
	except Exception as e:
		with open('errors.txt', 'a') as f:
			f.write(str(e))
			f.write('\n')

# run the app
if __name__ == '__main__':
	app.run_server(debug=True)
