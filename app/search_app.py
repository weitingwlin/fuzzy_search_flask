
import numpy as np
import pandas as pd
import string
import re
import dill
from itertools import product, combinations
# from nltk.corpus import stopwords
from scipy.stats import rankdata
from sklearn import manifold
from numpy.random import random
import random
from bokeh.plotting import figure,  show, output_file
from bokeh.models import ColumnDataSource, Range1d, LabelSet, Label
from bokeh.models.tools import TapTool
from bokeh.models.callbacks import OpenURL
from bokeh.models.glyphs import Text
import dill

c_dict = dill.load( open("app/data/morecommon_dict.pkl","rb"))
vocab = c_dict.keys()
books = pd.read_csv('app/data/fiction_1000.csv')
stop_words = dill.load( open("app/data/stop_words.pkl","rb"))
cat_books = books[books['category'].isin(['fiction'])]


def search_app(S, categories = ['fiction'], n = 5):
#     print(cat_books)
    titles, ind = fuzzy_find2(S, cat_books, maxshow=n)
    links = cat_books['link'][ind]
    zipped = [[t,l] for t, l in zip(titles, links)]
    # return titles
    return zipped



##### functions below
def trim_string(S):
    '''
    trim useless words if string is too long
    '''
    mystr1 = re.split('[\W\s]+', S)
    # split at punctuation or space

    mystr =[s.lower() for s in mystr1]
    # Remove "the", "a", "an"
    # nonsense = ["the", "a", "an", "and", "to","on", "from", "in", "by"]
    # mystr = [word for word in mystr if word.lower() not in nonsense]

    # remove more
    mystr_less = [word for word in mystr if word.lower() not in stop_words]

    if len(mystr_less) > 0 :
        mystr = mystr_less

    # remove placeholder
    mystr_less = [s for s in mystr if s in vocab]
    if len(mystr_less) > 0 :
        mystr = mystr_less

    return mystr


def str2mat(instr, limit = 5, placeholder = None):
    '''
    Convert string to a vector base on average vector of the composing words.
    instr: the inpput string
    placeholder: for the non-vocabularies
    '''
    # make a place-holder: mean of three strange words
    mystr = trim_string(instr)
    # number of words
    L = min(len(mystr), limit)

    ## padding up
    sheet = np.ones((300, limit))* 2
    for l in range(L):
        if (mystr[l] in vocab):
            sheet[:,l] = c_dict[mystr[l]]
        else:
            ph = np.ones(300)* 1
            ph[random.sample(list(np.arange(300)), 20)] = -3
            sheet[:,l] = ph

    return L, sheet


def compare_mats(M1, M2 , ph = 2, stress = 0.2, penalty = 0.5):
    n, limit = M1.shape
    L1 = sum(M1[0,:] != 2 ) # lenth of
    L2 = sum(M2[0,:] != 2 )
    # trim
    M1_trim = M1[:, 0:L1]
    M2_trim = M2[:, 0:L2]

    if L1 == 1:
        lin_dist = M2_trim - M1_trim
        euc_dist = [np.sqrt(sum(lin_dist[:,i]  ** 2)) for i in range(L2)]
        dist = min(euc_dist)
    elif L2 == 1:
        lin_dist = np.tile(M2_trim, L1) - M1_trim
        euc_dist = [np.sqrt(sum(lin_dist[:,i]  ** 2)) for i in range(L1)]
        # use mean if target is more than 1 words
        dist = np.mean(euc_dist)
    else:
        #
        ind_product = list(product(np.arange(L2), repeat=L1)) # select from M2 to match the size of M1
        ind_combination = list(combinations(np.arange(L2), L1))
        eucs = []
        for p, ind in enumerate(ind_product): # 2, (0,1):
            M2_p = M2_trim[:,list(ind)] # permuted M2'
            lin_dist = M2_p - M1_trim
            euc = [np.sqrt(sum(lin_dist[:,i]  ** 2)) for i in range(L1)]
            mean_euc = np.mean(euc)
            if ind not in ind_combination:
                mean_euc = mean_euc * (stress + 1)
            eucs.append(mean_euc)
        dist = min(eucs)
    # penalty for unequal list
    if L2 > L1:
        dist = dist +  ((L2 - L1)/(L1 + L2) * penalty)
    if L2 < L1:
        dist = dist +  ((L1 - L2)/(L1 + L2) * penalty/2)
    return dist

def compare_strs(S1, S2, limit = 5, placeholder = None):
    _, M1 = str2mat(S1, limit = limit)
    _, M2 = str2mat(S2, limit = limit)
    return compare_mats(M1, M2 , ph = placeholder)

