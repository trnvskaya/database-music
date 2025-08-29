from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from dotenv import load_dotenv
import os

# ==================== APP SETUP ====================

app = Flask(__name__)
load_dotenv()
app.secret_key = os.getenv('SECRET_KEY')

DATABASE_CONFIG = {
    'host' : os.getenv('DB_HOST'),
    'database' : os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'port': os.getenv('DB_PORT', 5432)
}

def get_db_connection():
    """Create database connection"""
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG, cursor_factory=RealDictCursor)
        return conn
    except psycopg2.Error as e:
        print(f"Database connection error: {e}")
        return None

def is_logged_in():
    """Check if user is logged in"""
    return 'username' in session

def require_login():
    if not is_logged_in():
        flash('Please log in to access this page', 'error')
        return redirect(url_for('login'))
    return None



# ==================== AUTH ROUTES ====================




@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name'].strip()
        email = request.form['email'].strip()
        password = request.form['password']
        user_type = request.form.get('user_type', 'basic').strip()

        if not full_name or not email or not password:
            flash('All fields are required', 'error')
            return render_template('auth/register.html')

        conn = get_db_connection()
        if not conn:
            flash('Database connection failed', 'error')
            return render_template('auth/register.html')

        try:
            cur = conn.cursor(cursor_factory=RealDictCursor)

            # Check if email exists
            cur.execute('SELECT username FROM users WHERE email = %s', (email,))
            if cur.fetchone():
                flash('Email already exists', 'error')
                return render_template('auth/register.html')

            # Insert new user; username is auto-generated SERIAL
            hashed_password = generate_password_hash(password)
            cur.execute('''
                INSERT INTO users (full_name, email, password_hash)
                VALUES (%s, %s, %s)
                RETURNING username
            ''', (full_name, email, hashed_password))
            new_user = cur.fetchone()
            username = new_user['username']  # numeric SERIAL

            # Create specific user type record
            if user_type == 'basic':
                cur.execute('''
                INSERT INTO basic_user (username, birth_date, preferences, profile_description, credit_card)
                VALUES (%s, CURRENT_DATE, %s, %s, %s)
                ''', (username, '', '', ''))

            elif user_type == 'artist':
                cur.execute('''
                INSERT INTO artist_user (username, discography, biography, genre)
                VALUES (%s, %s, %s, %s)
                ''', (username, '', '', ''))

            elif user_type == 'manager':
                cur.execute('''
                INSERT INTO manager_user (username, role_for_artist, tasks)
                VALUES (%s, %s, %s)
                ''', (username, '', ''))

            elif user_type == 'content_moderator':
                cur.execute('''
                INSERT INTO content_moderator_user (username, tasks, moderation_history)
                VALUES (%s, %s, %s)
                ''', (username, '', ''))

            conn.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))

        except psycopg2.Error as e:
            flash(f'Registration failed: {e}', 'error')
            conn.rollback()
        finally:
            conn.close()

    return render_template('auth/register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password']

        conn = get_db_connection()
        if not conn:
            flash('Database connection failed', 'error')
            return render_template('auth/login.html')

        try:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute('''
    SELECT username, full_name, email, password_hash,
           CASE
               WHEN EXISTS (SELECT 1 FROM artist_user WHERE username = users.username) THEN 'artist'
               WHEN EXISTS (SELECT 1 FROM manager_user WHERE username = users.username) THEN 'manager'
               WHEN EXISTS (SELECT 1 FROM content_moderator_user WHERE username = users.username) THEN 'content_moderator'
               ELSE 'basic'
           END AS user_type
    FROM users
    WHERE email = %s
''', (email,))
            user = cur.fetchone()


            if user and check_password_hash(user['password_hash'], password):
                session['username'] = user['username']
                session['full_name'] = user['full_name']
                session['email'] = user['email']
                session['user_type'] = user['user_type']  # <-- important!
                flash(f"Welcome back, {user['full_name']}!", 'success')
                return redirect(url_for('index'))
            else:
                flash('Invalid email or password', 'error')

        except psycopg2.Error as e:
            flash(f'Login failed: {e}', 'error')
        finally:
            conn.close()

    return render_template('auth/login.html')





@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))




# ==================== MAIN ROUTES ====================




