from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired


class MusicForm(FlaskForm):
    input_music = StringField('Название трека', validators=[DataRequired()])
    btn_search = SubmitField(' ')

