@echo off
REM ===================================================
REM Script chạy Streamlit app trên Windows
REM Double-click file này để khởi động app
REM ===================================================

cd /d "%~dp0"

echo ====================================================
echo   Uplift Modeling - Streamlit App
echo ====================================================
echo.

REM Check Python
where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python chua duoc cai. Tai tu python.org va cai dat.
    pause
    exit /b 1
)

REM Tao venv neu chua co
if not exist ".venv" (
    echo [INFO] Tao virtual environment lan dau...
    python -m venv .venv
    call .venv\Scripts\activate.bat
    echo [INFO] Cai dependencies...
    pip install --upgrade pip
    pip install -r requirements.txt
) else (
    call .venv\Scripts\activate.bat
)

REM Check models folder
if not exist "models\cf_final.pkl" (
    echo.
    echo [WARNING] Folder models\ thieu file cf_final.pkl
    echo Hay copy artifacts tu Google Drive vao folder models\
    echo.
    pause
)

REM Run Streamlit
echo.
echo [INFO] Khoi dong Streamlit app...
echo [INFO] App se mo tai http://localhost:8501
echo [INFO] Nhan Ctrl+C de dung
echo.
streamlit run app.py

pause
