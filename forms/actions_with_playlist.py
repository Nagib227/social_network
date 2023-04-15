from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired


class ActionsWithPlayList(FlaskForm):
    add_playList = SubmitField(' ')
    direct_order_playList = SubmitField(' ')
    random_order_playList = SubmitField(' ')
