# Backend for validation reports

### Installation:

#### 1) Go to backend directory

```bash
cd pro.guap-report-validator/report-validator/backend
```

#### 2) Installing the virtual environment

```bash
python3 -m venv venv
```

#### 3) Activating the virtual environment

##### on Linux

```bash
source venv/Scripts/Activate
```

##### on Windows

```bash
venv/Scripts/Activate
```

#### 4) Installing dependencies:

```bash
pip install -e .
```

### Run server in development mode(\* --reload)

```bash
uvicorn api.main:api --reload
```
