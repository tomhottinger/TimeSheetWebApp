from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from datetime import datetime, timedelta
import sqlite3
import os
import json
from dataclasses import dataclass
from typing import List, Optional
import uuid
from collections import defaultdict
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')

# Use environment variable for database path, fallback to local
DATABASE = os.environ.get('DATABASE_PATH', 'timesheet.db')

# REGISTRATION CONTROL - Set to False to disable new registrations
ALLOW_REGISTRATION = os.environ.get('ALLOW_REGISTRATION', 'true').lower() == 'true'

def init_database():
    """Initialize the SQLite database with required tables."""
    # Ensure directory exists
    db_dir = os.path.dirname(DATABASE)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Users table - now with password hash
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Check if password_hash column exists, add if not (for migration)
    cursor.execute('PRAGMA table_info(users)')
    columns = [column[1] for column in cursor.fetchall()]
    if 'password_hash' not in columns:
        cursor.execute('ALTER TABLE users ADD COLUMN password_hash TEXT')
        # Set default password for existing users (password: "password")
        default_hash = generate_password_hash('password')
        cursor.execute('UPDATE users SET password_hash = ? WHERE password_hash IS NULL', (default_hash,))
    
    # Tickets table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            id TEXT PRIMARY KEY,
            user_id INTEGER,
            name TEXT NOT NULL,
            color TEXT NOT NULL,
            jira_ticket TEXT DEFAULT '',
            matrix_ticket TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Add sort_order column to tickets table if it doesn't exist
    cursor.execute('PRAGMA table_info(tickets)')
    columns = [column[1] for column in cursor.fetchall()]
    if 'sort_order' not in columns:
        cursor.execute('ALTER TABLE tickets ADD COLUMN sort_order INTEGER DEFAULT 0')
    
    # Add archived column to tickets table if it doesn't exist
    if 'archived' not in columns:
        cursor.execute('ALTER TABLE tickets ADD COLUMN archived INTEGER DEFAULT 0')
    
    # Add archived_at column to tickets table if it doesn't exist
    if 'archived_at' not in columns:
        cursor.execute('ALTER TABLE tickets ADD COLUMN archived_at TIMESTAMP')
    
    # User ticket order preferences table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_ticket_order (
            user_id INTEGER PRIMARY KEY,
            ticket_order TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Time entries table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS time_entries (
            id TEXT PRIMARY KEY,
            user_id INTEGER,
            ticket_name TEXT NOT NULL,
            start_time TIMESTAMP NOT NULL,
            end_time TIMESTAMP,
            memo TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Current running entry tracking
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS current_entries (
            user_id INTEGER PRIMARY KEY,
            entry_id TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (entry_id) REFERENCES time_entries (id)
        )
    ''')
    
    # Create demo user with password "demo123" if no users exist
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        demo_hash = generate_password_hash('demo123')
        cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', 
                      ('demoUser', demo_hash))
    
    conn.commit()
    conn.close()

@dataclass
class User:
    id: int
    username: str

@dataclass
class TimeEntry:
    id: str
    user_id: int
    ticket_name: str
    start_time: str
    end_time: Optional[str]
    memo: str = ""
    
@dataclass
class Ticket:
    id: str
    user_id: int
    name: str
    color: str
    jira_ticket: str = ""
    matrix_ticket: str = ""

class TimesheetManager:
    def __init__(self):
        init_database()
    
    def authenticate_user(self, username: str, password: str):
        """Authenticate user with username and password."""
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, password_hash FROM users WHERE username = ?', (username,))
        row = cursor.fetchone()
        conn.close()
        
        if row and check_password_hash(row[2], password):
            return User(id=row[0], username=row[1])
        return None
    
    def get_users(self):
        """Get all users."""
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT id, username FROM users ORDER BY username')
        users = [User(id=row[0], username=row[1]) for row in cursor.fetchall()]
        conn.close()
        return users
    
    def get_user_by_id(self, user_id: int):
        """Get user by ID."""
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT id, username FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        return User(id=row[0], username=row[1]) if row else None
    
    def add_user(self, username: str, password: str):
        """Add a new user with password."""
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        try:
            password_hash = generate_password_hash(password)
            cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', 
                         (username, password_hash))
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return user_id
        except sqlite3.IntegrityError:
            conn.close()
            return None  # Username already exists
    
    def change_password(self, user_id: int, new_password: str):
        """Change user password."""
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        password_hash = generate_password_hash(new_password)
        cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?', 
                      (password_hash, user_id))
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
    
    def get_tickets(self, user_id: int, include_archived: bool = False):
        """Get all tickets for a specific user in the correct order."""
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # First, get the user's custom order if it exists
        cursor.execute('SELECT ticket_order FROM user_ticket_order WHERE user_id = ?', (user_id,))
        order_row = cursor.fetchone()
        custom_order = json.loads(order_row[0]) if order_row and order_row[0] else []
        
        # Get all tickets (archived or not based on parameter)
        if include_archived:
            cursor.execute('''
                SELECT id, user_id, name, color, jira_ticket, matrix_ticket, archived, archived_at
                FROM tickets WHERE user_id = ?
            ''', (user_id,))
        else:
            cursor.execute('''
                SELECT id, user_id, name, color, jira_ticket, matrix_ticket, archived, archived_at
                FROM tickets WHERE user_id = ? AND (archived = 0 OR archived IS NULL)
            ''', (user_id,))
        
        all_tickets = {}
        for row in cursor.fetchall():
            ticket = Ticket(
                id=row[0], user_id=row[1], name=row[2], color=row[3],
                jira_ticket=row[4], matrix_ticket=row[5]
            )
            all_tickets[ticket.id] = ticket
        
        conn.close()
        
        # Sort tickets according to custom order, then alphabetically for new ones
        ordered_tickets = []
        
        # First, add tickets in custom order
        for ticket_id in custom_order:
            if ticket_id in all_tickets:
                ordered_tickets.append(all_tickets[ticket_id])
                del all_tickets[ticket_id]
        
        # Then add any remaining tickets alphabetically
        remaining_tickets = sorted(all_tickets.values(), key=lambda t: t.name)
        ordered_tickets.extend(remaining_tickets)
        
        return ordered_tickets
    
    def get_archived_tickets(self, user_id: int):
        """Get archived tickets for a user."""
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, user_id, name, color, jira_ticket, matrix_ticket
            FROM tickets 
            WHERE user_id = ? AND archived = 1
            ORDER BY name
        ''', (user_id,))
        
        archived_tickets = []
        for row in cursor.fetchall():
            archived_tickets.append(Ticket(
                id=row[0], user_id=row[1], name=row[2], color=row[3],
                jira_ticket=row[4], matrix_ticket=row[5]
            ))
        conn.close()
        return archived_tickets
    
    def archive_ticket(self, user_id: int, ticket_id: str):
        """Archive a ticket instead of deleting it."""
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE tickets 
            SET archived = 1, archived_at = ?
            WHERE id = ? AND user_id = ?
        ''', (datetime.now().isoformat(), ticket_id, user_id))
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
    
    def restore_ticket(self, user_id: int, ticket_id: str):
        """Restore an archived ticket."""
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE tickets 
            SET archived = 0, archived_at = NULL
            WHERE id = ? AND user_id = ?
        ''', (ticket_id, user_id))
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
    
    def cleanup_old_archived_tickets(self, user_id: int):
        """Delete archived tickets with no entries in the last month."""
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        one_month_ago = (datetime.now() - timedelta(days=30)).isoformat()
        
        # Find archived tickets
        cursor.execute('''
            SELECT id, name FROM tickets 
            WHERE user_id = ? AND archived = 1
        ''', (user_id,))
        
        archived_tickets = cursor.fetchall()
        deleted_count = 0
        
        for ticket_id, ticket_name in archived_tickets:
            # Check if there are any entries in the last month
            cursor.execute('''
                SELECT COUNT(*) FROM time_entries
                WHERE user_id = ? AND ticket_name = ? AND start_time >= ?
            ''', (user_id, ticket_name, one_month_ago))
            
            count = cursor.fetchone()[0]
            
            if count == 0:
                # No entries in last month, safe to delete
                cursor.execute('DELETE FROM tickets WHERE id = ? AND user_id = ?', 
                             (ticket_id, user_id))
                deleted_count += 1
        
        conn.commit()
        conn.close()
        return deleted_count
    
    def save_ticket_order(self, user_id: int, ticket_order: List[str]):
        """Save the user's custom ticket order."""
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        order_json = json.dumps(ticket_order)
        cursor.execute('''
            INSERT OR REPLACE INTO user_ticket_order (user_id, ticket_order, updated_at)
            VALUES (?, ?, ?)
        ''', (user_id, order_json, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        return True
    
    def get_ticket_by_id(self, user_id: int, ticket_id: str):
        """Get a specific ticket by ID for a user."""
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, user_id, name, color, jira_ticket, matrix_ticket 
            FROM tickets WHERE id = ? AND user_id = ?
        ''', (ticket_id, user_id))
        row = cursor.fetchone()
        conn.close()
        if row:
            return Ticket(
                id=row[0], user_id=row[1], name=row[2], color=row[3],
                jira_ticket=row[4], matrix_ticket=row[5]
            )
        return None
    
    def add_ticket(self, user_id: int, name: str, color: str, jira_ticket: str = "", matrix_ticket: str = ""):
        """Add a new ticket for a user."""
        ticket_id = str(uuid.uuid4())
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO tickets (id, user_id, name, color, jira_ticket, matrix_ticket)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (ticket_id, user_id, name, color, jira_ticket, matrix_ticket))
        conn.commit()
        conn.close()
        return ticket_id
    
    def update_ticket(self, user_id: int, ticket_id: str, name: str, color: str, jira_ticket: str = "", matrix_ticket: str = ""):
        """Update a ticket (only if it belongs to the user)."""
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE tickets 
            SET name = ?, color = ?, jira_ticket = ?, matrix_ticket = ?
            WHERE id = ? AND user_id = ?
        ''', (name, color, jira_ticket, matrix_ticket, ticket_id, user_id))
        conn.commit()
        conn.close()
        return cursor.rowcount > 0
    
    def delete_ticket(self, user_id: int, ticket_id: str):
        """Delete a ticket (only if it belongs to the user)."""
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM tickets WHERE id = ? AND user_id = ?', (ticket_id, user_id))
        conn.commit()
        conn.close()
        return cursor.rowcount > 0
    
    def get_entries(self, user_id: int):
        """Get all time entries for a specific user."""
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, user_id, ticket_name, start_time, end_time, memo
            FROM time_entries WHERE user_id = ? ORDER BY start_time DESC
        ''', (user_id,))
        entries = []
        for row in cursor.fetchall():
            entries.append(TimeEntry(
                id=row[0], user_id=row[1], ticket_name=row[2],
                start_time=row[3], end_time=row[4], memo=row[5]
            ))
        conn.close()
        return entries
    
    def get_time_summary(self, user_id: int, start_date: str, end_date: str):
        """Get time summary for a user within a date range."""
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        start_datetime = f"{start_date}T00:00:00"
        end_datetime = f"{end_date}T23:59:59"
        
        cursor.execute('''
            SELECT ticket_name, 
                   SUM(CASE 
                       WHEN end_time IS NOT NULL 
                       THEN (julianday(end_time) - julianday(start_time)) * 24
                       ELSE 0 
                   END) as total_hours
            FROM time_entries 
            WHERE user_id = ? 
                AND start_time >= ? 
                AND start_time <= ?
                AND end_time IS NOT NULL
            GROUP BY ticket_name
            ORDER BY total_hours DESC
        ''', (user_id, start_datetime, end_datetime))
        
        summary = {}
        total_time = 0
        for row in cursor.fetchall():
            ticket_name = row[0]
            hours = round(row[1], 2)
            summary[ticket_name] = hours
            total_time += hours
        
        conn.close()
        return summary, round(total_time, 2)
    
    def start_time_entry(self, user_id: int, ticket_name: str):
        """Start a new time entry for a user."""
        self.stop_current_entry(user_id)
        
        entry_id = str(uuid.uuid4())
        start_time = datetime.now().isoformat()
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO time_entries (id, user_id, ticket_name, start_time)
            VALUES (?, ?, ?, ?)
        ''', (entry_id, user_id, ticket_name, start_time))
        
        cursor.execute('''
            INSERT OR REPLACE INTO current_entries (user_id, entry_id)
            VALUES (?, ?)
        ''', (user_id, entry_id))
        
        conn.commit()
        conn.close()
        return entry_id
    
    def stop_current_entry(self, user_id: int):
        """Stop the current running entry for a user."""
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute('SELECT entry_id FROM current_entries WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        
        if row:
            entry_id = row[0]
            end_time = datetime.now().isoformat()
            
            cursor.execute('''
                UPDATE time_entries SET end_time = ? WHERE id = ? AND user_id = ?
            ''', (end_time, entry_id, user_id))
            
            cursor.execute('DELETE FROM current_entries WHERE user_id = ?', (user_id,))
        
        conn.commit()
        conn.close()
    
    def get_current_entry_id(self, user_id: int):
        """Get the current running entry ID for a user."""
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT entry_id FROM current_entries WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None
    
    def update_entry(self, user_id: int, entry_id: str, start_time: str, end_time: str, memo: str):
        """Update a time entry (only if it belongs to the user)."""
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE time_entries 
            SET start_time = ?, end_time = ?, memo = ?
            WHERE id = ? AND user_id = ?
        ''', (start_time, end_time if end_time else None, memo, entry_id, user_id))
        conn.commit()
        conn.close()
        return cursor.rowcount > 0
    
    def delete_entry(self, user_id: int, entry_id: str):
        """Delete a time entry (only if it belongs to the user)."""
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM current_entries WHERE user_id = ? AND entry_id = ?', (user_id, entry_id))
        cursor.execute('DELETE FROM time_entries WHERE id = ? AND user_id = ?', (entry_id, user_id))
        
        conn.commit()
        conn.close()
        return cursor.rowcount > 0
    
    def get_current_duration(self, user_id: int):
        """Get the duration of the current running entry for a user."""
        entry_id = self.get_current_entry_id(user_id)
        if not entry_id:
            return 0
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT start_time FROM time_entries WHERE id = ? AND end_time IS NULL', (entry_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            start = datetime.fromisoformat(row[0])
            return (datetime.now() - start).total_seconds()
        return 0

timesheet = TimesheetManager()

def get_current_user_id():
    """Get the current user ID from session."""
    return session.get('user_id')

def require_login():
    """Redirect to login if no user is logged in."""
    if not get_current_user_id():
        return redirect(url_for('login'))
    return None

# ===== AUTHENTICATION ROUTES =====

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        user = timesheet.authenticate_user(username, password)
        if user:
            session['user_id'] = user.id
            flash(f'Willkommen zurück, {user.username}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Ungültiger Benutzername oder Passwort', 'error')
    
    # Pass registration status to template
    return render_template('login.html', allow_registration=ALLOW_REGISTRATION)

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Check if registration is allowed
    if not ALLOW_REGISTRATION:
        flash('Registrierung ist derzeit deaktiviert. Bitte kontaktieren Sie den Administrator.', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')
        
        if not username or not password:
            flash('Benutzername und Passwort sind erforderlich', 'error')
        elif len(password) < 6:
            flash('Passwort muss mindestens 6 Zeichen lang sein', 'error')
        elif password != password_confirm:
            flash('Passwörter stimmen nicht überein', 'error')
        else:
            user_id = timesheet.add_user(username, password)
            if user_id:
                session['user_id'] = user_id
                flash(f'Willkommen, {username}! Ihr Account wurde erstellt.', 'success')
                return redirect(url_for('index'))
            else:
                flash('Benutzername existiert bereits', 'error')
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Sie wurden abgemeldet', 'info')
    return redirect(url_for('login'))

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    redirect_response = require_login()
    if redirect_response:
        return redirect_response
    
    user_id = get_current_user_id()
    current_user = timesheet.get_user_by_id(user_id)
    
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        new_password_confirm = request.form.get('new_password_confirm', '')
        
        # Verify current password
        if not timesheet.authenticate_user(current_user.username, current_password):
            flash('Aktuelles Passwort ist falsch', 'error')
        elif len(new_password) < 6:
            flash('Neues Passwort muss mindestens 6 Zeichen lang sein', 'error')
        elif new_password != new_password_confirm:
            flash('Neue Passwörter stimmen nicht überein', 'error')
        else:
            if timesheet.change_password(user_id, new_password):
                flash('Passwort erfolgreich geändert', 'success')
                return redirect(url_for('index'))
            else:
                flash('Fehler beim Ändern des Passworts', 'error')
    
    return render_template('change_password.html', current_user=current_user)

# ===== APPLICATION ROUTES =====

@app.route('/')
def index():
    redirect_response = require_login()
    if redirect_response:
        return redirect_response
    
    user_id = get_current_user_id()
    current_user = timesheet.get_user_by_id(user_id)
    
    entries = timesheet.get_entries(user_id)
    entries_by_date = defaultdict(list)
    for entry in entries:
        entry_date = entry.start_time[:10]
        entries_by_date[entry_date].append(entry)
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Cleanup old archived tickets automatically
    timesheet.cleanup_old_archived_tickets(user_id)
    
    return render_template('timesheet.html', 
                         current_user=current_user,
                         tickets=timesheet.get_tickets(user_id),
                         archived_tickets=timesheet.get_archived_tickets(user_id),
                         entries=entries,
                         entries_by_date=dict(entries_by_date),
                         today=today,
                         current_entry_id=timesheet.get_current_entry_id(user_id))

@app.route('/summary')
def summary():
    redirect_response = require_login()
    if redirect_response:
        return redirect_response
    
    user_id = get_current_user_id()
    current_user = timesheet.get_user_by_id(user_id)
    
    today = datetime.now()
    
    # Handle predefined periods
    period = request.args.get('period', 'custom')
    
    if period == 'today':
        start_date = today.strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
    elif period == 'yesterday':
        yesterday = today - timedelta(days=1)
        start_date = yesterday.strftime('%Y-%m-%d')
        end_date = yesterday.strftime('%Y-%m-%d')
    elif period == 'this_week':
        # Start of week (Monday)
        start_of_week = today - timedelta(days=today.weekday())
        start_date = start_of_week.strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
    elif period == 'last_week':
        # Last week (Monday to Sunday)
        start_of_last_week = today - timedelta(days=today.weekday() + 7)
        end_of_last_week = start_of_last_week + timedelta(days=6)
        start_date = start_of_last_week.strftime('%Y-%m-%d')
        end_date = end_of_last_week.strftime('%Y-%m-%d')
    elif period == 'this_month':
        start_date = today.replace(day=1).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
    elif period == 'last_month':
        # First day of last month
        first_of_this_month = today.replace(day=1)
        last_day_of_last_month = first_of_this_month - timedelta(days=1)
        first_of_last_month = last_day_of_last_month.replace(day=1)
        start_date = first_of_last_month.strftime('%Y-%m-%d')
        end_date = last_day_of_last_month.strftime('%Y-%m-%d')
    else:  # custom
        start_date = request.args.get('start_date', today.strftime('%Y-%m-%d'))
        end_date = request.args.get('end_date', today.strftime('%Y-%m-%d'))
    
    summary_data, total_time = timesheet.get_time_summary(user_id, start_date, end_date)
    
    # Get detailed entries for the period
    entries = timesheet.get_entries(user_id)
    period_entries = [
        entry for entry in entries
        if entry.end_time and start_date <= entry.start_time[:10] <= end_date
    ]
    
    # Group entries by date
    entries_by_date = defaultdict(list)
    for entry in period_entries:
        entry_date = entry.start_time[:10]
        entries_by_date[entry_date].append(entry)
    
    # Calculate daily totals
    daily_totals = {}
    for date, date_entries in entries_by_date.items():
        daily_total = 0
        for entry in date_entries:
            if entry.end_time:
                start = datetime.fromisoformat(entry.start_time)
                end = datetime.fromisoformat(entry.end_time)
                hours = (end - start).total_seconds() / 3600
                daily_total += hours
        daily_totals[date] = round(daily_total, 2)
    
    return render_template('summary.html', 
                         current_user=current_user,
                         summary_data=summary_data,
                         total_time=total_time,
                         start_date=start_date,
                         end_date=end_date,
                         period=period,
                         entries_by_date=dict(entries_by_date),
                         daily_totals=daily_totals)

@app.route('/add_ticket', methods=['POST'])
def add_ticket():
    redirect_response = require_login()
    if redirect_response:
        return redirect_response
    
    user_id = get_current_user_id()
    name = request.form.get('name', '').strip()
    color = request.form.get('color', '#656d76')
    jira_ticket = request.form.get('jira_ticket', '').strip()
    matrix_ticket = request.form.get('matrix_ticket', '').strip()
    
    if name:
        timesheet.add_ticket(user_id, name, color, jira_ticket, matrix_ticket)
    
    return redirect(url_for('index'))

@app.route('/update_ticket', methods=['POST'])
def update_ticket():
    redirect_response = require_login()
    if redirect_response:
        return redirect_response
    
    user_id = get_current_user_id()
    ticket_id = request.form.get('ticket_id')
    name = request.form.get('name', '').strip()
    color = request.form.get('color', '#656d76')
    jira_ticket = request.form.get('jira_ticket', '').strip()
    matrix_ticket = request.form.get('matrix_ticket', '').strip()
    
    if ticket_id and name:
        timesheet.update_ticket(user_id, ticket_id, name, color, jira_ticket, matrix_ticket)
    
    return redirect(url_for('index'))

@app.route('/get_ticket/<ticket_id>')
def get_ticket(ticket_id):
    redirect_response = require_login()
    if redirect_response:
        return jsonify({'error': 'Not authenticated'})
    
    user_id = get_current_user_id()
    ticket = timesheet.get_ticket_by_id(user_id, ticket_id)
    
    if ticket:
        return jsonify({
            'id': ticket.id,
            'name': ticket.name,
            'color': ticket.color,
            'jira_ticket': ticket.jira_ticket,
            'matrix_ticket': ticket.matrix_ticket
        })
    else:
        return jsonify({'error': 'Ticket not found'}), 404

@app.route('/save_ticket_order', methods=['POST'])
def save_ticket_order():
    redirect_response = require_login()
    if redirect_response:
        return jsonify({'success': False, 'error': 'Not authenticated'})
    
    user_id = get_current_user_id()
    data = request.get_json()
    
    if not data or 'ticket_order' not in data:
        return jsonify({'success': False, 'error': 'Invalid data'})
    
    ticket_order = data['ticket_order']
    user_tickets = timesheet.get_tickets(user_id)
    valid_ticket_ids = {ticket.id for ticket in user_tickets}
    filtered_order = [tid for tid in ticket_order if tid in valid_ticket_ids]
    
    try:
        timesheet.save_ticket_order(user_id, filtered_order)
        return jsonify({'success': True})
    except Exception as e:
        app.logger.error(f"Error saving ticket order: {e}")
        return jsonify({'success': False, 'error': 'Database error'})

@app.route('/start_timer/<ticket_name>')
def start_timer(ticket_name):
    redirect_response = require_login()
    if redirect_response:
        return redirect_response
    
    user_id = get_current_user_id()
    timesheet.start_time_entry(user_id, ticket_name)
    return redirect(url_for('index'))

@app.route('/stop_timer')
def stop_timer():
    redirect_response = require_login()
    if redirect_response:
        return redirect_response
    
    user_id = get_current_user_id()
    timesheet.stop_current_entry(user_id)
    return redirect(url_for('index'))

@app.route('/update_entry', methods=['POST'])
def update_entry():
    redirect_response = require_login()
    if redirect_response:
        return redirect_response
    
    user_id = get_current_user_id()
    entry_id = request.form.get('entry_id')
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')
    memo = request.form.get('memo', '')
    
    timesheet.update_entry(user_id, entry_id, start_time, end_time, memo)
    return redirect(url_for('index'))

@app.route('/archive_ticket/<ticket_id>')
def archive_ticket(ticket_id):
    redirect_response = require_login()
    if redirect_response:
        return redirect_response
    
    user_id = get_current_user_id()
    timesheet.archive_ticket(user_id, ticket_id)
    return redirect(url_for('index'))

@app.route('/restore_ticket/<ticket_id>')
def restore_ticket(ticket_id):
    redirect_response = require_login()
    if redirect_response:
        return redirect_response
    
    user_id = get_current_user_id()
    timesheet.restore_ticket(user_id, ticket_id)
    return redirect(url_for('index'))

@app.route('/delete_ticket/<ticket_id>')
def delete_ticket(ticket_id):
    redirect_response = require_login()
    if redirect_response:
        return redirect_response
    
    user_id = get_current_user_id()
    timesheet.delete_ticket(user_id, ticket_id)
    return redirect(url_for('index'))

@app.route('/delete_entry/<entry_id>')
def delete_entry(entry_id):
    redirect_response = require_login()
    if redirect_response:
        return redirect_response
    
    user_id = get_current_user_id()
    timesheet.delete_entry(user_id, entry_id)
    return redirect(url_for('index'))

@app.route('/current_duration')
def current_duration():
    redirect_response = require_login()
    if redirect_response:
        return jsonify({'duration': 0})
    
    user_id = get_current_user_id()
    duration = timesheet.get_current_duration(user_id)
    return jsonify({'duration': duration})

if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    
    from datetime import datetime
    
    @app.template_filter('as_datetime')
    def as_datetime(date_str):
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    
    @app.template_filter('format_hours')
    def format_hours(hours):
        """Format hours as HH:MM"""
        total_minutes = int(hours * 60)
        h = total_minutes // 60
        m = total_minutes % 60
        return f"{h:02d}:{m:02d}"
    
    print("Multiuser Timesheet-Webapp mit Login wird gestartet...")
    print(f"Database: {DATABASE}")
    print(f"Registration: {'ENABLED' if ALLOW_REGISTRATION else 'DISABLED'}")
    if not ALLOW_REGISTRATION:
        print("ℹ️  Neue Registrierungen sind deaktiviert")
    print("Standard-Login: demoUser / demo123")
    print("Öffnen Sie http://localhost:5000 in Ihrem Browser")
    
    host = '0.0.0.0' if os.environ.get('FLASK_ENV') == 'production' else '127.0.0.1'
    app.run(debug=False, host=host, port=5000)
