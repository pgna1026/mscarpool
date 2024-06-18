지피티와 함께 몆시간 삽질끝에 만든 대작!

<로컬에서>

가상환경 만들기

python -m venv venv

venv\Scripts\activate #안되면 win+x눌러 PowerShell을 관리자 권한으로 실행 -> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -> y

pip install -r requirements.txt

flask db init

flask db migrate -m "Initial migration."

flask db upgrade

python run.py



가상환경 리셋

deactivate

venv 지우기


.
.
.
<azure에서>

run.py를
"""
from app import app, socketio

if __name__ == '__main__':
 socketio.run(app, debug=True)
"""
와 같이 수정

requirements.tat를 
"""
Flask==2.0.3
Flask-SQLAlchemy==2.5.1
SQLAlchemy==1.4.32
Flask-Migrate==4.0.7
Flask-SocketIO==5.1.1
Flask-WTF==0.15.1
Flask-Login==0.5.0
WTForms==2.3.3
Werkzeug==2.0.3
python-engineio>=4.0.0
python-socketio>=5.0.2
scikit-learn
numpy
gunicorn
eventlet
"""
로 수정(numpy, gunicorn, eventlet 추가함)

startup.txt 생성
"""gunicorn --worker-class eventlet -w 1 run:app"""

config.py 수정
"""import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///site.db' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

"""



azure 무료 구독 활성화

vscode에서 azure app service, azure accont 확장프로그램 설치

az login
구독 선택

 az group create --name <리소스 그룹명> --location eastus

az appservice plan create --name <앱서비스 플랜명> --resource-group <리소스 그룹명> --sku F1 --is-linux

az webapp create --resource-group <리소스 그룹명> --plan <앱서비스 플랜명> --name <앱 명> --runtime "PYTHON:3.9"


깃허브 들어가서 래포지토리 생성
래포지토리에 앱 업로드


https://portal.azure.com/
에 가서 app services 들어가서 <내 앱 이름> 들어가서 배포->배포 센터 들어가서 깃허브 연동

설정 -> 환경 변수 들어가 추가-> config의 시크릿키 추가

개발 도구 -> 고급 도구 -> 이동 선택 -> SSH 클릭
"""
cd home/site/wwwroot
source /antenv/bin/activate
flask db upgrade
""" 입력 해서 마이그래이션 적용


좀 기다리면 배포됨(상태는 깃허브에서 확인)

