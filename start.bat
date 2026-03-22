@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"

:: ── Color codes ──
:: Colors via ANSI escape sequences (Windows 10+)
:: Green=32, Yellow=33, Red=31, Cyan=36, Magenta=35, White=37, Bold=1, Reset=0

:: ── Helper labels ──
goto :main

:print_header
echo.
echo [36m╔══════════════════════════════════════════════════════════╗[0m
echo [36m║[0m                                                          [36m║[0m
echo [36m║[0m   [1;35m★  Django E-Commerce Platform  ★[0m                       [36m║[0m
echo [36m║[0m      [37mAutomated Setup ^& Configuration[0m                      [36m║[0m
echo [36m║[0m                                                          [36m║[0m
echo [36m╚══════════════════════════════════════════════════════════╝[0m
echo.
goto :eof

:print_step
:: %~1 = step number, %~2 = total, %~3 = description
echo [1;36m──────────────────────────────────────────────────────────────[0m
echo   [1;33m[%~1/%~2][0m  [1;37m%~3[0m
echo [1;36m──────────────────────────────────────────────────────────────[0m
goto :eof

:print_success
echo   [1;32m✔[0m  %~1
goto :eof

:print_info
echo   [36mℹ[0m  %~1
goto :eof

:print_warning
echo   [1;33m⚠[0m  %~1
goto :eof

:print_error
echo   [1;31m✘[0m  %~1
goto :eof

:print_done
echo.
echo [1;32m┌──────────────────────────────────────────────────────────┐[0m
echo [1;32m│              ✔  All steps completed!                    │[0m
echo [1;32m└──────────────────────────────────────────────────────────┘[0m
echo.
goto :eof

:print_server_start
echo.
echo [1;35m┌──────────────────────────────────────────────────────────┐[0m
echo [1;35m│          🚀  Launching Development Server...            │[0m
echo [1;35m│          Press Ctrl+C to stop the server                │[0m
echo [1;35m└──────────────────────────────────────────────────────────┘[0m
echo.
goto :eof

:: ═══════════════════════════════════════════════════════
::  Main script
:: ═══════════════════════════════════════════════════════
:main

call :print_header

:: ── Step 1: uv package manager ──
call :print_step 1 7 "Checking for uv package manager"
where uv >nul 2>nul
if %errorlevel% neq 0 (
    call :print_warning "uv is not installed. Installing..."
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    set "PATH=%USERPROFILE%\.local\bin;%USERPROFILE%\.cargo\bin;%PATH%"
    call :print_success "uv installed successfully"
) else (
    call :print_success "uv is already installed"
)

:: ── Step 2: Virtual environment ──
echo.
call :print_step 2 7 "Checking virtual environment"
if not exist ".venv" (
    call :print_info "Creating virtual environment (.venv)..."
    call uv venv
    call :print_success "Virtual environment created"
) else (
    call :print_success "Virtual environment already exists"
)

:: ── Step 3: Dependencies ──
echo.
call :print_step 3 7 "Installing dependencies"
call :print_info "Running uv sync..."
call uv sync
call :print_success "Dependencies installed"

set PYTHON=.venv\Scripts\python.exe

:: ── Step 4: Database migrations ──
echo.
call :print_step 4 7 "Applying database migrations"
call :print_info "Running makemigrations..."
%PYTHON% manage.py makemigrations
call :print_info "Running migrate..."
%PYTHON% manage.py migrate
call :print_success "Database migrations applied"

:: ── Step 5: Admin user ──
echo.
call :print_step 5 7 "Admin user creation"
echo.
set /p CREATE_ADMIN="  [1;33m?[0m  Do you want to create an admin user? [1;37m(y/n)[0m: "
if /i "%CREATE_ADMIN%"=="y" (
    echo.
    %PYTHON% manage.py createsuperuser
    call :print_success "Admin user created"
) else (
    call :print_info "Skipped admin user creation"
)

:: ── Step 6: Fake data seeding ──
echo.
call :print_step 6 7 "Fake data seeding"
echo.
set /p SEED_DATA="  [1;33m?[0m  Do you want to seed fake data into the database? [1;37m(y/n)[0m: "
if /i "%SEED_DATA%"=="y" (
    if exist "data_seeding.sql" (
        call :print_info "Loading data_seeding.sql..."
        %PYTHON% seed_db.py
        if %errorlevel% neq 0 (
            call :print_error "Seeding failed — check output above"
        ) else (
            call :print_success "Fake data loaded successfully"
        )
    ) else (
        call :print_error "data_seeding.sql not found"
    )
) else (
    call :print_info "Skipped data seeding"
)

:: ── Step 7: Start server ──
echo.
call :print_step 7 7 "Starting Django development server"
call :print_server_start
%PYTHON% manage.py runserver

pause
