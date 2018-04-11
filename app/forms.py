from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField
from wtforms.validators import DataRequired, URL

class AppForm(FlaskForm):
    searchstring = StringField('Search:',default='Apple', validators=[DataRequired()])
    audible_url = StringField('Paste audible.com url here:',default='', validators=[DataRequired()])
    fiction = BooleanField('Fiction', default=True)
    history = BooleanField('History')
    business = BooleanField('Business')
    submit = SubmitField('Submit')

class emojiForm(FlaskForm):
    audible_url = StringField('Paste audible.com url here:',default='', validators=[DataRequired(), URL()])
    submit = SubmitField('Submit')

# class N_result(FlaskForm):
#     increment = SubmitField('increment')
