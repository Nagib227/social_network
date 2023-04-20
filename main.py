from data import db_session

from flask import *
from flask_restful import reqparse, abort, Api, Resource, url_for

from flask_login import *

from data.user import User
from data.news import News
from data.message import Message
from data.chat import Chat

from data.music import find_music

from forms.register import RegisterUserForm
from forms.login import LoginUserForm
from forms.music import MusicForm
from forms.actions_with_tracks import ActionsWithTracks
from forms.actions_with_playList import ActionsWithPlayList

from forms.change_profile import FormChangeProfile
from werkzeug.utils import secure_filename


from data.VARIABLES import LOGIN, PASSWORD, ALLOWED_EXTENSIONS

from random import shuffle



app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'very_secret_key_that_no_one_will_ever_crack_bread_1111'

login_manager = LoginManager()
login_manager.init_app(app)


def main():
    db_session.global_init("db/social_network.db")
    app.run()


@app.route('/', methods=['GET', 'POST'])
@app.route('/news', methods=['GET', 'POST'])
def news():
    if not current_user.is_authenticated:
        return redirect('/login')

    autoplay = ""

    db_sess = db_session.create_session()
    authorized_user = db_sess.query(User).filter(User.id == current_user.id).first()

    form_music, form_actions_playList, form_actions_tracks = creat_forms_music()
    
    if form_music.validate_on_submit():
        processing_search_music(form_music=form_music, authorized_user=authorized_user, db_sess=db_sess)

    elif form_actions_playList.validate_on_submit():
        processing_playList_actions(form_actions_playList, authorized_user, db_sess)
            
    elif form_actions_tracks.validate_on_submit():
        processing_tracks_actions(form_actions_tracks, authorized_user, db_sess)

    elif request.method == 'POST':
        name_track = request.form.get("name_track", False)
        text_news = request.form.get("text_news", False)
        if name_track:
            processing_search_music(name_track=name_track, authorized_user=authorized_user, db_sess=db_sess)
        if text_news:
            add_news(text_news=text_news, creator_id=current_user.id)


    cur_track = get_current_track(authorized_user)
    ready_news = get_news(authorized_user, db_sess)
     
    return render_template('news.html', link_logo=url_for('static', filename='img/logo.png'),
                           form_music=form_music,
                           form_actions_playList=form_actions_playList,
                           form_actions_tracks=form_actions_tracks,
                           src_music=f'/static/music/wav/{cur_track}.wav',
                           autoplay=autoplay,
                           current_user=current_user,
                           playList=eval(authorized_user.playList),
                           news=ready_news)


def add_news(text_news, creator_id):
    db_sess = db_session.create_session()
    news = News(
        text=text_news,
        creator_id=creator_id)
    db_sess.add(news)
    db_sess.commit()
    

@app.route('/profile/<int:profile_id>', methods=['GET', 'POST'])
def profile(profile_id):
    if not current_user.is_authenticated:
        return redirect('/login')
    
    autoplay = ""
    message = ""

    change = profile_id == current_user.id
    
    db_sess = db_session.create_session()
    authorized_user = db_sess.query(User).filter(User.id == current_user.id).first()
    profile_user = db_sess.query(User).filter(User.id == profile_id).first()

    form_change = FormChangeProfile()

    form_music, form_actions_playList, form_actions_tracks = creat_forms_music()
    
    if form_music.validate_on_submit():
        processing_search_music(form_music=form_music, authorized_user=authorized_user, db_sess=db_sess)

    if form_actions_playList.validate_on_submit():
        processing_playList_actions(form_actions_playList, authorized_user, db_sess)
            
    if form_actions_tracks.validate_on_submit():
        processing_tracks_actions(form_actions_tracks, authorized_user, db_sess)

    if form_change.validate_on_submit() and change:
        print("save img")
        message = processing_form_change(form_change, authorized_user, db_sess)
        if not message:
            return redirect('#header')

    cur_track = get_current_track(authorized_user)
    profile_news = get_news(authorized_user, db_sess, filter_user=True)
    
    form_change = put_values_in_form_change(form_change, profile_user)
     
    return render_template('profile.html', link_logo=url_for('static', filename='img/logo.png'),
                           form_music=form_music,
                           form_actions_playList=form_actions_playList,
                           form_actions_tracks=form_actions_tracks,
                           src_music=f'/static/music/wav/{cur_track}.wav',
                           autoplay=autoplay,
                           current_user=current_user,
                           playList=eval(authorized_user.playList),
                           profile_user=profile_user,
                           profile_news=profile_news,
                           change=change,
                           form_change=form_change,
                           message=message)

