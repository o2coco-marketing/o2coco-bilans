@echo off
chcp 65001 >nul
cd /d "%~dp0"

where python >nul 2>&1
if errorlevel 1 (
    echo.
    echo ============================================================
    echo  Python n'est pas installé sur cet ordinateur.
    echo  Installez-le depuis https://www.python.org/downloads/
    echo  ^(cochez bien la case "Add python.exe to PATH" pendant l'installation^)
    echo  puis relancez ce fichier.
    echo ============================================================
    echo.
    pause
    exit /b 1
)

if not exist venv\Scripts\activate.bat (
    echo Premier démarrage : installation en cours, merci de patienter quelques minutes...
    python -m venv venv
)

call venv\Scripts\activate.bat

echo Vérification des composants nécessaires...
pip install -r requirements.txt --quiet --disable-pip-version-check
if errorlevel 1 (
    echo.
    echo Une erreur est survenue pendant l'installation. Vérifiez votre connexion internet et réessayez.
    pause
    exit /b 1
)

echo Lancement de l'application, votre navigateur va s'ouvrir automatiquement...
streamlit run app.py

if errorlevel 1 (
    echo.
    echo L'application s'est arrêtée de manière inattendue.
    pause
)
