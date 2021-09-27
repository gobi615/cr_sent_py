import os
import telebot
import time
import re
import emoji
import contractions
import requests 
from flask import Flask, request

global dict


API_KEY = os.environ['API_KEY']
bot = telebot.TeleBot(API_KEY)
TOKEN = API_KEY

server = Flask(__name__)

# @bot.message_handler(commands=['Greet'])
# def greet(m):  
#   bot.reply_to(m, 'Hey, its Gobi')

@bot.message_handler(commands=['start'])
def hello(m):
  global last_msg
  last_msg = m
  start()

bearer_token = os.environ.get("BEARER_TOKEN")
search_url = os.environ.get("SEARCH_URL")
query_params = {'query': 'CRYPTO','tweet.fields': 'author_id,created_at', 'max_results':'100'}
keywords = ['crypto ban', 'crypto market crash', 'market down', 'bear market', 'stock market crash', 'legal tender', 'china crypto ban', 'crypto exchange ban', 'bearish','baby floki coin', 'going down', 'restricted', 'crash']

def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2RecentSearchPython"
    return r

def connect_to_endpoint(url, params):
    response = requests.get(url, auth=bearer_oauth, params=params)
    # print(response.status_code)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()

def replace_retweet(tweet, default_replace=""):
    #\s - white space character
    tweet = re.sub('RT\s+', default_replace, tweet)
    return tweet

def replace_user(tweet, default_replace="twitteruser"):
    #\w means all the character in a word. in \w add + to complete the word.
    tweet = re.sub('\B@\w+', default_replace, tweet)
    return tweet

def demojize(tweet):
    tweet = emoji.demojize(tweet)
    return tweet

def replace_url(tweet, default_replace=""):
    tweet = re.sub('(http|https):\/\/\S+', default_replace, tweet)
    return tweet

def replace_hashtag(tweet, default_replace=""):
    tweet = re.sub('#+', default_replace, tweet)
    return tweet

def to_lowercase(tweet):
  tweet = tweet.lower()
  return tweet

def word_repetition(tweet):
  tweet = re.sub(r'(.)\1+', r'\1\1', tweet)
  return tweet

def punct_repetition(tweet, default_replace=""):
  tweet = re.sub(r'[\?\.\!]+(?=[\?\.\!])', default_replace, tweet)
  return tweet

def fix_contractions(tweet):
  tweet = contractions.fix(tweet)
  return tweet

def process_tweet(tweet, verbose=False):
  if verbose: print("Initial tweet: {}".format(tweet))

  ## Twitter Features
  tweet = replace_retweet(tweet) # replace retweet
  tweet = replace_user(tweet, "") # replace user tag
  tweet = replace_url(tweet) # replace url
  tweet = replace_hashtag(tweet) # replace hashtag
  if verbose: print("Post Twitter processing tweet: {}".format(tweet))

  ## Word Features
  tweet = to_lowercase(tweet) # lower case
  tweet = fix_contractions(tweet) # replace contractions
  tweet = punct_repetition(tweet) # replace punctuation repetition
  tweet = word_repetition(tweet) # replace word repetition
  tweet = demojize(tweet) # replace emojis
  if verbose: print("Post Word processing tweet: {}".format(tweet))

  return tweet

dict = []

def tweet_check():
    json_response = connect_to_endpoint(search_url, query_params)
    #print(json_response['data'][0]['text'])
    # print(json.dumps(json_response, indent=4, sort_keys=True))
    # print("Number of tweets: {}".format(len(json_response['data'])))
    for tweet in json_response['data']:
      # tweet['text'] = process_tweet(tweet['text']).lower()
      for key in keywords:    
        if( key in tweet['text']):
          #print('match')
          if(tweet['id'] not in dict):
            bot.send_message(last_msg.chat.id,tweet['text'])
            dict.append(tweet['id'])
    #print(json_response['data'][0]['text'])

def start():
  while True:
      print('tweet checking')
      tweet_check()
      print('going to sleep')
      time.sleep(10) #make function to sleep for 10 seconds

@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://crypt-sent-py.herokuapp.com/' + TOKEN)
    return "!", 200


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))