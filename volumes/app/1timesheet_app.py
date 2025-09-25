from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from datetime import datetime, timedelta
import sqlite3
import os
from dataclasses import dataclass
from typing import List, Optional
import uuid
from collections import defaultdict
import logging


app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')

app.logger.setLevel(logging.DEBUG)


# Use environment variable for database path, fallback to local
DATABASE = os.environ.get('DATABASE_PATH', 'timesheet.db')

def init_database():
    """Initialize the SQLite database with required tables."""
    # Ensure directory exists
    db_dir = os.path.dirname(DATABASE)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
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
    
    # Create some default users for testing
    #cursor.execute('INSERT OR IGNORE INTO users (username) VALUES (?)', ('Admin',))
    #cursor.execute('INSERT OR IGNORE INTO users (username) VALUES (?)', ('User1',))
    cursor.execute('INSERT OR IGNORE INTO users (username) VALUES (?)', ('demoUser',))
    
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
    
    def add_user(self, username: str):
        """Add a new user."""
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO users (username) VALUES (?)', (username,))
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return user_id
        except sqlite3.IntegrityError:
            conn.close()
            return None  # Username already exists
    
    def get_tickets(self, user_id: int):
        """Get all tickets for a specific user."""
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, user_id, name, color, jira_ticket, matrix_ticket 
            FROM tickets WHERE user_id = ? ORDER BY name
        ''', (user_id,))
        tickets = []
        for row in cursor.fetchall():
            tickets.append(Ticket(
                id=row[0], user_id=row[1], name=row[2], color=row[3],
                jira_ticket=row[4], matrix_ticket=row[5]
            ))
        conn.close()
        return tickets
    
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
        
        # DEBUG: First check ALL entries for this user
        cursor.execute('SELECT ticket_name, start_time, end_time FROM time_entries WHERE user_id = ?', (user_id,))
        all_user_entries = cursor.fetchall()
        app.logger.info(f"DEBUG - User {user_id} has {len(all_user_entries)} total entries:")
        for entry in all_user_entries[:5]:  # Show first 5
            app.logger.info(f"DEBUG - All entries: {entry[0]}, start={entry[1]}, end={entry[2]}")
        
        # Add time component to dates for proper filtering
        start_datetime = f"{start_date} 00:00:00"
        end_datetime = f"{end_date} 23:59:59"
        
        app.logger.info(f"DEBUG - Querying user_id: {user_id}")
        app.logger.info(f"DEBUG - Date range: {start_datetime} to {end_datetime}")
        
        # Check entries in date range WITHOUT time filter first
        cursor.execute('''
            SELECT ticket_name, start_time, end_time
            FROM time_entries 
            WHERE user_id = ?
        ''', (user_id,))
        
        all_entries_no_filter = cursor.fetchall()
        app.logger.info(f"DEBUG - Found {len(all_entries_no_filter)} entries for user (no date filter)")
        
        # Now with date filter
        cursor.execute('''
            SELECT ticket_name, start_time, end_time
            FROM time_entries 
            WHERE user_id = ? 
                AND start_time >= ? 
                AND start_time <= ?
        ''', (user_id, start_datetime, end_datetime))
        
        all_entries = cursor.fetchall()
        app.logger.info(f"DEBUG - Found {len(all_entries)} entries in date range")
        for entry in all_entries:
            app.logger.info(f"DEBUG - Entry: {entry[0]}, {entry[1]}, {entry[2]}")
        
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
        
        results = cursor.fetchall()
        app.logger.info(f"DEBUG - SQL returned {len(results)} grouped results")
        for result in results:
            app.logger.info(f"DEBUG - Result: {result[0]}, {result[1]} hours")
        
        summary = {}
        total_time = 0
        for row in results:
            ticket_name = row[0]
            hours = round(row[1], 2)
            summary[ticket_name] = hours
            total_time += hours
        
        app.logger.info(f"DEBUG - Final summary: {summary}")
        app.logger.info(f"DEBUG - Final total_time: {total_time}")
        
        conn.close()
        return summary, round(total_time, 2)
    
    # def get_time_summary(self, user_id: int, start_date: str, end_date: str):
    #     """Get time summary for a user within a date range."""
    #     conn = sqlite3.connect(DATABASE)
    #     cursor = conn.cursor()
        
    #     # Add time component to dates for proper filtering
    #     start_datetime = f"{start_date} 00:00:00"
    #     end_datetime = f"{end_date} 23:59:59"
        
    #     # DEBUG: Print what we're querying
    #     app.logger.info(f"DEBUG - Querying user_id: {user_id}")
    #     app.logger.info(f"DEBUG - Date range: {start_datetime} to {end_datetime}")
        
    #     # First, let's see what entries exist
    #     cursor.execute('''
    #         SELECT ticket_name, start_time, end_time
    #         FROM time_entries 
    #         WHERE user_id = ? 
    #             AND start_time >= ? 
    #             AND start_time <= ?
    #     ''', (user_id, start_datetime, end_datetime))
        
    #     all_entries = cursor.fetchall()
    #     app.logger.info(f"DEBUG - Found {len(all_entries)} entries in date range")
    #     for entry in all_entries:
    #         app.logger.info(f"DEBUG - Entry: {entry[0]}, {entry[1]}, {entry[2]}")
        
    #     cursor.execute('''
    #         SELECT ticket_name, 
    #                SUM(CASE 
    #                    WHEN end_time IS NOT NULL 
    #                    THEN (julianday(end_time) - julianday(start_time)) * 24
    #                    ELSE 0 
    #                END) as total_hours
    #         FROM time_entries 
    #         WHERE user_id = ? 
    #             AND start_time >= ? 
    #             AND start_time <= ?
    #             AND end_time IS NOT NULL
    #         GROUP BY ticket_name
    #         ORDER BY total_hours DESC
    #     ''', (user_id, start_datetime, end_datetime))
        
    #     results = cursor.fetchall()
    #     print(f"DEBUG - SQL returned {len(results)} grouped results")
    #     for result in results:
    #         print(f"DEBUG - Result: {result[0]}, {result[1]} hours")
        
    #     summary = {}
    #     total_time = 0
    #     for row in results:
    #         ticket_name = row[0]
    #         hours = round(row[1], 2)
    #         summary[ticket_name] = hours
    #         total_time += hours
        
    #     app.logger.info(f"DEBUG - Final summary: {summary}")
    #     app.logger.info(f"DEBUG - Final total_time: {total_time}")
        
    #     conn.close()
    #     return summary, round(total_time, 2)
    
    def start_time_entry(self, user_id: int, ticket_name: str):
        """Start a new time entry for a user."""
        # Stop current entry if exists
        self.stop_current_entry(user_id)
        
        # Start new entry
        entry_id = str(uuid.uuid4())
        start_time = datetime.now().isoformat()
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Insert new entry
        cursor.execute('''
            INSERT INTO time_entries (id, user_id, ticket_name, start_time)
            VALUES (?, ?, ?, ?)
        ''', (entry_id, user_id, ticket_name, start_time))
        
        # Set as current entry
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
        
        # Get current entry
        cursor.execute('SELECT entry_id FROM current_entries WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        
        if row:
            entry_id = row[0]
            end_time = datetime.now().isoformat()
            
            # Update entry with end time
            cursor.execute('''
                UPDATE time_entries SET end_time = ? WHERE id = ? AND user_id = ?
            ''', (end_time, entry_id, user_id))
            
            # Remove from current entries
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
        
        # Remove from current entries if it's the current one
        cursor.execute('DELETE FROM current_entries WHERE user_id = ? AND entry_id = ?', (user_id, entry_id))
        
        # Delete the entry
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

def require_user():
    """Redirect to user selection if no user is selected."""
    if not get_current_user_id():
        return redirect(url_for('select_user'))
    return None

@app.route('/')
def index():
    redirect_response = require_user()
    if redirect_response:
        return redirect_response
    
    user_id = get_current_user_id()
    current_user = timesheet.get_user_by_id(user_id)
    
    # Group entries by date for template
    entries = timesheet.get_entries(user_id)
    entries_by_date = defaultdict(list)
    for entry in entries:
        entry_date = entry.start_time[:10]  # Extract YYYY-MM-DD
        entries_by_date[entry_date].append(entry)
    
    # Get today's date
    today = datetime.now().strftime('%Y-%m-%d')
    
    return render_template('timesheet.html', 
                         current_user=current_user,
                         tickets=timesheet.get_tickets(user_id),
                         entries=entries,
                         entries_by_date=dict(entries_by_date),
                         today=today,
                         current_entry_id=timesheet.get_current_entry_id(user_id))

@app.route('/summary')
def summary():
    redirect_response = require_user()
    if redirect_response:
        return redirect_response
    
    user_id = get_current_user_id()
    current_user = timesheet.get_user_by_id(user_id)
    
    # Get date range from request parameters
    today = datetime.now().strftime('%Y-%m-%d')
    start_date = request.args.get('start_date', today)
    end_date = request.args.get('end_date', today)
    
    # DEBUG: Print route values
    print(f"DEBUG ROUTE - User ID: {user_id}")
    print(f"DEBUG ROUTE - Date range: {start_date} to {end_date}")
    
    # Get summary data
    summary_data, total_time = timesheet.get_time_summary(user_id, start_date, end_date)
    
    # DEBUG: Print final route values
    print(f"DEBUG ROUTE - Summary data: {summary_data}")
    print(f"DEBUG ROUTE - Total time: {total_time}")
    
    return render_template('summary.html', 
                         current_user=current_user,
                         summary_data=summary_data,
                         total_time=total_time,
                         start_date=start_date,
                         end_date=end_date)

@app.route('/select_user')
def select_user():
    users = timesheet.get_users()
    return render_template('user_select.html', users=users)

@app.route('/switch_user/<int:user_id>')
def switch_user(user_id):
    user = timesheet.get_user_by_id(user_id)
    if user:
        session['user_id'] = user_id
    return redirect(url_for('index'))

@app.route('/add_user', methods=['POST'])
def add_user():
    username = request.form.get('username', '').strip()
    if username:
        user_id = timesheet.add_user(username)
        if user_id:
            session['user_id'] = user_id
            return redirect(url_for('index'))
    return redirect(url_for('select_user'))

@app.route('/add_ticket', methods=['POST'])
def add_ticket():
    redirect_response = require_user()
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
    redirect_response = require_user()
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
    redirect_response = require_user()
    if redirect_response:
        return jsonify({'error': 'No user selected'})
    
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

@app.route('/start_timer/<ticket_name>')
def start_timer(ticket_name):
    redirect_response = require_user()
    if redirect_response:
        return redirect_response
    
    user_id = get_current_user_id()
    timesheet.start_time_entry(user_id, ticket_name)
    return redirect(url_for('index'))

@app.route('/stop_timer')
def stop_timer():
    redirect_response = require_user()
    if redirect_response:
        return redirect_response
    
    user_id = get_current_user_id()
    timesheet.stop_current_entry(user_id)
    return redirect(url_for('index'))

@app.route('/update_entry', methods=['POST'])
def update_entry():
    redirect_response = require_user()
    if redirect_response:
        return redirect_response
    
    user_id = get_current_user_id()
    entry_id = request.form.get('entry_id')
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')
    memo = request.form.get('memo', '')
    
    timesheet.update_entry(user_id, entry_id, start_time, end_time, memo)
    return redirect(url_for('index'))

@app.route('/delete_ticket/<ticket_id>')
def delete_ticket(ticket_id):
    redirect_response = require_user()
    if redirect_response:
        return redirect_response
    
    user_id = get_current_user_id()
    timesheet.delete_ticket(user_id, ticket_id)
    return redirect(url_for('index'))

@app.route('/delete_entry/<entry_id>')
def delete_entry(entry_id):
    redirect_response = require_user()
    if redirect_response:
        return redirect_response
    
    user_id = get_current_user_id()
    timesheet.delete_entry(user_id, entry_id)
    return redirect(url_for('index'))

@app.route('/current_duration')
def current_duration():
    redirect_response = require_user()
    if redirect_response:
        return jsonify({'duration': 0})
    
    user_id = get_current_user_id()
    duration = timesheet.get_current_duration(user_id)
    return jsonify({'duration': duration})

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    # Add custom filter for datetime conversion
    from datetime import datetime
    
    @app.template_filter('as_datetime')
    def as_datetime(date_str):
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    
    print("Multiuser Timesheet-Webapp wird gestartet...")
    print(f"Database: {DATABASE}")
    print("Öffnen Sie http://localhost:5000 in Ihrem Browser")
    
    # Use different host/port for Docker
    host = '0.0.0.0' if os.environ.get('FLASK_ENV') == 'production' else '127.0.0.1'
    app.run(debug=False, host=host, port=5000)
