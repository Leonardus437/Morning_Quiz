@echo off
echo Running system test...
echo.
echo Output will be saved to TEST_RESULTS.txt
echo.

TEST_SYSTEM.bat > TEST_RESULTS.txt 2>&1

echo.
echo ✅ Test complete! Opening results...
echo.

notepad TEST_RESULTS.txt

pause
