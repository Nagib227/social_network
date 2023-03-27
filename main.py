from data import db_session

from flask import *
from flask_restful import reqparse, abort, Api, Resource
 

CUR_USER = None

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'very_secret_key_that_no_one_will_ever_crack_bread_1111'
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


if __name__ == '__main__':
    main()
