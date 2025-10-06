#!/usr/bin/env python3

"""

Passwort Reset Tool für Timesheet App



Ermöglicht das Zurücksetzen von Benutzer-Passwörtern von außen

(z.B. wenn ein User sein Passwort vergessen hat)

"""



import sqlite3

import sys

import os

from werkzeug.security import generate_password_hash



# Verwende die gleiche Datenbank wie die App

DATABASE = os.environ.get('DATABASE_PATH', '/app/data/timesheet.db')



def connect_db():

    """Verbindung zur Datenbank herstellen."""

    return sqlite3.connect(DATABASE)



def list_users():

    """Alle Benutzer auflisten."""

    conn = connect_db()

    cursor = conn.cursor()

    

    cursor.execute('''

        SELECT u.id, u.username, u.created_at

        FROM users u

        ORDER BY u.username

    ''')

    

    users = cursor.fetchall()

    conn.close()

    

    print("\n" + "="*60)

    print("VERFÜGBARE BENUTZER:")

    print("="*60)

    print(f"{'ID':<5} {'Username':<30} {'Erstellt':<20}")

    print("-"*60)

    

    for user in users:

        user_id, username, created = user

        print(f"{user_id:<5} {username:<30} {created[:10]:<20}")

    

    print("="*60 + "\n")

    return users



def reset_password(user_id, new_password):

    """

    Passwort für einen User zurücksetzen.

    

    Args:

        user_id: ID des Users

        new_password: Neues Passwort (wird automatisch gehashed)

    

    Returns:

        True bei Erfolg, False bei Fehler

    """

    conn = connect_db()

    cursor = conn.cursor()

    

    try:

        # Prüfen ob User existiert

        cursor.execute('SELECT id, username FROM users WHERE id = ?', (user_id,))

        user = cursor.fetchone()

        

        if not user:

            print(f"❌ User ID {user_id} nicht gefunden!")

            return False

        

        # Passwort hashen

        password_hash = generate_password_hash(new_password)

        

        # Passwort in Datenbank aktualisieren

        cursor.execute('''

            UPDATE users SET password_hash = ? WHERE id = ?

        ''', (password_hash, user_id))

        

        conn.commit()

        print(f"\n✅ Passwort für '{user[1]}' (ID: {user_id}) erfolgreich geändert!")

        print(f"   Neues Passwort: {new_password}\n")

        return True

        

    except Exception as e:

        conn.rollback()

        print(f"\n❌ Fehler beim Zurücksetzen des Passworts: {e}\n")

        return False

    finally:

        conn.close()



def reset_password_by_username(username, new_password):

    """

    Passwort für einen User zurücksetzen (via Username).

    

    Args:

        username: Username des Users

        new_password: Neues Passwort (wird automatisch gehashed)

    

    Returns:

        True bei Erfolg, False bei Fehler

    """

    conn = connect_db()

    cursor = conn.cursor()

    

    try:

        # User-ID finden

        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))

        user = cursor.fetchone()

        

        if not user:

            print(f"❌ User '{username}' nicht gefunden!")

            return False

        

        user_id = user[0]

        

        # Passwort hashen

        password_hash = generate_password_hash(new_password)

        

        # Passwort in Datenbank aktualisieren

        cursor.execute('''

            UPDATE users SET password_hash = ? WHERE id = ?

        ''', (password_hash, user_id))

        

        conn.commit()

        print(f"\n✅ Passwort für '{username}' (ID: {user_id}) erfolgreich geändert!")

        print(f"   Neues Passwort: {new_password}\n")

        return True

        

    except Exception as e:

        conn.rollback()

        print(f"\n❌ Fehler beim Zurücksetzen des Passworts: {e}\n")

        return False

    finally:

        conn.close()



