@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"

:: Enable ANSI color support (Virtual Terminal Processing) for CMD
reg add HKCU\Console /v VirtualTerminalLevel /t REG_DWORD /d 1 /f >nul 2>&1

:: =============================================================================
:: joi - Project Development Tool (Windows)
:: =============================================================================

set "JOI_VERSION=0.1.0"
set "JOI_NAME=joi"
set "JOI_DESC=Project Development Tool"
set "JOI_LOCK_FILE=%~dp0.joi.lock"
set "JOI_ENV_FILE=%~dp0.joi.env"
set "PYTHON="

:: Flags
set "JOI_YES=0"
set "JOI_QUIET=0"
set "JOI_VERBOSE=0"
set "JOI_NO_COLOR=0"

:: Config defaults
set "JOI_SEED_DATA=y"
set "JOI_CREATE_ADMIN=n"
set "JOI_PORT=8000"

:: =============================================================================
:: ANSI color codes (Windows 10+)
:: =============================================================================
if "%JOI_NO_COLOR%"=="1" (
    set "C_RESET=" & set "C_BOLD=" & set "C_RED="
    set "C_GREEN=" & set "C_YELLOW=" & set "C_CYAN="
    set "C_WHITE=" & set "C_DIM="
) else (
    set "C_RESET=[0m"
    set "C_BOLD=[1m"
    set "C_RED=[1;31m"
    set "C_GREEN=[1;32m"
    set "C_YELLOW=[1;33m"
    set "C_CYAN=[1;36m"
    set "C_WHITE=[1;37m"
    set "C_DIM=[2m"
)

:: =============================================================================
:: Argument parsing
:: =============================================================================
set "COMMAND="

:parse_args
if "%~1"=="" goto :after_parse
if "%~1"=="-h" goto :show_help
if "%~1"=="--help" goto :show_help
if "%~1"=="/?" goto :show_help
if "%~1"=="-v" goto :show_version
if "%~1"=="--version" goto :show_version
if "%~1"=="-y" set "JOI_YES=1" & shift & goto :parse_args
if "%~1"=="--yes" set "JOI_YES=1" & shift & goto :parse_args
if "%~1"=="--no-color" set "JOI_NO_COLOR=1" & shift & goto :parse_args
if "%~1"=="--verbose" set "JOI_VERBOSE=1" & shift & goto :parse_args
if "%~1"=="--quiet" set "JOI_QUIET=1" & shift & goto :parse_args

:: Unknown flag
if "%~1:~0,1%"=="-" (
    echo %C_RED%[ERROR]%C_RESET%  Unknown option: %~1
    echo   Run 'joi --help' for usage
    exit /b 2
)

set "COMMAND=%~1"
shift

:: Parse remaining flags for specific commands
:parse_command_args
if "%~1"=="" goto :after_parse
if "%~1"=="--seed" set "JOI_SEED_DATA=y" & shift & goto :parse_command_args
if "%~1"=="--no-seed" set "JOI_SEED_DATA=n" & shift & goto :parse_command_args
if "%~1"=="--admin" set "JOI_CREATE_ADMIN=y" & shift & goto :parse_command_args
if "%~1"=="--no-admin" set "JOI_CREATE_ADMIN=n" & shift & goto :parse_command_args
if "%~1"=="--skip-migrations" set "JOI_SKIP_MIGRATIONS=1" & shift & goto :parse_command_args
if "%~1"=="--clear" set "JOI_CLEAR=1" & shift & goto :parse_command_args
if "%~1"=="--port" set "JOI_PORT=%~2" & shift & shift & goto :parse_command_args
shift
goto :parse_command_args

:after_parse

if "%COMMAND%"=="" goto :show_help

:: Load config
if exist "%JOI_ENV_FILE%" call :load_config

:: Acquire lock for mutating commands
if "%COMMAND%"=="setup" call :acquire_lock
if "%COMMAND%"=="install" call :acquire_lock
if "%COMMAND%"=="migrate" call :acquire_lock
if "%COMMAND%"=="seed" call :acquire_lock
if "%COMMAND%"=="admin" call :acquire_lock
if "%COMMAND%"=="reset" call :acquire_lock

