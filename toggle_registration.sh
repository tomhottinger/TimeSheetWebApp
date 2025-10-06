#!/bin/bash



# toggle_registration.sh

# Script zum einfachen Aktivieren/Deaktivieren der Registrierung



ENV_FILE=".env"

CONTAINER_NAME="timesheet-app"



# Farben für Output

GREEN='\033[0;32m'

RED='\033[0;31m'

YELLOW='\033[1;33m'

NC='\033[0m' # No Color



echo ""

echo "=========================================="

echo " 🔐 Registrierungs-Kontrolle"

echo "=========================================="

echo ""



# Funktion: Aktuellen Status ermitteln

get_current_status() {

    if [ -f "$ENV_FILE" ]; then

        if grep -q "^ALLOW_REGISTRATION=false" "$ENV_FILE"; then

            echo "disabled"

        elif grep -q "^ALLOW_REGISTRATION=true" "$ENV_FILE"; then

            echo "enabled"

        else

            echo "not_set"

        fi

    else

        echo "no_env_file"

    fi

}



# Funktion: Status anzeigen

show_status() {

    local status=$(get_current_status)

    

    echo "Aktueller Status:"

    case $status in

        "enabled")

            echo -e "  ${GREEN}✅ Registrierung ist AKTIVIERT${NC}"

            echo "  → Neue User können sich selbst registrieren"

            ;;

        "disabled")

            echo -e "  ${RED}🔒 Registrierung ist DEAKTIVIERT${NC}"

            echo "  → Nur Admin kann neue User anlegen"

            ;;

        "not_set")

            echo -e "  ${YELLOW}⚠️  Status nicht gesetzt (Standard: AKTIVIERT)${NC}"

            echo "  → Registrierung ist momentan erlaubt"

            ;;

        "no_env_file")

            echo -e "  ${RED}❌ .env Datei nicht gefunden${NC}"

            echo "  → Erstelle zuerst eine .env Datei"

            ;;

    esac

    echo ""

}



# Funktion: Registrierung aktivieren

enable_registration() {

    echo "🔓 Aktiviere Registrierung..."

    

    # .env Datei existiert?

    if [ ! -f "$ENV_FILE" ]; then

        echo "ALLOW_REGISTRATION=true" > "$ENV_FILE"

        echo -e "${GREEN}✅ .env erstellt und Registrierung aktiviert${NC}"

    else

        # Zeile existiert bereits?

        if grep -q "^ALLOW_REGISTRATION=" "$ENV_FILE"; then

            # Zeile ersetzen

            if [[ "$OSTYPE" == "darwin"* ]]; then

                # macOS

                sed -i '' 's/^ALLOW_REGISTRATION=.*/ALLOW_REGISTRATION=true/' "$ENV_FILE"

            else

                # Linux

                sed -i 's/^ALLOW_REGISTRATION=.*/ALLOW_REGISTRATION=true/' "$ENV_FILE"

            fi

            echo -e "${GREEN}✅ Registrierung aktiviert${NC}"

        else

            # Zeile hinzufügen

            echo "ALLOW_REGISTRATION=true" >> "$ENV_FILE"

            echo -e "${GREEN}✅ Registrierung aktiviert${NC}"

        fi

    fi

    

    restart_container

}



# Funktion: Registrierung deaktivieren

disable_registration() {

    echo "🔒 Deaktiviere Registrierung..."

    

    # .env Datei existiert?

    if [ ! -f "$ENV_FILE" ]; then

        echo "ALLOW_REGISTRATION=false" > "$ENV_FILE"

        echo -e "${GREEN}✅ .env erstellt und Registrierung deaktiviert${NC}"

    else

        # Zeile existiert bereits?

        if grep -q "^ALLOW_REGISTRATION=" "$ENV_FILE"; then

            # Zeile ersetzen

            if [[ "$OSTYPE" == "darwin"* ]]; then

                # macOS

                sed -i '' 's/^ALLOW_REGISTRATION=.*/ALLOW_REGISTRATION=false/' "$ENV_FILE"

            else

                # Linux

                sed -i 's/^ALLOW_REGISTRATION=.*/ALLOW_REGISTRATION=false/' "$ENV_FILE"

            fi

            echo -e "${GREEN}✅ Registrierung deaktiviert${NC}"

        else

            # Zeile hinzufügen

            echo "ALLOW_REGISTRATION=false" >> "$ENV_FILE"

            echo -e "${GREEN}✅ Registrierung deaktiviert${NC}"

        fi

    fi

    

    restart_container

}



# Funktion: Container neu starten

restart_container() {

    echo ""

    echo "🔄 Container wird neu gestartet..."

    

    if docker ps | grep -q "$CONTAINER_NAME"; then

        docker compose restart

        

        if [ $? -eq 0 ]; then

            echo -e "${GREEN}✅ Container neu gestartet${NC}"

            echo ""

            echo "ℹ️  Änderung ist jetzt aktiv!"

            echo "   Teste die Login-Seite in deinem Browser"

        else

            echo -e "${RED}❌ Fehler beim Neustarten${NC}"

            echo "   Versuche manuell: docker-compose restart"

        fi

    else

        echo -e "${YELLOW}⚠️  Container läuft nicht${NC}"

        echo "   Starte mit: docker-compose up -d"

    fi

}



# Hauptmenü

show_status



echo "Was möchtest du tun?"

echo "  1) Registrierung AKTIVIEREN"

echo "  2) Registrierung DEAKTIVIEREN"

echo "  3) Nur Status anzeigen"

echo "  4) Container neu starten"

echo "  5) Beenden"

echo ""

read -p "Wahl (1-5): " choice



case $choice in

    1)

        echo ""

        enable_registration

        echo ""

        show_status

        ;;

    2)

        echo ""

        disable_registration

        echo ""

        show_status

        ;;

    3)

        # Status wird schon oben angezeigt

        ;;

    4)

        echo ""

        restart_container

        ;;

    5)

        echo ""

        echo "👋 Tschüss!"

        echo ""

        exit 0

        ;;

    *)

        echo ""

        echo -e "${RED}❌ Ungültige Auswahl${NC}"

        echo ""

        exit 1

        ;;

esac



echo ""

echo "=========================================="

echo ""
