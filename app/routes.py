from app import app
from flask import render_template, flash, redirect, request, session
from app.forms import AppForm, emojiForm#, N_result
from app.search_app import search_app, suggestion_plot, plot_2D
from app.emoji_app import show_emoji
from bokeh.embed import components
from bokeh.resources import CDN
from bokeh.plotting import figure
from bokeh.models.glyphs import Text





@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/app', methods=['GET', 'POST'])
def my_app():
    form = AppForm()
    Sup = ""
    session['n_out'] = 5
    zipped = ['sou','/index']
    if form.validate_on_submit():
        print('validate')
    zipped = search_app(form.searchstring.data, 5)
        # print(zipped)
    # print(session['n_out'])
    p = suggestion_plot(form.searchstring.data)
    script, div = components(p)
    print(zipped)
    return render_template('app.html', form = form, strout = zipped, \
                           N_out = session['n_out'],
                        script=script, div=div,  bokeh_js=CDN.render_js())

@app.route('/emoji', methods=['GET', 'POST'])
def my_emoji():
    form = emojiForm()
    res = []
    if form.validate_on_submit():
        print('emoji validated')
        res = show_emoji(form.audible_url.data)
    # p = suggestion_plot()
    # script, div = components(p)
    return render_template('emoji.html',res=res, form = form)