:: Dispatch
if "%COMMAND%"=="setup" goto :cmd_setup
if "%COMMAND%"=="install" goto :cmd_install
if "%COMMAND%"=="migrate" goto :cmd_migrate
if "%COMMAND%"=="seed" goto :cmd_seed
if "%COMMAND%"=="admin" goto :cmd_admin
if "%COMMAND%"=="server" goto :cmd_server
if "%COMMAND%"=="check" goto :cmd_check
if "%COMMAND%"=="reset" goto :cmd_reset
if "%COMMAND%"=="help" goto :show_help
if "%COMMAND%"=="version" goto :show_version

echo %C_RED%[ERROR]%C_RESET%  Unknown command: %COMMAND%
echo   Run 'joi --help' for usage
exit /b 2

:: =============================================================================
:: Config loading
:: =============================================================================
:load_config
for /f "usebackq tokens=1,* delims==" %%A in ("%JOI_ENV_FILE%") do (
    set "key=%%A"
    set "val=%%B"
    if not "!key:~0,1!"=="#" (
        if "!key!"=="SEED_DATA" if "!JOI_SEED_DATA!"=="y" set "JOI_SEED_DATA=!val!"
        if "!key!"=="CREATE_ADMIN" if "!JOI_CREATE_ADMIN!"=="n" set "JOI_CREATE_ADMIN=!val!"
        if "!key!"=="PORT" if "!JOI_PORT!"=="8000" set "JOI_PORT=!val!"
    )
)
goto :eof

:: =============================================================================
:: Lock file
:: =============================================================================
:acquire_lock
if exist "%JOI_LOCK_FILE%" (
    echo %C_YELLOW%[WARN]%C_RESET%  Lock file found, removing...
    del "%JOI_LOCK_FILE%" 2>nul
)
echo %RANDOM% > "%JOI_LOCK_FILE%"
goto :eof

:release_lock
del "%JOI_LOCK_FILE%" 2>nul
goto :eof

:: =============================================================================
:: Prompt helper
:: =============================================================================
:confirm
:: %1 = prompt, %2 = default (y/n)
:: Sets CONFIRM_RESULT=y or n
set "CONFIRM_RESULT=%~2"
if "%JOI_YES%"=="1" goto :eof
set /p "CONFIRM_ANSWER=  %C_YELLOW%[PROMPT]%C_RESET%  %~1 (y/n): "
if /i "%CONFIRM_ANSWER%"=="y" set "CONFIRM_RESULT=y"
if /i "%CONFIRM_ANSWER%"=="n" set "CONFIRM_RESULT=n"
goto :eof

:: =============================================================================
:: Find Python
:: =============================================================================
:find_python
if exist "%~dp0.venv\Scripts\python.exe" (
    set "PYTHON=%~dp0.venv\Scripts\python.exe"
) else (
    echo %C_RED%[ERROR]%C_RESET%  Python not found in .venv
    echo   Run 'joi install' first
    exit /b 3
)
goto :eof

:: =============================================================================
:: Help
:: =============================================================================
:show_help
echo.
echo   %C_BOLD%joi%C_RESET% - Project Development Tool
echo.
echo   USAGE:
echo     joi ^<command^> [options]
echo.
echo   COMMANDS:
echo     setup       Full project setup (install + migrate + seed + admin)
echo     install     Install dependencies (uv sync)
echo     migrate     Run database migrations
echo     seed        Seed database with fixtures
echo     admin       Create superuser
echo     server      Start Django dev server
echo     check       Check environment and dependencies
echo     reset       Reset database (drop + migrate + reseed)
echo     help        Show this help message
echo.
echo   GLOBAL OPTIONS:
echo     -h, --help        Show help
echo     -v, --version     Show version
echo     -y, --yes         Skip all confirmation prompts
echo     --no-color        Disable colored output
echo     --verbose         Show detailed output
echo     --quiet           Only show errors
echo.
echo   COMMAND-SPECIFIC OPTIONS:
echo     joi setup --seed / --no-seed        Control seeding
echo     joi setup --admin / --no-admin      Control admin creation
echo     joi setup --skip-migrations         Skip migrations
echo     joi seed --clear                    Clear then reseed
echo     joi server --port 8080              Custom port
echo.
echo   EXAMPLES:
echo     joi setup                 Interactive full setup
echo     joi setup -y --no-seed    Auto-setup, skip seeding
echo     joi install               Just install dependencies
echo     joi server --port 8080    Start server on port 8080
echo     joi check                 Diagnose environment
echo.
call :cleanup
exit /b 0

