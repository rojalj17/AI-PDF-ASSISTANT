@echo off
REM AI PDF Assistant - Windows setup and run script

IF NOT EXIST venv (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate

echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Make sure Ollama is running and the following models are pulled:
echo   ollama pull gemma3:4b
echo   ollama pull nomic-embed-text
echo.

echo Starting AI PDF Assistant...
echo Open http://localhost:8000 in your browser once it's ready.
python server.py

pause