def allowed_file(filename):
    """ Функция проверки расширения файла """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_img_profile(file, authorized_user, db_sess):
    file.save(f"static/img_profiles/{authorized_user.id}.png")

    authorized_user.way_profile_img = f"/static/img_profiles/{authorized_user.id}.png"
    db_sess.commit()


@app.route('/chat/<chat_id>')
@app.route('/chat')
def chat1(chat_id=3):
    return render_template('chat.html')


@app.route('/chats')
def chats():
    return render_template('chats.html')


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


def creat_forms_music():
    form_music = MusicForm()
    form_actions_playList = ActionsWithPlayList()
    form_actions_tracks = ActionsWithTracks()
    return form_music, form_actions_playList, form_actions_tracks

def get_current_track(authorized_user):
    cur_track = ""
    if authorized_user.current_track_info:
        track_info = eval(authorized_user.current_track_info)
        print(track_info)
        cur_track = track_info[3]
    return cur_track


def get_news(authorized_user, db_sess, filter_user=None):
    if filter_user:
        prenews = db_sess.query(User.name, User.surname, News.text, News.creation_date) \
                  .filter(News.creator_id == authorized_user.id).join(User, User.id == News.creator_id).all()
    else:
        prenews = db_sess.query(User.name, User.surname, News.text, News.creation_date)\
                  .join(User, User.id == News.creator_id).all()

    ready_news = []
    for new in prenews:
        time = ':'.join(str(new[3].time()).split('.')[0].split(':')[:-1])
        date = str(new[3].date())
        new = [*new[:-1], f'{date}, {time}']
        ready_news.append(new)
    ready_news.sort(key=lambda a: a[3], reverse=True)

    print("jfgvjfg   ", ready_news)
    return ready_news


def put_values_in_form_change(form_change, profile_user):
    form_change.surname.data = profile_user.surname
    form_change.name.data = profile_user.name
    form_change.age.data = profile_user.age
    form_change.num_phone.data = profile_user.num_phone
    form_change.address.data = profile_user.address
    return form_change


def processing_search_music(form_music=None, name_track="", authorized_user=None, db_sess=None):
    if form_music:
        if form_music.btn_search.data:
            print("search")
            title_artist_imgUrl_nameFile = find_music(q=form_music.input_music.data)

    if name_track:
        print("name_track")
        title_artist_imgUrl_nameFile = find_music(q=name_track)
    authorized_user.current_track_info = str(title_artist_imgUrl_nameFile)
    db_sess.commit()
    return None


def processing_playList_actions(form_actions_playList, authorized_user, db_sess):
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

    db_sess.commit()
    return None


def processing_tracks_actions(form_actions_tracks, authorized_user, db_sess):
    if form_actions_tracks.next_track.data:
        print("next")
        order_playList = eval(authorized_user.current_order_playList)
        if not order_playList:
            return None
        authorized_user.current_ind_track += 1
        if authorized_user.current_ind_track >= len(order_playList):
            authorized_user.current_ind_track = 0
        ind_track = authorized_user.current_ind_track
        authorized_user.current_track_info = str(order_playList[::-1][ind_track])
        
    if form_actions_tracks.back_track.data:
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

def processing_form_change(form_change, authorized_user, db_sess):
    message = ""
    
    authorized_user.surname = form_change.surname.data
    authorized_user.name = form_change.name.data
    try:
        authorized_user.age = int(form_change.age.data)
    except ValueError:
        message = "Не верный формат возраста"
    authorized_user.num_phone = form_change.num_phone.data
    authorized_user.address = form_change.address.data
    db_sess.commit()

    fileName = secure_filename(form_change.profile_img.data.filename)
    if fileName and not allowed_file(fileName):
        message = "Не верный формат изображения"
    elif fileName:
        file = form_change.profile_img.data
        save_img_profile(file, authorized_user, db_sess)
    return message


if __name__ == '__main__':
    main()
