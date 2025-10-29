@echo off
echo ================================================
echo FITNESS VIDEO FILTER
echo ================================================
echo.
echo This will scan all transcripts and find fitness-related videos
echo.
pause

python filter_fitness_videos.py transcripts 5

echo.
echo ================================================
echo Check these files:
echo - fitness_videos.json (machine-readable)
echo - fitness_videos_report.txt (human-readable list)
echo ================================================
pause
