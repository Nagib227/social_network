from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired


class ActionsWithTracks(FlaskForm):
    next_track = SubmitField(' ')
    back_track = SubmitField(' ')