def set_default_password_for_all():

    """Setzt für ALLE User das Passwort auf 'password' zurück."""

    conn = connect_db()

    cursor = conn.cursor()

    

    try:

        # Alle User holen

        cursor.execute('SELECT id, username FROM users')

        users = cursor.fetchall()

        

        if not users:

            print("❌ Keine User gefunden!")

            return False

        

        print(f"\n⚠️  WARNUNG: Dies setzt das Passwort für {len(users)} User auf 'password' zurück!")

        print("   Betroffen sind:")

        for user in users:

            print(f"   - {user[1]} (ID: {user[0]})")

        

        confirm = input("\n   Wirklich fortfahren? (ja/nein): ").strip().lower()

        

        if confirm not in ['ja', 'j', 'yes', 'y']:

            print("❌ Abgebrochen.")

            return False

        

        # Standard-Passwort hashen

        password_hash = generate_password_hash('password')

        

        # Für alle User setzen

        cursor.execute('UPDATE users SET password_hash = ?', (password_hash,))

        

        conn.commit()

        print(f"\n✅ Passwort für {len(users)} User auf 'password' zurückgesetzt!\n")

        return True

        

    except Exception as e:

        conn.rollback()

        print(f"\n❌ Fehler: {e}\n")

        return False

    finally:

        conn.close()



def interactive_mode():

    """Interaktiver Modus für einfache Bedienung."""

    print("\n" + "="*60)

    print(" 🔐 PASSWORT RESET TOOL")

    print("="*60)

    

    while True:

        print("\nWas möchten Sie tun?")

        print("  1) Benutzer auflisten")

        print("  2) Passwort zurücksetzen (via User-ID)")

        print("  3) Passwort zurücksetzen (via Username)")

        print("  4) Alle Passwörter auf 'password' setzen")

        print("  5) Beenden")

        

        choice = input("\nWahl (1-5): ").strip()

        

        if choice == '1':

            list_users()

            

        elif choice == '2':

            list_users()

            try:

                user_id = int(input("User ID: ").strip())

                new_password = input("Neues Passwort: ").strip()

                

                if len(new_password) < 6:

                    print("❌ Passwort muss mindestens 6 Zeichen lang sein!")

                    continue

                

                confirm = input(f"Passwort wirklich ändern? (ja/nein): ").strip().lower()

                if confirm in ['ja', 'j', 'yes', 'y']:

                    reset_password(user_id, new_password)

                else:

                    print("❌ Abgebrochen.")

                    

            except ValueError:

                print("❌ Ungültige ID!")

                

        elif choice == '3':

            list_users()

            username = input("Username: ").strip()

            new_password = input("Neues Passwort: ").strip()

            

            if len(new_password) < 6:

                print("❌ Passwort muss mindestens 6 Zeichen lang sein!")

                continue

            

            confirm = input(f"Passwort für '{username}' wirklich ändern? (ja/nein): ").strip().lower()

            if confirm in ['ja', 'j', 'yes', 'y']:

                reset_password_by_username(username, new_password)

            else:

                print("❌ Abgebrochen.")

                

        elif choice == '4':

            set_default_password_for_all()

            

        elif choice == '5':

            print("\n👋 Auf Wiedersehen!\n")

            break

            

        else:

            print("❌ Ungültige Auswahl!")



def main():

    """Hauptfunktion mit Command-Line Argumenten."""

    if len(sys.argv) == 1:

        # Kein Argument = Interaktiver Modus

        interactive_mode()

        

    elif sys.argv[1] == 'list':

        list_users()

        

    elif sys.argv[1] == 'reset-id' and len(sys.argv) == 4:

        user_id = int(sys.argv[2])

        new_password = sys.argv[3]

        if len(new_password) < 6:

            print("❌ Passwort muss mindestens 6 Zeichen lang sein!")

            sys.exit(1)

        reset_password(user_id, new_password)

        

    elif sys.argv[1] == 'reset-user' and len(sys.argv) == 4:

        username = sys.argv[2]

        new_password = sys.argv[3]

        if len(new_password) < 6:

            print("❌ Passwort muss mindestens 6 Zeichen lang sein!")

            sys.exit(1)

        reset_password_by_username(username, new_password)

        

    elif sys.argv[1] == 'reset-all':

        set_default_password_for_all()

        

    else:

        print("\n📖 VERWENDUNG:")

        print("="*60)

        print("Interaktiver Modus (empfohlen):")

        print("  python reset_password.py")

        print("\nDirekte Kommandos:")

        print("  python reset_password.py list")

        print("  python reset_password.py reset-id <user_id> <neues_passwort>")

        print("  python reset_password.py reset-user <username> <neues_passwort>")

        print("  python reset_password.py reset-all")

        print("\nBeispiele:")

        print("  python reset_password.py reset-id 1 neupass123")

        print("  python reset_password.py reset-user tom MeinPass456")

        print("="*60 + "\n")



if __name__ == '__main__':

    main()
