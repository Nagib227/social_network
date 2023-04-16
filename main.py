from data import db_session

from flask import *
from flask_restful import reqparse, abort, Api, Resource

from flask_login import *

from data.user import User
from data.message import Message
from data.chat import Chat

from data.music import find_music

from forms.register import RegisterUserForm
from forms.login import LoginUserForm
from forms.music import MusicForm
from forms.actions_with_tracks import ActionsWithTracks

from data.VARIABLES import LOGIN, PASSWORD

from random import shuffle



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


def processing_search_music(form_music, authorized_user, db_sess):
    if form_music.btn_search.data:
        print("search")
        title_artist_imgUrl_nameFile = find_music(q=request.form["input_music"])
        authorized_user.current_track_info = str(title_artist_imgUrl_nameFile)
    db_sess.commit()
    return None

def processing_tracks_actions(form_actions_playList, authorized_user, db_sess):
    if form_actions_playList.add_playList.data:
        print("add")
        playList = eval(authorized_user.playList)
        title_artist_imgUrl_nameFile = eval(current_user.current_track_info)
        if not title_artist_imgUrl_nameFile in playList:
            playList.append(title_artist_imgUrl_nameFile)
            authorized_user.playList = str(playList)
            
    if form_actions_playList.direct_order_playList.data:
        print("direct")
        order_playList = eval(authorized_user.playList)
        if not order_playList:
            return None
        authorized_user.current_order_playList = str(order_playList)
        authorized_user.current_track_info = str(order_playList[::-1][0])
        authorized_user.current_ind_track = 0
        
    if form_actions_playList.random_order_playList.data:
        print("random")
        order_playList = eval(authorized_user.playList)
        if not order_playList:
            return None
        shuffle(order_playList)
        authorized_user.current_order_playList = str(order_playList)
        authorized_user.current_track_info = str(order_playList[::-1][0])
        authorized_user.current_ind_track = 0
        
    if form_actions_playList.next_track.data:
        print("next")
        order_playList = eval(authorized_user.current_order_playList)
        if not order_playList:
            return None
        authorized_user.current_ind_track += 1
        if authorized_user.current_ind_track >= len(order_playList):
            authorized_user.current_ind_track = 0
        ind_track = authorized_user.current_ind_track
        authorized_user.current_track_info = str(order_playList[::-1][ind_track])
        
    if form_actions_playList.back_track.data:
        print("back")
        order_playList = eval(authorized_user.current_order_playList)
        if not order_playList:
            return None
        if authorized_user.current_ind_track <= 0:
            authorized_user.current_ind_track = len(order_playList)
        authorized_user.current_ind_track -= 1
        ind_track = authorized_user.current_ind_track
        authorized_user.current_track_info = str(order_playList[::-1][ind_track])

    db_sess.commit()
    return None


@app.route('/', methods=['GET', 'POST'])
@app.route('/news', methods=['GET', 'POST'])
def news():
    if not current_user.is_authenticated:
        return redirect('/login')
    
    autoplay = "autoplay"
    
    db_sess = db_session.create_session()
    authorized_user = db_sess.query(User).filter(User.id == current_user.id).first()
    
    form_music = MusicForm()
    form_actions_tracks = ActionsWithTracks()
    
    if form_music.validate_on_submit():
        processing_search_music(form_music, authorized_user, db_sess)
            
    if form_actions_tracks.validate_on_submit():
        processing_tracks_actions(form_actions_tracks, authorized_user, db_sess)
    
    cur_track = ""
    if authorized_user.current_track_info:
        track_info = eval(authorized_user.current_track_info)
        print(track_info)
        cur_track = track_info[3]
     
    return render_template('news.html', link_logo=url_for('static', filename='img/logo.png'),
                           form_music=form_music,
                           form_actions_tracks=form_actions_tracks,
                           src_music=f'static/music/wav/{cur_track}.wav',
                           autoplay=autoplay)

@app.route('/register', methods=['GET', 'POST'])
def reqister():
    if current_user.is_authenticated:
        return redirect('/news')
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
            email=form.email.data,
            playList="[]"
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/news')
    form = LoginUserForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=True) # зарегистрированный user # current_user
            return redirect(f"/news")
        return render_template('login.html',
                                title='Авторизация',
                                message="Неправильный логин или пароль",
                                form=form)
    return render_template('login.html', title='Авторизация', form=form)

@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.get(User, user_id)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == '__main__':
    main()
