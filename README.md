# valorant-store

## Riot OAuth 설정

로그인은 사이트가 아이디나 비밀번호를 받지 않고, Riot Games의 공식 OAuth 인증 페이지로 이동하는 방식입니다. 시작하기 전에 Riot Developer Portal에서 발급받은 앱 정보를 배포 환경에 설정하세요.

```bash
export FLASK_SECRET_KEY='long-random-secret'
export RIOT_CLIENT_ID='your-approved-client-id'
export RIOT_REDIRECT_URI='https://your-domain.example/auth/callback'
```

`RIOT_REDIRECT_URI`는 Riot 앱 설정에 등록된 콜백 주소와 정확히 일치해야 합니다. 필요하면 `RIOT_AUTHORIZE_URL` 및 `RIOT_TOKEN_URL`도 OAuth 제공자가 지정한 값으로 설정할 수 있습니다.
