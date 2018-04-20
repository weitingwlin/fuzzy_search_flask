from app import app
from flask import render_template, flash, redirect, request, session
from app.forms import AppForm, emojiForm#, N_result
from app.search_app import search_app, plot_tab, plot_demo
from app.emoji_app import show_emoji
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
def my_app():
    form = AppForm()
    Sup = " "
    session['n_out'] = 5
    zipped = ['','/index']
    script,div = [],[]
    if 1:
        print('validate')
        zipped = search_app(form.searchstring.data, n= 8)
        p = plot_tab(form.searchstring.data)

        script, div = components(p)
    # print(zipped)
    return render_template('app.html', form = form, strout = zipped, \
                           N_out = session['n_out'], mytitle=form.searchstring.data,
                        script=script, div=div)

@app.route('/emoji/', methods=['GET', 'POST'])
# @app.route('/emoji/<link>', methods=['GET', 'POST'])
def my_emoji(link = '', title = ''):
    form = emojiForm()
    res = []
    query_val = request.args.get('link',link)
    title = request.args.get('title','')
    # print(link)
    if query_val:
        res = show_emoji(query_val)
        print("query")
        print(query_val)
    if form.validate_on_submit():
        # print(session.get('link_url', 'not set'))
        res = show_emoji(form.audible_url.data)


    return render_template('emoji.html',res=res, form = form, title=title)