:show_version
echo joi v%JOI_VERSION%
call :cleanup
exit /b 0

:: =============================================================================
:: Command: check
:: =============================================================================
:cmd_check
echo.
echo   %C_BOLD%%JOI_NAME%%C_RESET% %C_DIM%v%JOI_VERSION%%C_RESET%  %C_DIM%-%C_RESET%  %JOI_DESC%
echo.

echo   %C_BOLD%%C_CYAN%[1/5]%C_RESET%  Checking uv
where uv >nul 2>nul
if %errorlevel% equ 0 (
    for /f "tokens=*" %%v in ('uv --version 2^>nul') do echo   %C_GREEN%[OK]%C_RESET%    %%v
) else (
    echo   %C_YELLOW%[WARN]%C_RESET%  uv not installed
)

echo.
echo   %C_BOLD%%C_CYAN%[2/5]%C_RESET%  Checking virtual environment
if exist "%~dp0.venv" (
    echo   %C_GREEN%[OK]%C_RESET%    .venv exists
) else (
    echo   %C_YELLOW%[WARN]%C_RESET%  .venv not found (run: joi install)
)

echo.
echo   %C_BOLD%%C_CYAN%[3/5]%C_RESET%  Checking database
if exist "%~dp0db.sqlite3" (
    for %%A in ("%~dp0db.sqlite3") do echo   %C_GREEN%[OK]%C_RESET%    db.sqlite3 (%%~zA bytes)
) else (
    echo   %C_YELLOW%[WARN]%C_RESET%  db.sqlite3 not found (run: joi migrate)
)

echo.
echo   %C_BOLD%%C_CYAN%[4/5]%C_RESET%  Checking fixtures
if exist "%~dp0fixtures" (
    set "count=0"
    for %%F in ("%~dp0fixtures\*.json") do set /a count+=1
    echo   %C_GREEN%[OK]%C_RESET%    fixtures/ (!count! files)
) else (
    echo   %C_YELLOW%[WARN]%C_RESET%  No fixtures/ directory found
)

echo.
echo   %C_BOLD%%C_CYAN%[5/5]%C_RESET%  Checking config
if exist "%JOI_ENV_FILE%" (
    echo   %C_GREEN%[OK]%C_RESET%    .joi.env exists
) else (
    echo   %C_CYAN%[INFO]%C_RESET%  No .joi.env (copy from .joi.env.example)
)

echo.
call :release_lock
exit /b 0

:: =============================================================================
:: Command: install
:: =============================================================================
:cmd_install
echo.
echo   %C_BOLD%%JOI_NAME%%C_RESET% %C_DIM%v%JOI_VERSION%%C_RESET%  %C_DIM%-%C_RESET%  %JOI_DESC%
echo.

echo   %C_BOLD%%C_CYAN%[1/2]%C_RESET%  Package manager
where uv >nul 2>nul
if %errorlevel% neq 0 (
    echo   %C_YELLOW%[WARN]%C_RESET%  uv is not installed. Installing...
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    set "PATH=%USERPROFILE%\.local\bin;%USERPROFILE%\.cargo\bin;%PATH%"
    echo   %C_GREEN%[OK]%C_RESET%    uv installed
) else (
    echo   %C_GREEN%[OK]%C_RESET%    uv is installed
)

echo.
echo   %C_BOLD%%C_CYAN%[2/2]%C_RESET%  Dependencies
if not exist "%~dp0.venv" (
    echo   %C_CYAN%[INFO]%C_RESET%  Creating virtual environment...
    call uv venv
)

