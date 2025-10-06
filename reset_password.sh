#!/bin/bash



# reset_password.sh

# Wrapper-Script um das Passwort Reset Tool im Docker Container auszuführen



CONTAINER_NAME="timesheet-app"

SCRIPT_PATH="/app/reset_password.py"



# Prüfen ob Container läuft

if ! docker ps | grep -q $CONTAINER_NAME; then

    echo "❌ Container '$CONTAINER_NAME' läuft nicht!"

    echo "   Starte mit: docker-compose up -d"

    exit 1

fi



# Prüfen ob Reset-Script im Container existiert

if ! docker exec $CONTAINER_NAME test -f $SCRIPT_PATH 2>/dev/null; then

    echo "⚠️  Reset-Script nicht im Container gefunden."

    echo "   Kopiere Script in Container..."

    docker cp reset_password.py $CONTAINER_NAME:$SCRIPT_PATH

    docker exec $CONTAINER_NAME chmod +x $SCRIPT_PATH

    echo "   ✅ Script kopiert!"

fi



# Script im Container ausführen

docker exec -it $CONTAINER_NAME python $SCRIPT_PATH "$@"
