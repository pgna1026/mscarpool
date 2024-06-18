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




<azure에서>
웹 앱 만들기

azure 무료 구독 활성화

az login
구독 선택

 az group create --name <리소스 그룹명> --location eastus

az appservice plan create --name <앱서비스 플랜명> --resource-group <리소스 그룹명> --sku F1 --is-linux

az webapp create --resource-group <리소스 그룹명> --plan <앱서비스 플랜명> --name <앱 명> --runtime "PYTHON:3.9"


깃허브 들어가서 래포지토리 생성
래포지토리에 앱 업로드
.github/workflows 만들어서 그 안에 <앱 명>.yml 추가 
거기에 
      - name: Initialize and apply database migrations
        run: |
          python -m venv venv
          source venv/bin/activate
          flask db init
          flask db migrate -m "Initial migration."
          flask db upgrade
처럼 기본 세팅 추가


https://portal.azure.com/
에 가서 app services 들어가서 <내 앱 이름> 들어가서 배포->배포 센터 들어가서 깃허브 연동

좀 기다리면 배포됨(상태는 깃허브에서 확인)

