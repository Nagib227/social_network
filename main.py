from data import db_session

from flask import *
from flask_restful import reqparse, abort, Api, Resource

from flask_login import LoginManager, login_user, current_user

from data.user import User
from data.message import Message
from data.chat import Chat

from data.music import find_music

from forms.register import RegisterUserForm
from forms.login import LoginUserForm
from forms.music import MusicForm

import vlc
# import winsound
# import sounddevice as sd
# import soundfile as sf
# import simpleaudio as sa


LOGIN = ""
PASSWORD = ""

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
'''


def main():
    db_session.global_init("db/social_network.db")
    # app.register_blueprint(job_api.blueprint)
    app.run()


@app.route('/')
def to_the_news():
    return render_template('chat.html')


@app.route('/news', methods=['GET', 'POST'])
def news():
    if not current_user.is_authenticated:
        return redirect('/login')
    form_music = MusicForm()
    if form_music.validate_on_submit():
        print(form_music.name_music.data, 1)
        print(form_music.btn_search.data, 2)
        if form_music.btn_search.data:
            title_artist_imgUrl = find_music(login=LOGIN, password=PASSWORD,
                                             q=request.form["name_music"])
            print(title_artist_imgUrl)
        if form_music.play.data:
            p = vlc.MediaPlayer("file:///music/wav/temp.wav")
            p.play()
    return render_template('news.html', link_logo=url_for('static', filename='img/logo.png', form_music=form_music))


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    return render_template('profile.html')


@app.route('/chats')
def chats():
    return render_template('chats.html')


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form_music = MusicForm()
    form = RegisterUserForm()
    if form_music.validate_on_submit():
        print(form_music.name_music.data, 1)
        print(form_music.btn_search.data, 2)
        if form_music.btn_search.data:
            title_artist_imgUrl = find_music(login=LOGIN, password=PASSWORD,
                                             q=request.form["name_music"])
            print(title_artist_imgUrl)
        if form_music.play.data:
            p = vlc.MediaPlayer("file:///music/wav/temp.wav")
            p.play()
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
    form_music = MusicForm()
    form = LoginUserForm()
    if form_music.validate_on_submit():
        print(form_music.name_music.data, 1)
        print(form_music.btn_search.data, 2)
        if form_music.btn_search.data:
            title_artist_imgUrl = find_music(login=LOGIN, password=PASSWORD,
                                             q=request.form["name_music"])
            print(title_artist_imgUrl)
        if form_music.play.data:
            # wave_object = sa.WaveObject.from_wave_file('music/wav/temp.wav')
            # play_object = wave_object.play()
            # play_object.wait_done()
            # array, smp_rt = sf.read('music/wav/temp.wav', dtype='float32')
            # sd.play(array, smp_rt)
            # status = sd.wait()
            # sd.stop()
            p = vlc.MediaPlayer("file:///music/wav/temp.wav")
            p.play()
            # winsound.PlaySound('music/wav/temp.wav', winsound.SND_FILENAME)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=True)
            print(current_user, 3) # зарегистрированный user # current_user
            return redirect(f"/news")
        return render_template('login.html',
                               title='Авторизация',
                               message="Неправильный логин или пароль",
                               form=form,
                               form_music=form_music)
    return render_template('login.html', title='Авторизация', form=form, form_music=form_music)
# current_user
'''
@app.route('/music', methods=['GET', 'POST'])
def music():
    print(request.method)
    if request.method == "POST":
        print(request.form["name_music"])
        print(request.form["find_music"])
        # login
        # password
        find_music(login="", password="", q=request.form["name_music"])
        p = vlc.MediaPlayer("file:///music/wav/temp.wav")
        p.play()
    return render_template('music.html')
'''

if __name__ == '__main__':
    main()
