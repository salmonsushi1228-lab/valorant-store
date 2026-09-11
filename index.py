from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

# app.run() 부분은 Vercel이 알아서 서버를 띄우므로 삭제하거나 
# 로컬 테스트용 조건문만 남겨둡니다.
if __name__ == '__main__':
    app.run(debug=True)
