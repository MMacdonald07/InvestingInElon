import _thread
import ctypes
import os
import pickle
import time
import alpaca_trade_api as trade_api

from nltk.tokenize import word_tokenize
from sentiment_model import remove_noise
from config import user_key, user_secret_key, base_url


def handler(sig):
    """
    Prevents program crashing at CTRL+C event by raising KeyboardInterrupt
    """
    _thread.interrupt_main()
    return 1


basepath = r'C:\Users\mdmac\anaconda3\Library\bin'
ctypes.CDLL(os.path.join(basepath, 'libmmd.dll'))
ctypes.CDLL(os.path.join(basepath, 'libifcoremd.dll'))
routine = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_uint)(handler)
ctypes.windll.kernel32.SetConsoleCtrlHandler(routine, 1)

# Connects to Alpaca
al_api = trade_api.REST(user_key, user_secret_key, base_url, api_version='v2')


def report_positions(position):
    """
    Neatly prints position data to user

    :param position: Investment approach to take with stock i.e. long, short or none
    :type position: str
    :returns: None
    """
    output = '\n' + 50 * '=' + '\n'
    output += f'Going {position} on TSLA.\n' + '\n'
    time.sleep(2)
    output += str(al_api.list_positions()) + '\n'
    output += 50 * '=' + '\n'
    print(output)


def investor(tweet):
    """
    Uses tweet tone to deduce investment position to take

    :param tweet: The information from StreamListener
    :returns: None
    """
    #  Loads classifier from sentiment_model.py
    classifier = pickle.load(open('classifier.pkl', 'rb'))
    custom_tokens = remove_noise(word_tokenize(tweet.text))
    # Classifies tweet as positive/negative tone
    tone = classifier.classify(dict([token, True] for token in custom_tokens))
    if tone == 'Negative':
        # If negative tone, short stock
        al_api.submit_order('TSLA', 30, 'sell', 'market', 'gtc')
        report_positions('SHORT')
    elif tone == 'Positive':
        # If positive tone, go long on stock
        al_api.submit_order('TSLA', 30, 'buy', 'market', 'gtc')
        report_positions('LONG')
    else:
        # If no signal returned, make no investment
        report_positions('NOWHERE')


def close_out():
    """
    Closes out all current positions on stock at market price

    :returns: None
    """
    report_positions('CLOSE OUT')
    al_api.close_all_positions()
