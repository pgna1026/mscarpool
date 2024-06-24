# 마송고 카풀 서비스 출시!!

## <로컬에서 사용법>

### 가상환경 만들기

1. python -m venv venv

2. venv\Scripts\activate #안되면 win+x눌러 PowerShell을 관리자 권한으로 실행 -> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -> y

3. pip install -r requirements.txt

4. flask db init

5. flask db migrate -m "Initial migration."

6. flask db upgrade

7. python run.py


### 가상환경 리셋

1. deactivate

2. venv 지우기


-----------------

## <azure에서 사용법>

1. azure 무료 구독 활성화

2. vscode에서 azure app service, azure accont 확장프로그램 설치

3. az login

4. 구독 선택

5. az group create --name <리소스 그룹명> --location eastus

6. az appservice plan create --name <앱서비스 플랜명> --resource-group <리소스 그룹명> --sku F1 --is-linux

7. az webapp create --resource-group <리소스 그룹명> --plan <앱서비스 플랜명> --name <앱 명> --runtime "PYTHON:3.9"

8.깃허브 들어가서 래포지토리 생성

9. 래포지토리에 앱 업로드

10. https://portal.azure.com/ 에 가서 app services 들어가서 <내 앱 이름> 들어가서 배포->배포 센터 들어가서 깃허브 연동

11. 설정 -> 환경 변수 들어가 추가-> config의 시크릿키 추가

12. 개발 도구 -> 고급 도구 -> 이동 선택 -> SSH 클릭

13. cd /home/site/wwwroot

14. source /antenv/bin/activate

15. flask db upgrade 를 입력 해서 마이그래이션 적용

16. 좀 기다리면 배포됨(상태는 깃허브에서 확인)
