from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired


class FormChangeProfile(FlaskForm):
    profile_img = FileField('Img')
    surname = StringField('Фамилия', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    age = StringField('Возраст', validators=[DataRequired()])
    num_phone = StringField('Номер телефона', validators=[DataRequired()])
    address = StringField('Адрес', validators=[DataRequired()])
    ok_submit = SubmitField('Сохранить')
