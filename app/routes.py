from app import app
from flask import render_template, flash, redirect, request, session
from app.forms import AppForm, emojiForm#, N_result
from app.search_app import search_app, plot_tab, plot_demo, plot_emoji_hist
from app.emoji_app import show_emoji, rank_emo
from bokeh.embed import components
from bokeh.resources import CDN
from bokeh.plotting import figure
from bokeh.models.glyphs import Text





@app.route('/')
@app.route('/index')
def index():
    p = plot_demo()
    script, div = components(p)
    return render_template('index.html', script=script, div=div)

@app.route('/app', methods=['GET', 'POST'])
def my_app(link = '', title = ''):
    form = AppForm()
    Sup = " "
    session['n_out'] = 5
    zipped = ['','/index']
    script,div = [],[]
    script2,div2 = [],[]
    res = []
    query_val = request.args.get('link',link)
    title = request.args.get('title','')
    # if query_val:
    #     res = show_emoji(query_val)
    #     emo, cnt, total = rank_emo(res)
    #     p2 = plot_emoji_hist(emo, cnt, total)
    #     script2, div2 = components(p2)
    if 1:
        print('validate')
        zipped = search_app(form.searchstring.data, n= 5)
        p = plot_tab(form.searchstring.data)
        script, div = components(p)

    # print(zipped)
    return render_template('app.html', form = form, strout = zipped, \
                           N_out = session['n_out'], mytitle=form.searchstring.data,
                        script=script, div=div, script2=script2, div2=div2)

@app.route('/emoji/', methods=['GET', 'POST'])
# @app.route('/emoji/<link>', methods=['GET', 'POST'])
def my_emoji(link = '', title = ''):
    form = emojiForm()
    res = []
    script,div = [],[]
    query_val = request.args.get('link',link)
    title = request.args.get('title','')
    if query_val:
        res = show_emoji(query_val)
    if form.validate_on_submit():
        res = show_emoji(form.audible_url.data)
    if res:
        emo, cnt, total = rank_emo(res)
        p = plot_emoji_hist(emo, cnt, total)
        script, div = components(p)
    return render_template('emoji.html',res=res, form = form, title=title, script=script, div=div)

@app.route('/about_me')
def about_me():
    return render_template('about_me.html')

@app.route('/how_it_works')
def how_it_works():
    return render_template('how_it_works2.html')
