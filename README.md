# fastAPI

### VSCode 사용

## 환경 구축(가상환경에서 사용)
1. VSCode에서 Python 확장 프로그램 설치.
2. cmd 입력

**윈도우**
```
C:\Users\pahkey> cd \
C:\> mkdir venvs
C:\> cd venvs

C:\venvs> python -m venv myapi        #myapi 대신 원하는 이름 입력 가능.
```
**Mac**
```
C:\Users\pahkey> mkdir venvs
C:\Users\pahkey> cd venvs

C:\Users\pahkey\venvs> python3 -m venv myapi      #myapi 대신 원하는 이름 입력 가능.
```
**가상환경 진입**
- 터미널(윈도우 기준)
```
>  cd C:\venvs\myapi\Scripts
C:\venvs\myapi\Scripts> activate
```
- VSCode
ctrl+shift+p 입력 -> Python:Select Interpreter 선택 -> 가상환경(경로확인) 선택
![image](https://github.com/user-attachments/assets/c3445d03-db3a-4d3d-8cf1-72fbdd7d328d)
![image](https://github.com/user-attachments/assets/654c820d-816c-415c-a0bd-10da42d7b4d1)


**FastAPI 설치**
```
(myapi) C:\venvs\myapi\Scripts> pip install fastapi
```
**uvicorn 설치 - 비동기 호출 지원하는 파이썬용 웹서버**
```
pip install uvicorn
```
**가상환경 벗어나기**
```
(myapi) C:\venvs\myapi\Scripts> deactivate
```

**실행**
```
uvicorn test:app --reload
```

http://127.0.0.1:8000 브라우저에서 입력.

![image](https://github.com/user-attachments/assets/d7337fb7-3d2a-4313-ac84-4e0cb355c697)

실행 성공!

http://127.0.0.1:8000/docs에서 API 문서 확인 가능
