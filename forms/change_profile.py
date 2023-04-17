from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired


class FormChangeProfile(FlaskForm):
    profile_img = FileField('Img')
    ok_submit = SubmitField('Сохранить')
