from data import db_session

from flask import *
from flask_restful import reqparse, abort, Api, Resource

from flask_login import LoginManager, login_user, current_user

from data.user import User
from data.message import Message
from data.chat import Chat

from forms.register import RegisterUserForm
from forms.login import LoginUserForm
 

CUR_USER = None

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'very_secret_key_that_no_one_will_ever_crack_bread_1111'

login_manager = LoginManager()
login_manager.init_app(app)
'''
api.add_resource(user_resources.UserListResource, '/api/v2/users')
api.add_resource(user_resources.UserResource, '/api/v2/users/<int:user_id>')

api.add_resource(user_resources.UserListResource, '/api/v2/jobs')
api.add_resource(job_resources.JobResource, '/api/v2/jobs/<int:job_id>')


login_manager = LoginManager()
login_manager.init_app(app)
'''


def main():
    db_session.global_init("db/social_network.db")
    # app.register_blueprint(job_api.blueprint)
    app.run()


@app.route('/')
def index():
    return render_template('index.html', link_logo=url_for('static', filename='img/logo.png'))


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterUserForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            surname=form.surname.data,
            name=form.name.data,
            age=int(form.age.data),
            num_phone=form.num_phone.data,
            address=form.address.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)

@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    global CUR_USER
    form = LoginUserForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=True)
            print(current_user) # зарегистрированный user # current_user
            return redirect(f"/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)
# current_user

if __name__ == '__main__':
    main()
