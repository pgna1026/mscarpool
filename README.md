지피티와 함께 몆시간 삽질끝에 만든 대작!



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