:: Clean up Unix symlinks that break on Windows
if exist "%~dp0.venv\lib64" rmdir "%~dp0.venv\lib64" 2>nul
if exist "%~dp0.venv\lib64" del /f /q "%~dp0.venv\lib64" 2>nul

echo   %C_CYAN%[INFO]%C_RESET%  Running uv sync...
call uv sync
if %errorlevel% neq 0 (
    echo   %C_RED%[ERROR]%C_RESET%  uv sync failed
    call :release_lock
    exit /b 1
)
echo   %C_GREEN%[OK]%C_RESET%    Dependencies installed

echo.
call :release_lock
exit /b 0

:: =============================================================================
:: Command: migrate
:: =============================================================================
:cmd_migrate
echo.
echo   %C_BOLD%%JOI_NAME%%C_RESET% %C_DIM%v%JOI_VERSION%%C_RESET%  %C_DIM%-%C_RESET%  %JOI_DESC%
echo.

call :find_python
if %errorlevel% neq 0 exit /b 3

echo   %C_BOLD%%C_CYAN%[1/2]%C_RESET%  makemigrations
echo   %C_CYAN%[INFO]%C_RESET%  Detecting model changes...
%PYTHON% manage.py makemigrations
echo   %C_GREEN%[OK]%C_RESET%    Migrations created

echo.
echo   %C_BOLD%%C_CYAN%[2/2]%C_RESET%  migrate
echo   %C_CYAN%[INFO]%C_RESET%  Applying migrations...
%PYTHON% manage.py migrate
echo   %C_GREEN%[OK]%C_RESET%    Database migrations applied

echo.
call :release_lock
exit /b 0

:: =============================================================================
:: Command: seed
:: =============================================================================
:cmd_seed
echo.
echo   %C_BOLD%%JOI_NAME%%C_RESET% %C_DIM%v%JOI_VERSION%%C_RESET%  %C_DIM%-%C_RESET%  %JOI_DESC%
echo.

call :find_python
if %errorlevel% neq 0 exit /b 3

if "%JOI_CLEAR%"=="1" (
    echo   %C_YELLOW%[WARN]%C_RESET%  This will delete all data from the database
    call :confirm "Are you sure?" "n"
    if "!CONFIRM_RESULT!"=="y" (
        echo   %C_CYAN%[INFO]%C_RESET%  Clearing database...
        %PYTHON% manage.py load_data --clear
        echo   %C_GREEN%[OK]%C_RESET%    Database cleared and reseeded
    ) else (
        echo   %C_CYAN%[INFO]%C_RESET%  Cancelled
    )
    call :release_lock
    exit /b 0
)

if exist "%~dp0fixtures" (
    echo   %C_CYAN%[INFO]%C_RESET%  Loading fixtures...
    %PYTHON% manage.py load_data
    if %errorlevel% neq 0 (
        echo   %C_RED%[ERROR]%C_RESET%  Seeding failed
        call :release_lock
        exit /b 1
    )
    echo   %C_GREEN%[OK]%C_RESET%    Database seeded
) else if exist "%~dp0data_seeding.sql" (
    echo   %C_YELLOW%[WARN]%C_RESET%  fixtures/ not found, falling back to data_seeding.sql
    echo   %C_CYAN%[INFO]%C_RESET%  Loading data_seeding.sql...
    %PYTHON% seed_db.py
    if %errorlevel% neq 0 (
        echo   %C_RED%[ERROR]%C_RESET%  Seeding failed
        call :release_lock
        exit /b 1
    )
    echo   %C_GREEN%[OK]%C_RESET%    Database seeded
) else (
    echo   %C_RED%[ERROR]%C_RESET%  No fixtures/ directory or data_seeding.sql found
    call :release_lock
    exit /b 1
)

echo.
call :release_lock
exit /b 0

:: =============================================================================
:: Command: admin
:: =============================================================================
:cmd_admin
echo.
echo   %C_BOLD%%JOI_NAME%%C_RESET% %C_DIM%v%JOI_VERSION%%C_RESET%  %C_DIM%-%C_RESET%  %JOI_DESC%
echo.

