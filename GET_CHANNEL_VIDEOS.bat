@echo off
echo ================================================
echo YOUTUBE CHANNEL VIDEO EXTRACTOR
echo ================================================
echo.
echo This will extract ALL video URLs from your channels
echo This may take 5-10 minutes depending on channel size
echo.
echo Do you want to test with just 10 videos per channel first? (y/n)
set /p test_mode="Enter y for test mode, n for full extraction: "

if /i "%test_mode%"=="y" (
    echo.
    echo TEST MODE: Extracting first 10 videos from each channel...
    python extract_channel_videos.py "youtube channels.md" 10
) else (
    echo.
    echo FULL MODE: Extracting ALL videos from each channel...
    python extract_channel_videos.py "youtube channels.md"
)

echo.
echo ================================================
echo Check the 'channel_videos' folder for results
echo ================================================
pause