@app.route('/')
def index():
    conn = get_db_connection()
    if not conn:
        return render_template('index.html', stats=None)
    
    try:
        cur = conn.cursor()
        stats = {}
        cur.execute('SELECT COUNT(*) as count FROM users')
        stats['users'] = cur.fetchone()['count']
        
        cur.execute('SELECT COUNT(*) as count FROM artist_user')
        stats['artists'] = cur.fetchone()['count']
        
        cur.execute('SELECT COUNT(*) as count FROM song')
        stats['songs'] = cur.fetchone()['count']
        
        cur.execute('SELECT COUNT(*) as count FROM event')
        stats['events'] = cur.fetchone()['count']
        
        # Get recent events
        cur.execute('''
            SELECT e.*, l.address, l.city, l.region, l.country 
            FROM event e 
            LEFT JOIN location l ON e.location_id = l.location_id 
            ORDER BY e.date DESC LIMIT 5
        ''')
        recent_events = cur.fetchall()
        
        conn.close()
        return render_template('index.html', stats=stats, recent_events=recent_events)
        
    except psycopg2.Error as e:
        flash(f'Database error: {e}', 'error')
        conn.close()
        return render_template('index.html', stats=None)



@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'username' not in session:
        flash('You must be logged in to view your profile.', 'error')
        return redirect(url_for('login'))

    user_type = session.get('user_type')
    username = session['username']

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Fetch main user info
    cur.execute('SELECT * FROM users WHERE username = %s', (username,))
    user = cur.fetchone()

    # Fetch type-specific info
    type_info = {}
    artist_songs = []
    if user_type == 'artist':
        cur.execute('SELECT * FROM artist_user WHERE username = %s', (username,))
        type_info = cur.fetchone() or {}
        cur.execute('''
            SELECT s.song_id, s.name 
            FROM song s
            JOIN song_artist_user sau ON s.song_id = sau.song_id
            WHERE sau.username = %s
        ''', (username,))
        artist_songs = cur.fetchall()
    elif user_type == 'manager':
        cur.execute('SELECT * FROM manager_user WHERE username = %s', (username,))
        type_info = cur.fetchone() or {}
    elif user_type == 'basic':
        cur.execute('SELECT * FROM basic_user WHERE username = %s', (username,))
        type_info = cur.fetchone() or {}
    elif user_type == 'moderator':
        cur.execute('SELECT * FROM content_moderator_user WHERE username = %s', (username,))
        type_info = cur.fetchone() or {}

    # Handle profile update
    if request.method == 'POST':
        messages = []  # Collect messages to flash once

        # General info (except email)
        full_name = request.form.get('full_name')
        mobile_phone = request.form.get('mobile_phone')
        links_media = request.form.get('links_media')

        cur.execute('''
            UPDATE users SET full_name=%s, mobile_phone=%s, links_media=%s
            WHERE username=%s
        ''', (full_name, mobile_phone, links_media, username))

        # Password change
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        if old_password and new_password:
            if check_password_hash(user['password_hash'], old_password):
                hashed_password = generate_password_hash(new_password)
                cur.execute('UPDATE users SET password_hash=%s WHERE username=%s', (hashed_password, username))
                messages.append('Password updated successfully!')
            else:
                messages.append('Old password is incorrect.')

        # Update type-specific info
        if user_type == 'artist':
            discography = request.form.get('discography')
            biography = request.form.get('biography')
            genre = request.form.get('genre')
            photos = request.form.get('photos')
            cur.execute('''
                UPDATE artist_user
                SET discography=%s, biography=%s, genre=%s, photos=%s
                WHERE username=%s
            ''', (discography, biography, genre, photos, username))
        elif user_type == 'manager':
            role_for_artist = request.form.get('role_for_artist')
            tasks = request.form.get('tasks')
            cur.execute('''
                UPDATE manager_user
                SET role_for_artist=%s, tasks=%s
                WHERE username=%s
            ''', (role_for_artist, tasks, username))
        elif user_type == 'basic':
            # convert empty strings to None to avoid invalid date/float errors
            def clean(val):
                return val if val else None

            birth_date = clean(request.form.get('birth_date'))
            preferences = clean(request.form.get('preferences'))
            profile_description = clean(request.form.get('profile_description'))
            credit_card = clean(request.form.get('credit_card'))
            subscription_type = clean(request.form.get('subscription_type'))
            subscription_price = clean(request.form.get('subscription_price'))
            subscription_date = clean(request.form.get('subscription_date'))
            bank_information = clean(request.form.get('bank_information'))

            cur.execute('''
                UPDATE basic_user
                SET birth_date=%s, preferences=%s, profile_description=%s,
                    credit_card=%s, subscription_type=%s, subscription_price=%s,
                    subscription_date=%s, bank_information=%s
                WHERE username=%s
            ''', (birth_date, preferences, profile_description, credit_card,
                  subscription_type, subscription_price, subscription_date,
                  bank_information, username))
        elif user_type == 'moderator':
            tasks = request.form.get('tasks')
            moderation_history = request.form.get('moderation_history')
            cur.execute('''
                UPDATE content_moderator_user
                SET tasks=%s, moderation_history=%s
                WHERE username=%s
            ''', (tasks, moderation_history, username))

        conn.commit()
        conn.close()

        # Flash all messages at once
        for msg in messages:
            flash(msg, 'success')
        if not messages:
            flash('Profile updated successfully!', 'success')

        return redirect(url_for('profile'))  # <- redirect prevents duplicates

    conn.close()
    return render_template(
        'auth/profile.html',
        user=user,
        type_info=type_info,
        artist_songs=artist_songs,
        user_type=user_type
    )