call :find_python
if %errorlevel% neq 0 exit /b 3

echo   %C_CYAN%[INFO]%C_RESET%  Starting superuser creation...
%PYTHON% manage.py createsuperuser

echo.
call :release_lock
exit /b 0

:: =============================================================================
:: Command: server
:: =============================================================================
:cmd_server
echo.
echo   %C_BOLD%%JOI_NAME%%C_RESET% %C_DIM%v%JOI_VERSION%%C_RESET%  %C_DIM%-%C_RESET%  %JOI_DESC%
echo.

call :find_python
if %errorlevel% neq 0 exit /b 3

echo.
echo   %C_BOLD%%C_CYAN%Starting Django development server on port %JOI_PORT%%C_RESET%
echo   %C_DIM%Press Ctrl+C to stop%C_RESET%
echo.
%PYTHON% manage.py runserver 127.0.0.1:%JOI_PORT%

call :release_lock
exit /b 0

:: =============================================================================
:: Command: reset
:: =============================================================================
:cmd_reset
echo.
echo   %C_BOLD%%JOI_NAME%%C_RESET% %C_DIM%v%JOI_VERSION%%C_RESET%  %C_DIM%-%C_RESET%  %JOI_DESC%
echo.

call :find_python
if %errorlevel% neq 0 exit /b 3

echo   %C_YELLOW%[WARN]%C_RESET%  This will delete the database and all data
call :confirm "Continue?" "n"
if "!CONFIRM_RESULT!" neq "y" (
    echo   %C_CYAN%[INFO]%C_RESET%  Cancelled
    call :release_lock
    exit /b 0
)

echo.
echo   %C_BOLD%%C_CYAN%[1/3]%C_RESET%  Removing database
if exist "%~dp0db.sqlite3" (
    del "%~dp0db.sqlite3"
    echo   %C_GREEN%[OK]%C_RESET%    db.sqlite3 removed
) else (
    echo   %C_CYAN%[INFO]%C_RESET%  No database file found
)

echo.
echo   %C_BOLD%%C_CYAN%[2/3]%C_RESET%  Running migrations
%PYTHON% manage.py makemigrations
%PYTHON% manage.py migrate
echo   %C_GREEN%[OK]%C_RESET%    Database recreated

echo.
echo   %C_BOLD%%C_CYAN%[3/3]%C_RESET%  Reseeding
call :confirm "Seed the database?" "y"
if "!CONFIRM_RESULT!"=="y" (
    set "JOI_YES=1"
    set "JOI_CLEAR="
    goto :cmd_seed
)

echo.
call :release_lock
exit /b 0

:: =============================================================================
:: Command: setup (full setup flow)
:: =============================================================================
:cmd_setup
echo.
echo   %C_BOLD%%JOI_NAME%%C_RESET% %C_DIM%v%JOI_VERSION%%C_RESET%  %C_DIM%-%C_RESET%  %JOI_DESC%
echo.

:: Step 1: uv
echo   %C_BOLD%%C_CYAN%[1/6]%C_RESET%  Package manager
where uv >nul 2>nul
if %errorlevel% neq 0 (
    echo   %C_YELLOW%[WARN]%C_RESET%  uv is not installed. Installing...
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    set "PATH=%USERPROFILE%\.local\bin;%USERPROFILE%\.cargo\bin;%PATH%"
    echo   %C_GREEN%[OK]%C_RESET%    uv installed
) else (
    echo   %C_GREEN%[OK]%C_RESET%    uv is installed
)

:: Step 2: venv
echo.
echo   %C_BOLD%%C_CYAN%[2/6]%C_RESET%  Virtual environment
if not exist "%~dp0.venv" (
    echo   %C_CYAN%[INFO]%C_RESET%  Creating virtual environment...
    call uv venv
    echo   %C_GREEN%[OK]%C_RESET%    Virtual environment created
) else (
    echo   %C_GREEN%[OK]%C_RESET%    .venv exists
)