def fuzzy_find2(mytitle, shelf, maxshow = 10, threshhold = 5):
    '''
    mytitle: the user input keyword for fuzzy search
    shelf: df with column named 'title', find book from
    maxshow: the max. number of result return.
    threshhold: threshhold of similarity for the "match"
    '''
    dist = []
    for s in shelf["title"]:
        dist.append(compare_strs(mytitle, s))
    dist = np.array(dist)

    fuzzy = np.where(dist < threshhold)[0]
    L = len(fuzzy)
    if L > maxshow:
        rankF = rankdata(dist, method='min')
        fuzzy = np.where(rankF <= maxshow)[0]

    return list(shelf["title"][fuzzy]), fuzzy

def string_distance(Slist, limit = 5, placeholder = None):

    N = len(Slist)
    dist = np.zeros((N,N))
    for i in range(N):
        for j in range(i,N):
            dist[i,j] = compare_strs(Slist[i], Slist[j], limit=limit, placeholder=placeholder)
            dist[j,i] = dist[i,j]
    return dist


def suggestion_map(mytitle, shelf, n_init =10, maxshow=15):
    # 1. get a list of suggested books
    thresh = 5
    S_list, S_indices = fuzzy_find2(mytitle, shelf, maxshow = maxshow, threshhold = thresh)
    # 2. calculate distance matrix
    Dist = string_distance(S_list + [mytitle], limit = 5, placeholder = None)
    # 3. calculate Y
    Y = manifold.MDS(n_components= 2, n_init =  n_init, dissimilarity='precomputed')\
                     .fit_transform(Dist)
    # 4. get notation
    notation = S_list + [mytitle]
    similarity = thresh - Dist[-1,:]
    return Y, notation, similarity

# def plot_2D(Yin = None, notation = None, sizes = 1):
#     # p = figure(tools='save')
#     # p.scatter(Y[:,0], Y[:,1], fill_alpha=0.6)#,
#     xmock = max(Yin[:,0]) + 2
#     ymock = max(Yin[:,1]) + 0.5
#     Y = np.concatenate((np.array([xmock, ymock]).reshape(1,2),  Yin), axis=0)
#     #
#     sizes =  np.concatenate((np.array([0]),  sizes), axis=0)
#     notation =  np.concatenate((np.array([""]),  notation), axis=0)
#
#
#     color = ["#1f1b99" for i in sizes]
#     color[-1] = "#f442c5"
#     source = ColumnDataSource(data=dict(Dim1 = Y[:,0], Dim2 = Y[:,1],
#                                         names = notation, sizes = sizes * 0.1,\
#                                         colors = color))
#     p = figure(title='2-D representation of the distances between titles')
#     p.scatter(x='Dim1', y='Dim2', source=source, radius='sizes',
#               fill_color='colors', fill_alpha=0.6,
#               line_color=None)
#     p.xaxis[0].axis_label = 'Dimension 1'
#     p.yaxis[0].axis_label = 'Dimension 2'
#     labels = LabelSet(x='Dim1', y='Dim2', text='names', level='glyph',
#               x_offset=0, y_offset=0.05, source=source, render_mode='canvas')
#     p.add_layout(labels)
#
#     return p

# def suggestion_plot(mytitle):
#     Y, notation, sizes = suggestion_map(mytitle, books)
#     return plot_2D(Y, notation, sizes)

def plot_tab(mytitle, Yin = None, notation = None, sizes = 1):
    threshhold = 5
    titles, ind = fuzzy_find2(mytitle, shelf = cat_books, maxshow = 8, threshhold = 5)
    links = cat_books['link'][ind]


    Dist = string_distance(titles + [mytitle], limit = 5, placeholder = None)
    # 3. calculate Y
    Y = manifold.MDS(n_components= 2, n_init =  10, dissimilarity='precomputed')\
                     .fit_transform(Dist)
    # 4. get notation
    notation = titles + [mytitle]
    similarity = threshhold - Dist[-1,:]
    # plot
    p = figure(plot_width=600, plot_height=600,
               tools=["tap", 'box_zoom', 'reset', 'pan'], title="Book titles similar to \" " + mytitle +"\"",
               )
    source = ColumnDataSource(data=dict(
                            x=Y[:,0], y=Y[:,1],
                            color = ['blue'] * len(titles) + ['red'],
                            urls = list(links) + ['/'],
                            names = notation

    ))
    p.circle('x', 'y', color='color', size=20, source=source ,fill_alpha=0.4,line_color=None)
    p.xaxis[0].axis_label = 'Dimension 1'
    p.yaxis[0].axis_label = 'Dimension 2'
    glyph = Text(x="x", y="y", text="names", angle=0.5, text_color="#1a3c72")
    p.add_glyph(source, glyph)
    url = "@urls"
    taptool = p.select(type=TapTool)
    taptool.callback = OpenURL(url=url)
    return p
