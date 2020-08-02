"""
A Tesla investment bot functioning based on tweets from Elon Musk.

Author: Matthew MacDonald
"""
import tweepy
import time

from config import *
from tsla_investor import investor, close_out


class MyStreamListener(tweepy.StreamListener):
    """Overrides methods in StreamListener"""
    def on_status(self, tweet):
        """
        Provides guidelines for what to do when tweet received

        :param tweet: Information from StreamListener
        :return: True
        """
        if from_creator(tweet):
            try:
                time.sleep(0.2)
                print(f'Elon tweeted: {tweet.text}')
                investor(tweet)
                return True
            except BaseException as err:
                # Informs user of what has caused error to be raised
                print(f'Error on data {str(err)}')
            return True
        return True

    def on_error(self, status_code):
        """
        What to do when listed number to connect to API exceeded

        :param status_code: Error number
        :type status_code: int
        :return: False
        """
        if status_code == 420:
            print('Error 420')
            return False


def from_creator(tweet):
    """
    Prevents retweets and replies from appearing in stream

    :param tweet: The information from StreamListener
    :returns: False if tweet is a retweet, True otherwise
    """
    if hasattr(tweet, 'retweeted_status'):
        return False
    elif tweet.in_reply_to_status_id is not None:
        return False
    elif tweet.in_reply_to_screen_name is not None:
        return False
    elif tweet.in_reply_to_user_id is not None:
        return False
    else:
        return True


# Only runs code if main file
if __name__ == '__main__':
    try:
        # Authenticate to Twitter
        auth = tweepy.OAuthHandler(api_key, secret_key)
        auth.set_access_token(access_token, secret_token)
        tw_api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

        tweets_listener = MyStreamListener(tw_api)
        stream = tweepy.Stream(tw_api.auth, tweets_listener)
        # Filters tweets to only receive Elon's - use http://gettwitterid.com/ for user ID
        stream.filter(follow=['44196397', '1004809825027547137'], languages=['en'])
    except KeyboardInterrupt as e:
        # if user stops stream close out all positions
        print('\nProgram stopped by user...')
        close_out()