:: Step 3: dependencies
echo.
echo   %C_BOLD%%C_CYAN%[3/6]%C_RESET%  Dependencies
:: Clean up Unix symlinks that break on Windows
if exist "%~dp0.venv\lib64" rmdir "%~dp0.venv\lib64" 2>nul
if exist "%~dp0.venv\lib64" del /f /q "%~dp0.venv\lib64" 2>nul
echo   %C_CYAN%[INFO]%C_RESET%  Running uv sync...
call uv sync
if %errorlevel% neq 0 (
    echo   %C_RED%[ERROR]%C_RESET%  uv sync failed
    call :release_lock
    exit /b 1
)
echo   %C_GREEN%[OK]%C_RESET%    Dependencies installed

set "PYTHON=%~dp0.venv\Scripts\python.exe"

:: Step 4: migrations
if not defined JOI_SKIP_MIGRATIONS set "JOI_SKIP_MIGRATIONS=0"
echo.
if "%JOI_SKIP_MIGRATIONS%"=="0" (
    echo   %C_BOLD%%C_CYAN%[4/6]%C_RESET%  Database migrations
    echo   %C_CYAN%[INFO]%C_RESET%  Running makemigrations...
    %PYTHON% manage.py makemigrations
    echo   %C_CYAN%[INFO]%C_RESET%  Running migrate...
    %PYTHON% manage.py migrate
    echo   %C_GREEN%[OK]%C_RESET%    Database migrations applied
) else (
    echo   %C_BOLD%%C_CYAN%[4/6]%C_RESET%  Database migrations
    echo   %C_CYAN%[INFO]%C_RESET%  Skipped (--skip-migrations)
)

:: Step 5: admin
echo.
echo   %C_BOLD%%C_CYAN%[5/6]%C_RESET%  Admin user
if "%JOI_CREATE_ADMIN%"=="y" (
    %PYTHON% manage.py createsuperuser
    echo   %C_GREEN%[OK]%C_RESET%    Admin user created
) else (
    call :confirm "Create an admin user?" "n"
    if "!CONFIRM_RESULT!"=="y" (
        %PYTHON% manage.py createsuperuser
        echo   %C_GREEN%[OK]%C_RESET%    Admin user created
    ) else (
        echo   %C_CYAN%[INFO]%C_RESET%  Skipped admin creation
    )
)

:: Step 6: seed
echo.
echo   %C_BOLD%%C_CYAN%[6/6]%C_RESET%  Seed database
if "%JOI_SEED_DATA%"=="y" (
    if exist "%~dp0fixtures" (
        echo   %C_CYAN%[INFO]%C_RESET%  Loading fixtures...
        %PYTHON% manage.py load_data
        echo   %C_GREEN%[OK]%C_RESET%    Database seeded
    ) else if exist "%~dp0data_seeding.sql" (
        echo   %C_YELLOW%[WARN]%C_RESET%  fixtures/ not found, falling back to data_seeding.sql
        %PYTHON% seed_db.py
        echo   %C_GREEN%[OK]%C_RESET%    Database seeded
    ) else (
        echo   %C_RED%[ERROR]%C_RESET%  No seed data found
    )
) else (
    call :confirm "Seed fake data into the database?" "n"
    if "!CONFIRM_RESULT!"=="y" (
        if exist "%~dp0fixtures" (
            %PYTHON% manage.py load_data
            echo   %C_GREEN%[OK]%C_RESET%    Database seeded
        ) else if exist "%~dp0data_seeding.sql" (
            %PYTHON% seed_db.py
            echo   %C_GREEN%[OK]%C_RESET%    Database seeded
        )
    ) else (
        echo   %C_CYAN%[INFO]%C_RESET%  Skipped data seeding
    )
)

:: Summary
echo.
echo   %C_GREEN%%C_BOLD%[OK]  Setup complete!%C_RESET%
echo.
echo   %C_DIM%Next steps:%C_RESET%
echo     %C_WHITE%joi server%C_RESET%        Start the dev server
echo     %C_WHITE%joi admin%C_RESET%         Create an admin user
echo.

call :release_lock
exit /b 0
