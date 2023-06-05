from flask import Flask, redirect, url_for,request
from flask_oauthlib.client import OAuth

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
oauth = OAuth(app)

google = oauth.remote_app(
    'google',
    consumer_key='480090602143-naqm1phl4lgn81pt44d0350omrr9rg3e.apps.googleusercontent.com',
    consumer_secret='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',
    request_token_params={
        'scope': 'email profile'
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params={
        'grant_type': 'authorization_code'
    }
)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login')
def login():
    return google.authorize(callback=url_for('authorized', _external=True))

@app.route('/authorized')
def authorized():
    resp = google.authorized_response()
    if resp is None:
        return 'Access denied: reason={0} error={1}'.format(
            request.args['error_reason'],
            request.args['error_description']
        )
    access_token = resp['access_token']
    # Usa el access_token para acceder a los datos del usuario










if __name__ == '__main__':
    app.run()
