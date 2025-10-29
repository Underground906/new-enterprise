@echo off
echo ================================================
echo YouTube Transcript Fetcher
echo ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/3] Checking dependencies...
pip show yt-dlp >nul 2>&1
if errorlevel 1 (
    echo Installing yt-dlp...
    pip install yt-dlp
) else (
    echo yt-dlp already installed
)

echo.
echo [2/3] Starting transcript extraction...
echo This will process 455 videos with 2-second delays
echo Estimated time: ~15-20 minutes
echo.
echo Press Ctrl+C to cancel, or
pause

echo.
echo [3/3] Fetching transcripts...
python fetch_transcripts_ytdlp.py youtube_videos_only.txt 2

echo.
echo ================================================
echo DONE! Check the 'transcripts' folder for results
echo ================================================
pause
