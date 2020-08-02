import random
import re
import string
import pickle

from nltk import classify, NaiveBayesClassifier
from nltk.corpus import twitter_samples, stopwords
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tag import pos_tag


def remove_noise(tweet_tokens, stop_words=()):
    """
    Removes abstract symbols and normalises tokenised text

    :param tweet_tokens: Tokenised text from tweet received
    :type tweet_tokens: list
    :param stop_words: Tuple from NLTK module of useless words e.g. the, is, at
    :type stop_words: tuple
    :return: Cleaned version of tokenised text
    """
    cleaned_tokens = []
    for token, tag in pos_tag(tweet_tokens):
        # Removes characters such as hashtag
        token = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|' \
                       '(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', token)
        token = re.sub('(@[A-Za-z0-9_]+)', '', token)
        # Assigns token as a noun - pos = part of speech
        if tag.startswith("NN"):
            pos = 'n'
        # Assigns token as a verb
        elif tag.startswith('VB'):
            pos = 'v'
        # Assigns token as an adjective
        else:
            pos = 'a'
        lemmatizer = WordNetLemmatizer()
        # Normalises all tokens e.g. "playing", "played" all return to "play"
        token = lemmatizer.lemmatize(token, pos)
        if len(token) > 0 and token not in string.punctuation and token.lower() not in stop_words:
            # Removes any punctuation and stopwords returning lower-case tokens
            cleaned_tokens.append(token.lower())
    return cleaned_tokens


def model_tweets(cleaned_tokens_list):
    """
    Formats tweets to be used in machine learning

    :param cleaned_tokens_list: A list of tokens already run through the remove_noise function
    :type cleaned_tokens_list: list
    :return: Dictionary of each token with True value
    """
    for tweet_tokens in cleaned_tokens_list:
        yield dict([token, True] for token in tweet_tokens)


if __name__ == '__main__':

    stop_words = stopwords.words('english')
    positive_tweet_tokens = twitter_samples.tokenized('positive_tweets.json')
    negative_tweet_tokens = twitter_samples.tokenized('negative_tweets.json')
    positive_cleaned_tokens_list = []
    negative_cleaned_tokens_list = []

    # Cleans all tweets in positive_tweet_tokens and negative_tweet_tokens
    for tokens in positive_tweet_tokens:
        positive_cleaned_tokens_list.append(remove_noise(tokens, stop_words))

    for tokens in negative_tweet_tokens:
        negative_cleaned_tokens_list.append(remove_noise(tokens, stop_words))

    positive_tokens_for_model = model_tweets(positive_cleaned_tokens_list)
    negative_tokens_for_model = model_tweets(negative_cleaned_tokens_list)
    # Labels all tweets as either positive or negative for supervised machine learning
    positive_dataset = [(tweet_dict, "Positive") for tweet_dict in positive_tokens_for_model]
    negative_dataset = [(tweet_dict, "Negative") for tweet_dict in negative_tokens_for_model]

    # Combines datasets and performs randomised train test split
    dataset = positive_dataset + negative_dataset
    random.shuffle(dataset)
    train_data = dataset[:7000]
    test_data = dataset[7000:]

    # Uses Naive-Bayes classification technique to train model
    classifier = NaiveBayesClassifier.train(train_data)

    print("Accuracy is:", classify.accuracy(classifier, test_data))

    # Dumps model for use in tsla_investor.py
    pickle.dump(classifier, open('classifier.pkl', 'wb'))
