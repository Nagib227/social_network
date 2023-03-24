from data import db_session

from flask import *
 

MAIN_MESSAGE = None
CUR_USER = None

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'very_secret_key_that_no_one_will_ever_crack_bread_1111'
'''
api.add_resource(user_resources.UserListResource, '/api/v2/users')
api.add_resource(user_resources.UserResource, '/api/v2/users/<int:user_id>')

api.add_resource(user_resources.UserListResource, '/api/v2/jobs')
api.add_resource(job_resources.JobResource, '/api/v2/jobs/<int:job_id>')
'''

login_manager = LoginManager()
login_manager.init_app(app)



def main():
    db_session.global_init("db/social_network.db")
    app.register_blueprint(job_api.blueprint)
    app.run()

'''
@app.route('/')
def index():
    global MAIN_MESSAGE, CUR_USER
    db_sess = db_session.create_session()
    jobs = db_sess.query(Job).all()
    data = list(map(lambda x: [x, f"""{db_sess.query(User).filter(User.id == x.team_leader).first().surname} 
{db_sess.query(User).filter(User.id == x.team_leader).first().name}"""], jobs))
    main_message = MAIN_MESSAGE
    print(main_message)
    MAIN_MESSAGE = None
    print(main_message)
    if CUR_USER:
        return render_template('index.html', data=data, user=CUR_USER,
                               main_message=main_message)
    return render_template('index.html', data=data)
'''


if __name__ == '__main__':
    main()
