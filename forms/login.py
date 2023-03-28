from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired


class LoginUserForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')
