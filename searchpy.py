import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import plotly.plotly
import tweepy
import numpy
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from tweepy import Stream
from tweepy.streaming import StreamListener
from dash.dependencies import Input, Output


# from wordcloud import WordCloud
CONSUMER_KEY = "u2w4FopTMw3xYSwjUSzSvhfe1"
CONSUMER_SECRET = "wtFwfU9qIviOSjey8KY4gLWl37x6uyUJTdU3aKvGimi42jVJQt"
ACCESS_TOKEN = "928463445481148416-0C1el66F4bTa8OJK2NO6QokHFUzkArJ"
ACCESS_TOKEN_SECRET = "xaiZya5B5MesEL2zuecHUmCY2D1rHhMA0qSG2dN7XpC4U"


auth = auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

api = tweepy.API(auth)
analyzer = SentimentIntensityAnalyzer()

query = 'tester'
max_tweets = 100
public_tweets = [status for status in tweepy.Cursor(
    api.search, q=query, lang="en").items(max_tweets)]

data = [[obj.user.screen_name, obj.user.name, obj.user.id_str, obj.user.description, obj.created_at.year, obj.created_at.month, obj.created_at.day,
         "%s.%s" % (obj.created_at.hour, obj.created_at.minute), obj.id_str, obj.text, analyzer.polarity_scores(obj.text)["compound"]] for obj in public_tweets]
df = pd.DataFrame(data, columns=['screen_name', 'name', 'twitter_id', 'description',
                                 'year', 'month', 'date', 'time', 'tweet_id', 'tweet', 'compound_score'])

# Create a list of positive tweets
df_pos = df[["tweet", "compound_score"]].sort_values(by="compound_score")
# Create a list of negative tweets
df_neg = df[["tweet", "compound_score"]].sort_values(
    by="compound_score", ascending=False)
df_summary_stats = df.describe(include=[numpy.number])

positive = 0
neutral = 0
negative = 0
compound_scores = []

for tweet in public_tweets:

    compound = analyzer.polarity_scores(tweet.text)["compound"]
    compound_scores.append(compound)
    if(compound >= .05):
        positive += 1
    elif((compound > -0.05) and (compound < 0.05)):
        neutral += 1
    else:
        negative += 1
compound_average = round(numpy.mean(compound_scores), 5)



# Dash Stuff!
app = dash.Dash()


def generate_table(dataframe, max_rows=5):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )


app.css.append_css(
    {"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})

app.layout = html.Div(children=[
    dcc.Input(id='my-id', value='Software', type='text'),
    html.Div(id='my-div'),
    
	html.H2(children='Twitter Sentiment for {{my-id.value}}'),
    html.H4(children='Sentiment on Negative Tweets'),
    generate_table(df_pos.head()),
    html.H4(children='Sentiment on Positive Tweets'),
    generate_table(df_neg.head()),
    html.H4(children='Summary Statistics'),
    generate_table(df_summary_stats),
    html.Div(children='''
        Parsing 1,000 tweets and conducting sentiment analysis with VADER.
    '''),
	
])

	
@app.callback(
    Output(component_id='my-div', component_property='children'),
    [Input(component_id='my-id', component_property='value')]
)	
	
	
##updating based on data argument from the tweepy-vader data in line 33	
##added in set and reset indexes

def update_value(df):

    return dcc.Graph(
        id="test",
        figure=go.Figure(
            # id="test",
            data=[
                go.Pie(
                    labels=["positive", "negative", "neutral"],
                    values=[positive, negative, neutral]
                )
            ]
        )
    )




if __name__ == '__main__':
    app.run_server(debug=True)