# ==================== ARTIST ROUTES ====================




@app.route('/artists')
def artists():
    conn = get_db_connection()
    if not conn:
        return render_template('artists/list.html', artists=[])
    
    try:
        cur = conn.cursor()
        cur.execute('''
            SELECT u.username, u.full_name, u.email, au.genre
            FROM users u
            JOIN artist_user au ON u.username = au.username
            ORDER BY u.username
        ''')
        artists = cur.fetchall()
        conn.close()
        return render_template('artists/list.html', artists=artists)
        
    except psycopg2.Error as e:
        flash(f'Error loading artists: {e}', 'error')
        conn.close()
        return render_template('artists/list.html', artists=[])

@app.route('/artist/<username>')
def artist_detail(username):
    conn = get_db_connection()
    if not conn:
        return redirect(url_for('artists'))

    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Get artist info
        cur.execute('''
            SELECT u.username, u.full_name, u.email, au.genre, au.biography
            FROM users u
            JOIN artist_user au ON u.username = au.username
            WHERE au.username = %s
        ''', (username,))
        artist = cur.fetchone()

        if not artist:
            flash('Artist not found', 'error')
            return redirect(url_for('artists'))

        # Get artist's songs
        cur.execute('''
            SELECT s.*
            FROM song s
            JOIN song_artist_user sau ON s.song_id = sau.song_id
            WHERE sau.username = %s
        ''', (username,))
        songs = cur.fetchall()

        # Get artist's events
        cur.execute('''
            SELECT e.*, l.city as location_name
            FROM event e
            LEFT JOIN location l ON e.location_id = l.location_id
            JOIN event_artist_user eau ON e.event_id = eau.event_id
            WHERE eau.username = %s
            ORDER BY e.date DESC
        ''', (username,))
        events = cur.fetchall()

        conn.close()
        return render_template('artists/detail.html', artist=artist, songs=songs, events=events)

    except psycopg2.Error as e:
        flash(f'Error loading artist: {e}', 'error')
        conn.close()
        return redirect(url_for('artists'))





# ==================== SONG ROUTES ====================






@app.route('/songs')
def songs():
    conn = get_db_connection()
    if not conn:
        return render_template('songs/list.html', songs=[])
    
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)  # Use RealDictCursor for dict rows
        cur.execute('''
            SELECT s.song_id, s.name, u.full_name AS artist_name 
            FROM song s 
            LEFT JOIN song_artist_user sau ON s.song_id = sau.song_id 
            LEFT JOIN artist_user au ON sau.username = au.username 
            LEFT JOIN users u ON au.username = u.username
            ORDER BY s.name DESC
        ''')
        songs = cur.fetchall()
        conn.close()
        return render_template('songs/list.html', songs=songs)
        
    except psycopg2.Error as e:
        flash(f'Error loading songs: {e}', 'error')
        conn.close()
        return render_template('songs/list.html', songs=[])


@app.route('/song/<int:song_id>')
def song_detail(song_id):
    conn = get_db_connection()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Get song info
        cur.execute('SELECT song_id, name, lyrics FROM song WHERE song_id = %s', (song_id,))
        song = cur.fetchone()

        # Get artists
        cur.execute('''
            SELECT u.full_name AS artist_name, au.username AS artist_username
            FROM song_artist_user sau
            JOIN artist_user au ON sau.username = au.username
            JOIN users u ON au.username = u.username
            WHERE sau.song_id = %s
        ''', (song_id,))
        artists = cur.fetchall()

        conn.close()
        return render_template('songs/detail.html', song=song, artists=artists)
    except psycopg2.Error as e:
        flash(f'Error loading song: {e}', 'error')
        conn.close()
        return render_template('songs/detail.html', song=None, artists=[])





