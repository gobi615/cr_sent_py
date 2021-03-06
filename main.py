import os
import telebot
import time
import requests 
from flask import Flask, request
import json
global dict


API_KEY = os.environ['API_KEY']
bot = telebot.TeleBot(API_KEY)
TOKEN = API_KEY
WORDS = os.environ['KEYWORDS']
keywords = []
for sentence in WORDS.split(','):
  keywords.append(sentence.strip())

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
url = os.environ.get("URL")
tmln = os.environ.get("T")
maxresult = os.environ.get("MAX_RESULT")
interval = os.environ.get("QUERY_INTERVAL")
tmlns = []

def create_url():
  ids = tmln.split(',')
  for id in ids:
    tmlns.append(url+"{}/tweets".format(id))
  return tmlns

def get_params():
    # Tweet fields are adjustable.
    # Options include:
    # attachments, author_id, context_annotations,
    # conversation_id, created_at, entities, geo, id,
    # in_reply_to_user_id, lang, non_public_metrics, organic_metrics,
    # possibly_sensitive, promoted_metrics, public_metrics, referenced_tweets,
    # source, text, and withheld
    return {'max_results':str(maxresult)}

def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2RecentSearchPython"
    return r

def connect_to_endpoint(url, params):
    response = requests.request("GET", url, auth=bearer_oauth, params=params)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()

dict = []

urls = create_url()  
params = get_params()
def tweet_check():
    # print(urls)
    for url in urls:      
      json_response = connect_to_endpoint(url, params)
      # print(json.dumps(json_response, indent=4, sort_keys=True))
      # print(json_response['data'][0]['text'])
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
      print('going to sleep')
      time.sleep(int(interval)) #make function to sleep for 10 seconds
      #print(json_response['data'][0]['text'])

def start():
  while True:
      print('tweet checking')
      tweet_check()

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