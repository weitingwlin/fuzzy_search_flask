import requests
from bs4 import BeautifulSoup
# from datetime import datetime
import numpy as np
import pandas as pd
import re
import random
import string
import dill
import h5py
from keras.models import Model,load_model

###############
c_dict = dill.load( open("app/data/morecommon_dict.pkl","rb"))
word2ind = dill.load( open("app/data/word2ind.pkl","rb"))
# vocab = list(c_dict.keys())
# # build a small word2ind dictionary
# word2ind = {}
# for i,w in enumerate(vocab):
#     word2ind[w] = i
# random.seed(3)
emoji_dict = {0:'',1:'😀',2: '🤔',3: '😥',4:'😱',5:'😒',6:'👍'}
mymodel = load_model('app/data/emoji_model.h5')
Len = 20
###############

# url = 'https://www.audible.com/pd/Classics/A-Clockwork-Orange-Audiobook/B002V1OHIW'
def show_emoji(url):
    res = get_emoji(url, mymodel, max_reviewers = 30, max_sentences=10)

    return res


#################
def one_hot(X):
    a = np.array(X)
    b = np.zeros((len(a), max(a)+1))
    b[np.arange(len(a)), a] = 1
    return b

def review_to_indices(X, word_to_index=word2ind, max_len = 10):
    m = len(X)
    X_indices = np.zeros((m, max_len))
    vocab = word_to_index.keys()
    for i in range(m):
        review_words =X[i].lower().split()
        # Initialize j to 0
        j = 0
        # Loop over the words of sentence_words
        for w in review_words[:max_len]:
            if w in vocab:
                X_indices[i, j] = word_to_index[w]
            # Increment j to j + 1
                j = j + 1
    return X_indices

def get_reviews(url, max_reviewers=1, max_sentences=1):
    '''
    url: url of main page for a book
    max_reviewers: randomly select n reviewers
    max_sentences: randomly select n sentences from each reviewer
    return sentences in review
    '''
    short_review = []
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "lxml")
    # get the review block
    parent = soup.find('div',attrs = {'class': 'bc-section listReviewsTabUS'})
    if parent is None:
        return short_review
    reviews = parent.select('p.bc-text.bc-spacing-small.bc-color-secondary')
    # randomly pick reviews
    selected_reviews = random.sample(reviews, min(max_reviewers, len(reviews)))

    for review in selected_reviews:
        sentences = [s.strip() for s in re.split('[\.\?\!]\s', review.text) if len(s)>30 ]
        selected_sentences = random.sample(sentences, min(max_sentences, len(sentences)))
        short_review =  short_review + selected_sentences
    return short_review

def get_emoji(url, model, max_reviewers = 10, max_sentences=10):
    temp = get_reviews(url, max_reviewers, max_sentences)
    temp = [s for s in temp if s != '']
    t_ind = review_to_indices(temp, word_to_index=word2ind, max_len = Len)
    res = model.predict(t_ind)
    #
    # thresh_ind = np.max(res, axis=1) > thresh
    predicted = np.argmax(res, axis=1)
    emos = []
    for i, t in enumerate(temp):
        if predicted[i] != 0 :
            emos.append([t, emoji_dict[predicted[i]] , predicted[i] ])
    return emos

def emo_hist(res):
    # take result from `get emoji`
    hist = [0,0,0,0,0,0,0]
    for emo in res:
        hist[emo[2]] += 1
    return hist

def rank_emo(res, emoji_dict=emoji_dict):
    hist = emo_hist(res)
    total = sum(hist)
    freq = [ h/total for h in hist]
    emoji_list = [i for i in emoji_dict.values()]
    em_sorted = ['']
    co_sorted = [max(freq) + 0.25]
    for em, co in sorted(zip(emoji_list[1:], freq[1:]),  key= lambda x:x[1], reverse=True):
        em_sorted.append(em)
        co_sorted.append(co)
    return em_sorted, co_sorted, total
