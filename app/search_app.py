
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
    titles, ind = fuzzy_find2(S, cat_books, maxshow=n )
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

    mystr_less = [word for word in mystr if word.lower() not in stop_words]

    if len(mystr_less) > 0 :
        mystr = mystr_less

    # remove placeholder
    mystr_less = [s for s in mystr if s in vocab]
    if len(mystr_less) > 1 :
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


def compare_mats(M1, M2 , ph = 2, stress = 0.5, penalty = 1):
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
        dist = dist +  ((L1 - L2)/(L1 + L2) * penalty/1)
    return dist

def compare_strs(S1, S2, limit = 5, placeholder = None):
    _, M1 = str2mat(S1, limit = limit)
    _, M2 = str2mat(S2, limit = limit)
    return compare_mats(M1, M2 , ph = placeholder)

def fuzzy_find2(mytitle, shelf, maxshow=10, threshhold = 5):
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


def suggestion_map(mytitle, shelf, n_init =10, maxshow=25):
    # 1. get a list of suggested books
    thresh = 10
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
    p = figure(plot_width=500, plot_height=500,
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
    glyph = Text(x="x", y="y", text="names", angle=0.5, text_color="#1a3c72", text_font_size="1.5em")
    p.add_glyph(source, glyph)
    url = "@urls"
    taptool = p.select(type=TapTool)
    taptool.callback = OpenURL(url=url)
    return p

mydemo = ['orange', 'tangerine','lemon',\
          'butterfly', 'dragonfly','bee', \
           'genius', 'Einstein', 'brilliant']
Y = manifold.MDS(n_components= 2,n_init = 100,random_state=2,dissimilarity='precomputed', metric=False)\
    .fit_transform(string_distance(mydemo))

def plot_demo():
    p = figure(plot_width=600, plot_height=600,
           tools=[ 'box_zoom', 'reset', 'pan'], title="",
          x_range=(-0.6, 0.6), y_range=(-0.6, 0.6))
    source = ColumnDataSource(data=dict(
                            x=Y[:,0],
                            y=Y[:,1],
                            color=['orange','orange','orange','green','green','green','blue','blue','blue'],
                             names = mydemo))
    p.circle('x', 'y', color='color', size=20, source=source ,fill_alpha=0.4,line_color=None)
    p.xaxis[0].axis_label = 'Dimension 1'
    p.yaxis[0].axis_label = 'Dimension 2'
    glyph = Text(x="x", y="y", text="names", angle=0.5, text_color="#1a3c72", text_font_size="1.5em")
    p.add_glyph(source, glyph)
    return p

def plot_emoji_hist(em_sorted, co_sorted, total):
    source = ColumnDataSource(data=dict(
                emoji=em_sorted,
                counts=co_sorted,
                color = ['#ffffff', '#5254a3', '#5254a3', '#5254a3', '#5254a3', '#5254a3', '#5254a3'],
            #    legend = ["Baseline (no emoji)", "Frequency", "Frequency", "Frequency", "Frequency", "Frequency"],
            #    desc = ["Baseline (no emoji)", "Frequency", "Frequency", "Frequency", "Frequency", "Frequency"]
    ))

    p = figure(x_range=em_sorted, plot_height=350, title="Summarized from " + str(total) + " review sentences",
               toolbar_location=None, tools="hover")

    p.vbar(x='emoji', top='counts', width=0.9, color='color', source=source,)
    # p.xaxis.axis_label_text_font_size = "100pt"
    labels = LabelSet(x='emoji', y='counts', text='emoji', level='glyph',text_font_size="32pt",
                  x_offset=-5, y_offset=5, source=source, render_mode='canvas')
    p.add_layout(labels)
    # glyph = Text(x='emoji', y='counts', text="emoji", angle=0, text_color="#1a3c72", text_font_size="20pt")
    # p.add_glyph(source, glyph)
    p.axis.visible = False
    p.ygrid.visible = False
    p.xgrid.grid_line_color = None
    p.legend.orientation = "vertical"
    p.xaxis.major_label_text_font_size = '0pt'
    return(p)