@app.route('/add_song', methods=['GET', 'POST'])
def add_song():
    # Only allow logged-in artists
    if 'username' not in session or session.get('user_type') != 'artist':
        flash('You must be logged in as an artist to add a song.', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name'].strip()
        lyrics = request.form.get('lyrics', '').strip()

        if not name:
            flash('Song name is required.', 'error')
            return render_template('songs/add.html')

        conn = get_db_connection()
        if not conn:
            flash('Database connection failed', 'error')
            return render_template('songs/add.html')

        try:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            # Add song
            cur.execute('INSERT INTO song (name, lyrics) VALUES (%s, %s) RETURNING song_id',
                        (name, lyrics))
            song_id = cur.fetchone()['song_id']

            # Associate with current artist
            cur.execute('INSERT INTO song_artist_user (song_id, username) VALUES (%s, %s)',
                        (song_id, session['username']))

            conn.commit()
            flash('Song added successfully!', 'success')
            return redirect(url_for('songs'))

        except psycopg2.Error as e:
            flash(f'Error adding song: {e}', 'error')
            conn.rollback()
        finally:
            conn.close()

    return render_template('songs/add.html')






# ==================== PLAYLIST ROUTES ====================



@app.route('/playlists')
def playlists():
    login_check = require_login()
    if login_check:
        return login_check

    conn = get_db_connection()
    playlists = []
    if conn:
        try:
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            # Show all playlists
            cur.execute('''
                SELECT p.*, bu.basic_user_username AS owner_name
                FROM playlist p
                JOIN basic_user bu ON p.username = bu.username
                ORDER BY p.playlist_id DESC
            ''')
            playlists = cur.fetchall()
        except psycopg2.Error as e:
            flash(f'Error loading playlists: {e}', 'danger')
        finally:
            conn.close()
    return render_template('playlists/list.html', playlists=playlists)


@app.route('/create_playlist', methods=['GET', 'POST'])
def create_playlist():
    login_check = require_login()
    if login_check:
        return login_check

    if request.method == 'POST':
        name = request.form['name']  # new playlist name
        description = request.form.get('description', '')
        link = request.form.get('link', '')

        conn = get_db_connection()
        if not conn:
            flash('Database connection failed', 'danger')
            return render_template('playlists/create.html')

        try:
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

            # Check if current user is a basic user
            cur.execute('SELECT username FROM basic_user WHERE username = %s', (session['username'],))
            basic_user = cur.fetchone()

            if not basic_user:
                flash('Only basic users can create playlists', 'danger')
                return render_template('playlists/create.html')

            # Insert playlist with auto-increment ID
            cur.execute('''
                INSERT INTO playlist (username, name, description, link)
                VALUES (%s, %s, %s, %s)
            ''', (basic_user['username'], name, description, link))

            conn.commit()
            flash('Playlist created successfully!', 'success')
            return redirect(url_for('playlists'))

        except psycopg2.Error as e:
            flash(f'Error creating playlist: {e}', 'danger')
        finally:
            conn.close()

    return render_template('playlists/create.html')


@app.route('/playlist/<int:playlist_id>')
def playlist_detail(playlist_id):
    login_check = require_login()
    if login_check:
        return login_check

    conn = get_db_connection()
    if not conn:
        flash('Database connection failed', 'danger')
        return redirect(url_for('playlists'))

    playlist = None
    songs_in_playlist = []
    songs_available = []

    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Get playlist info
        cur.execute('''
            SELECT p.*, bu.basic_user_username AS owner_name
            FROM playlist p
            JOIN basic_user bu ON p.username = bu.username
            WHERE p.playlist_id = %s
        ''', (playlist_id,))
        playlist = cur.fetchone()

        if not playlist:
            flash('Playlist not found', 'warning')
            return redirect(url_for('playlists'))

        # Songs already in playlist
        cur.execute('''
            SELECT s.*
            FROM song s
            JOIN song_playlist sp ON s.song_id = sp.song_id
            WHERE sp.playlist_id = %s
        ''', (playlist_id,))
        songs_in_playlist = cur.fetchall()

        # Songs NOT in playlist (to show in dropdown for adding)
        cur.execute('''
            SELECT *
            FROM song
            WHERE song_id NOT IN (
                SELECT song_id FROM song_playlist WHERE playlist_id = %s
            )
        ''', (playlist_id,))
        songs_available = cur.fetchall()

    except psycopg2.Error as e:
        flash(f'Error loading playlist: {e}', 'danger')
        return redirect(url_for('playlists'))
    finally:
        conn.close()

    return render_template(
        'playlists/detail.html',
        playlist=playlist,
        songs_in_playlist=songs_in_playlist,
        songs_available=songs_available
    )



@app.route('/add_song_to_playlist', methods=['POST'])
def add_song_to_playlist():
    login_check = require_login()
    if login_check:
        return login_check

    playlist_id = request.form['playlist_id']
    song_id = request.form['song_id']

    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection failed'})

    try:
        cur = conn.cursor()
        # Check if song is already in playlist
        cur.execute('SELECT 1 FROM song_playlist WHERE playlist_id = %s AND song_id = %s', (playlist_id, song_id))
        if cur.fetchone():
            return jsonify({'success': False, 'message': 'Song already in playlist'})

        # Insert song into playlist
        cur.execute('INSERT INTO song_playlist (song_id, playlist_id) VALUES (%s, %s)', (song_id, playlist_id))
        conn.commit()
        return jsonify({'success': True, 'message': 'Song added to playlist'})

    except psycopg2.Error as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        conn.close()



# ==================== EVENT ROUTES ====================






@app.route('/events')
def events():
    conn = get_db_connection()
    if not conn:
        return render_template('events/list.html', events=[])
    
    try:
        cur = conn.cursor()
        # Fix: Use correct column names from your schema
        cur.execute('''
            SELECT e.event_id, e.description, e.date, e.conditions,
                   l.country, l.region, l.city, l.address
            FROM event e
            LEFT JOIN location l ON e.location_id = l.location_id
            ORDER BY e.date ASC
        ''')
        events = cur.fetchall()
        conn.close()
        return render_template('events/list.html', events=events)
        
    except psycopg2.Error as e:
        flash(f'Error loading events: {e}', 'error')
        conn.close()
        return render_template('events/list.html', events=[])




@app.route('/events/<int:event_id>')
def event_detail(event_id):
    conn = get_db_connection()
    if not conn:
        flash("Database connection failed", "error")
        return redirect(url_for('events'))

    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute('''
            SELECT e.event_id, e.description, e.date, e.conditions,
                   l.country, l.region, l.city, l.address
            FROM event e
            LEFT JOIN location l ON e.location_id = l.location_id
            WHERE e.event_id = %s
        ''', (event_id,))
        event = cur.fetchone()
        conn.close()

        if not event:
            flash("Event not found", "error")
            return redirect(url_for('events'))

        return render_template('events/detail.html', event=event)

    except psycopg2.Error as e:
        flash(f"Error loading event: {e}", "error")
        conn.close()
        return redirect(url_for('events'))





@app.route('/create_event', methods=['GET', 'POST'])
def create_event():
    # Require login
    login_check = require_login()
    if login_check:
        return login_check

    # Only artists and managers can create events
    if session.get('user_type') not in ['artist', 'manager']:
        flash('Only artists and managers can create events', 'error')
        return redirect(url_for('events'))

    conn = get_db_connection()
    if not conn:
        flash('Database connection failed', 'error')
        return render_template('events/create.html', locations=[])

    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Get locations for dropdown (needed for both GET and POST)
        cur.execute('SELECT location_id, country, region, city, address FROM location ORDER BY city')
        locations = cur.fetchall()

        # Handle form submission
        if request.method == 'POST':
            description = request.form.get('description', '').strip()
            date = request.form.get('date')
            conditions = request.form.get('conditions', '').strip()
            location_id = request.form.get('location_id')

            if not description or not date or not location_id:
                flash('Please fill in all required fields.', 'error')
                return render_template('events/create.html', locations=locations)

            # Insert event
            cur.execute('''
                INSERT INTO event (location_id, description, date, conditions) 
                VALUES (%s, %s, %s, %s) RETURNING event_id
            ''', (location_id, description, date, conditions))
            
            event_id = cur.fetchone()['event_id']

            # Associate event with artist if current user is an artist
            if session.get('user_type') == 'artist':
                cur.execute('''
                    INSERT INTO event_artist_user (event_id, artist_user_id) 
                    SELECT %s, username FROM artist_user WHERE username = %s
                ''', (event_id, session['username']))

            conn.commit()
            flash('Event created successfully!', 'success')
            return redirect(url_for('events'))

        # GET request renders form
        return render_template('events/create.html', locations=locations)

    except psycopg2.Error as e:
        flash(f'Error creating event: {e}', 'error')
        return render_template('events/create.html', locations=locations)

    finally:
        if conn:
            conn.close()





# # ==================== MERCHANDISE ROUTES ====================


# @app.route('/merchandise')
# def merchandise():
#     conn = get_db_connection()
#     if not conn:
#         return render_template('merchandise/list.html', products=[])
    
#     try:
#         cur = conn.cursor(cursor_factory=RealDictCursor)
#         cur.execute('SELECT * FROM merchandise_product ORDER BY name')
#         products = cur.fetchall()
#         conn.close()
#         return render_template('merchandise/list.html', products=products)
        
#     except psycopg2.Error as e:
#         flash(f'Error loading merchandise: {e}', 'error')
#         conn.close()
#         return render_template('merchandise/list.html', products=[])


# @app.route('/add_merchandise', methods=['GET', 'POST'])
# def add_merchandise():
#     login_check = require_login()
#     if login_check:
#         return login_check
    
#     if session.get('user_type') not in ['artist', 'manager']:
#         flash('Only artists and managers can add merchandise', 'error')
#         return redirect(url_for('merchandise'))
    
#     if request.method == 'POST':
#         name = request.form['name']
#         description = request.form.get('description', '')
#         price = request.form['price']
#         stock_quantity = request.form['stock_quantity']
#         category = request.form.get('category', '')

#         conn = get_db_connection()
#         if not conn:
#             flash('Database connection failed', 'error')
#             return render_template('merchandise/add.html')
        
#         try:
#             cur = conn.cursor()
#             cur.execute('''
#                 INSERT INTO merchandise_product (name, description, price, stock_quantity, category, created_at)
#                 VALUES (%s, %s, %s, %s, %s, %s)
#             ''', (name, description, price, stock_quantity, category, datetime.now()))
            
#             conn.commit()
#             conn.close()
            
#             flash('Merchandise added successfully!', 'success')
#             return redirect(url_for('merchandise'))
            
#         except psycopg2.Error as e:
#             flash(f'Error adding merchandise: {e}', 'error')
#             conn.close()
    
#     return render_template('merchandise/add.html')



# # ==================== SEARCH ROUTE ====================




# @app.route('/search')
# def search():
#     query = request.args.get('q', '').strip()
#     if not query:
#         return render_template('search.html', results=None, query='')

#     conn = get_db_connection()
#     if not conn:
#         flash('Database connection failed', 'error')
#         return render_template('search.html', results=None, query=query)

#     try:
#         cur = conn.cursor(cursor_factory=RealDictCursor)
#         search_pattern = f'%{query}%'
#         results = {
#             'artists': [],
#             'songs': [],
#             'events': [],
#             'playlists': []
#         }

#         # Search artists
#         cur.execute('''
#             SELECT u.username, au.genre, au.biography 
#             FROM users u
#             JOIN artist_user au ON u.username = au.username
#             WHERE u.username ILIKE %s OR au.genre ILIKE %s OR au.biography ILIKE %s
#         ''', (search_pattern, search_pattern, search_pattern))
#         results['artists'] = cur.fetchall()

#         # Search songs
#         cur.execute('''
#             SELECT s.name AS title, u.username AS artist_name
#             FROM song s
#             JOIN song_artist_user sau ON s.song_id = sau.song_id
#             JOIN artist_user au ON sau.username = au.username
#             JOIN users u ON au.username = u.username
#             WHERE s.name ILIKE %s
#         ''', (search_pattern,))
#         results['songs'] = cur.fetchall()

#         # Search events
#         cur.execute('''
#             SELECT e.event_id, e.description, e.date, l.city AS location_name
#             FROM event e
#             LEFT JOIN location l ON e.location_id = l.location_id
#             WHERE e.description ILIKE %s
#         ''', (search_pattern,))
#         results['events'] = cur.fetchall()

#         # Search playlists (public only)
#         cur.execute('''
#             SELECT p.playlist_id, p.name, u.username AS owner_name
#             FROM playlist p
#             JOIN basic_user bu ON p.basic_user_id = bu.basic_user_id
#             JOIN users u ON bu.username = u.username
#             WHERE p.is_public = TRUE AND p.name ILIKE %s
#         ''', (search_pattern,))
#         results['playlists'] = cur.fetchall()

#         conn.close()
#         return render_template('search.html', results=results, query=query)

#     except psycopg2.Error as e:
#         flash(f'Search error: {e}', 'error')
#         conn.close()
#         return render_template('search.html', results=None, query=query)




if __name__ == '__main__':
    app.run(debug=True)