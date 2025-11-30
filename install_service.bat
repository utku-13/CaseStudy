@echo off
REM #############################################################
REM  Turkish Technology Case Study - Windows Service Installer
REM  This script must be run as Administrator.
REM #############################################################

REM 1) Set base path to this script's directory (e.g. C:\...\CaseStudy\)
set "BASE_DIR=%~dp0"

REM 2) Full path to the EXE (no quotes here)
set "EXE_PATH=%BASE_DIR%dist\case_study_app\case_study_app.exe"

REM 3) Show what we are going to use as binPath (for debugging)
echo BASE_DIR = %BASE_DIR%
echo EXE_PATH = %EXE_PATH%
echo.

REM 4) Create the Windows service.
REM NOTE: There MUST be a space after 'binPath=' and 'start='.
REM       We pass the EXE path in quotes, then the --loop argument.
sc create CaseStudyService ^
 binPath= "\"%EXE_PATH%\" --loop" ^
 start= auto ^
 DisplayName= "Case Study App Service"

REM 5) Optional: set service description
sc description CaseStudyService "Runs case_study_app.exe in loop mode to refresh outputs every minute."

REM 6) Configure the service to restart automatically on failure
sc failure CaseStudyService reset= 0 actions= restart/60000

REM 7) Start the service
sc start CaseStudyService

echo.
echo Service 'CaseStudyService' create/start commands have been issued.
echo Check 'services.msc' or run 'sc query CaseStudyService' to verify.
echo.
pause
