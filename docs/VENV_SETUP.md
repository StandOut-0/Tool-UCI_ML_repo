# Day1: venv 프로젝트 설정

이 문서는 로컬 개발을 위한 Python 가상환경(venv) 설정 방법을 정리합니다.

Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Windows (cmd):

```cmd
python -m venv .venv
.\.venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Unix / macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

팁:
- VSCode에서 작업한다면 `.venv`를 워크스페이스 인터프리터로 설정하세요.
- 이미 설치된 패키지를 최신화하려면 `pip install -r requirements.txt --upgrade`를 사용하세요.
