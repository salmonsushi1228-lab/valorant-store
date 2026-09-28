import base64
import hashlib
import json
import os
import secrets
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from flask import Flask, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")

RIOT_AUTHORIZE_URL = os.environ.get("RIOT_AUTHORIZE_URL", "https://auth.riotgames.com/authorize")
RIOT_TOKEN_URL = os.environ.get("RIOT_TOKEN_URL", "https://auth.riotgames.com/token")

@app.route('/')
def home():
    return render_template('index.html')


def oauth_configuration():
    client_id = os.environ.get("RIOT_CLIENT_ID")
    redirect_uri = os.environ.get("RIOT_REDIRECT_URI")
    if not client_id or not redirect_uri or not app.secret_key:
        return None
    return client_id, redirect_uri


@app.route('/auth/login')
def riot_login():
    config = oauth_configuration()
    if not config:
        return redirect(url_for('home', auth_error='Riot OAuth 설정이 완료되지 않았습니다.'))

    client_id, redirect_uri = config
    verifier = secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode()).digest()
    ).rstrip(b'=').decode()
    state = secrets.token_urlsafe(32)
    session['riot_oauth_state'] = state
    session['riot_code_verifier'] = verifier
    params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'openid account',
        'state': state,
        'nonce': secrets.token_urlsafe(24),
        'code_challenge': challenge,
        'code_challenge_method': 'S256',
    }
    return redirect(f'{RIOT_AUTHORIZE_URL}?{urlencode(params)}')


@app.route('/auth/callback')
def riot_callback():
    config = oauth_configuration()
    code = request.args.get('code')
    state = request.args.get('state')
    if not config or not code or not state or state != session.pop('riot_oauth_state', None):
        return redirect(url_for('home', auth_error='로그인 검증에 실패했습니다. 다시 시도해 주세요.'))

    client_id, redirect_uri = config
    verifier = session.pop('riot_code_verifier', None)
    if not verifier:
        return redirect(url_for('home', auth_error='로그인 세션이 만료되었습니다. 다시 시도해 주세요.'))

    payload = urlencode({
        'grant_type': 'authorization_code',
        'client_id': client_id,
        'code': code,
        'redirect_uri': redirect_uri,
        'code_verifier': verifier,
    }).encode()
    token_request = Request(RIOT_TOKEN_URL, data=payload, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    try:
        with urlopen(token_request, timeout=10) as response:
            token_data = json.loads(response.read().decode())
    except (HTTPError, URLError, ValueError):
        return redirect(url_for('home', auth_error='Riot 인증 토큰을 가져오지 못했습니다.'))

    access_token = token_data.get('access_token')
    if not access_token:
        return redirect(url_for('home', auth_error='Riot 인증 응답에 액세스 토큰이 없습니다.'))
    return redirect(f'{url_for("home")}#access_token={quote(access_token, safe="")}')

# app.run() 부분은 Vercel이 알아서 서버를 띄우므로 삭제하거나 
# 로컬 테스트용 조건문만 남겨둡니다.
if __name__ == '__main__':
    app.run(debug=True)
