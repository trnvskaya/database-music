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
    return 'user_id' in session

def require_login():
    if not is_logged_in():
        flash('Please log in to access this page', 'error')
        return redirect(url_for('login'))
    return None



# ==================== AUTH ROUTES ====================




@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password']
        user_type = request.form.get('user_type', 'basic').strip()

        if not username or not email or not password:
            flash('All fields are required', 'error')
            return render_template('auth/register.html')

        conn = get_db_connection()
        if not conn:
            flash('Database connection failed', 'error')
            return render_template('auth/register.html')

        try:
            cur = conn.cursor(cursor_factory=RealDictCursor)

            # Check for existing username/email
            cur.execute('SELECT username FROM users WHERE username = %s OR email = %s', (username, email))
            if cur.fetchone():
                flash('Username or email already exists', 'error')
                return render_template('auth/register.html')

            # Insert new user
            hashed_password = generate_password_hash(password)
            cur.execute('''
                INSERT INTO users (username, full_name, email, password_hash)
                VALUES (%s, %s, %s, %s)
            ''', (username, username, email, hashed_password))

            # Create specific user type record
            if user_type == 'basic':
                cur.execute('INSERT INTO basic_user (username) VALUES (%s)', (username,))
            elif user_type == 'artist':
                cur.execute('INSERT INTO artist_user (username) VALUES (%s)', (username,))
            elif user_type == 'manager':
                cur.execute('INSERT INTO manager_user (username) VALUES (%s)', (username,))

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
        username = request.form['username'].strip()
        password = request.form['password']

        conn = get_db_connection()
        if not conn:
            flash('Database connection failed', 'error')
            return render_template('auth/login.html')

        try:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute('''
                SELECT username, password_hash
                FROM users
                WHERE username = %s
            ''', (username,))
            user = cur.fetchone()

            if user and check_password_hash(user['password_hash'], password):
                session['username'] = user['username']
                flash(f'Welcome back, {username}!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Invalid username or password', 'error')

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




@app.route('/dashboard')
def dashboard():
    if not is_logged_in():
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection failed', 'error')
        return render_template('dashboard.html')
    
    try:
        cur = conn.cursor()
        user_data = {}
        
        # Get user's playlists
        cur.execute('''
            SELECT * FROM playlist WHERE basic_user_username = 
            (SELECT basic_user_username FROM basic_user WHERE username = %s)
        ''', (session['username'],))
        user_data['playlists'] = cur.fetchall()
        
        # Get user's events (if artist)
        if session['user_type'] == 'artist':
            cur.execute('''
                SELECT e.*, l.address, l.city, l.region, l.country 
                FROM event e 
                LEFT JOIN location l ON e.location_id = l.location_id 
                JOIN event_artist_user eau ON e.event_id = eau.event_id 
                WHERE eau.username = (SELECT username FROM artist_user WHERE username = %s)
            ''', (session['username'],))
            user_data['my_events'] = cur.fetchall()
        
        conn.close()
        return render_template('dashboard.html', user_data=user_data)
        
    except psycopg2.Error as e:
        flash(f'Dashboard error: {e}', 'error')
        conn.close()
        return render_template('dashboard.html', user_data={})



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


@app.route('/add_song', methods=['GET', 'POST'])
def add_song():
    login_check = require_login()
    if login_check:
        return login_check
    
    if request.method == 'POST':
        name = request.form['name']
        lyrics = request.form.get('lyrics', '')
        
        conn = get_db_connection()
        if not conn:
            flash('Database connection failed', 'error')
            return render_template('songs/add.html')
        
        try:
            cur = conn.cursor(cursor_factory=RealDictCursor)  # Use RealDictCursor
            cur.execute('''
                INSERT INTO song (name, lyrics) 
                VALUES (%s, %s) RETURNING song_id
            ''', (name, lyrics))
            
            song_id = cur.fetchone()['song_id']
            
            # Associate song with artist if current user is an artist
            if session.get('user_type') == 'artist':
                cur.execute('''
                    INSERT INTO song_artist_user (song_id, username) 
                    VALUES (%s, %s)
                ''', (song_id, session['username']))
            
            conn.commit()
            conn.close()
            
            flash('Song added successfully!', 'success')
            return redirect(url_for('songs'))
            
        except psycopg2.Error as e:
            flash(f'Error adding song: {e}', 'error')
            conn.close()
    
    return render_template('songs/add.html')






# ==================== PLAYLIST ROUTES ====================






@app.route('/playlists')
def playlists():
    login_check = require_login()
    if login_check:
        return login_check
    
    conn = get_db_connection()
    if not conn:
        return render_template('playlists/list.html', playlists=[])
    
    try:
        cur = conn.cursor()
        cur.execute('''
            SELECT p.*, u.username as owner_name 
            FROM playlist p 
            JOIN basic_user bu ON p.basic_user_id = bu.basic_user_id 
            JOIN users u ON bu.user_id = u.user_id 
            WHERE p.is_public = TRUE OR bu.user_id = %s 
            ORDER BY p.created_at DESC
        ''', (session['user_id'],))
        playlists = cur.fetchall()
        conn.close()
        return render_template('playlists/list.html', playlists=playlists)
        
    except psycopg2.Error as e:
        flash(f'Error loading playlists: {e}', 'error')
        conn.close()
        return render_template('playlists/list.html', playlists=[])

@app.route('/create_playlist', methods=['GET', 'POST'])
def create_playlist():
    login_check = require_login()
    if login_check:
        return login_check
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form.get('description', '')
        is_public = 'is_public' in request.form
        
        conn = get_db_connection()
        if not conn:
            flash('Database connection failed', 'error')
            return render_template('playlists/create.html')
        
        try:
            cur = conn.cursor()
            # Get basic_user_id
            cur.execute('SELECT basic_user_id FROM basic_user WHERE user_id = %s', (session['user_id'],))
            basic_user = cur.fetchone()
            
            if not basic_user:
                flash('Only basic users can create playlists', 'error')
                return render_template('playlists/create.html')
            
            cur.execute('''
                INSERT INTO playlist (name, description, is_public, basic_user_id, created_at) 
                VALUES (%s, %s, %s, %s, %s)
            ''', (name, description, is_public, basic_user['basic_user_id'], datetime.now()))
            
            conn.commit()
            conn.close()
            
            flash('Playlist created successfully!', 'success')
            return redirect(url_for('playlists'))
            
        except psycopg2.Error as e:
            flash(f'Error creating playlist: {e}', 'error')
            conn.close()
    
    return render_template('playlists/create.html')

@app.route('/playlist/<int:playlist_id>')
def playlist_detail(playlist_id):
    login_check = require_login()
    if login_check:
        return login_check
    
    conn = get_db_connection()
    if not conn:
        return redirect(url_for('playlists'))
    
    try:
        cur = conn.cursor()
        
        # Get playlist info
        cur.execute('''
            SELECT p.*, u.username as owner_name 
            FROM playlist p 
            JOIN basic_user bu ON p.basic_user_id = bu.basic_user_id 
            JOIN users u ON bu.user_id = u.user_id 
            WHERE p.playlist_id = %s
        ''', (playlist_id,))
        playlist = cur.fetchone()
        
        if not playlist:
            flash('Playlist not found', 'error')
            return redirect(url_for('playlists'))
        
        # Get playlist songs
        cur.execute('''
            SELECT s.*, u.username as artist_name 
            FROM song s 
            JOIN song_playlist sp ON s.song_id = sp.song_id 
            LEFT JOIN song_artist_user sau ON s.song_id = sau.song_id 
            LEFT JOIN artist_user au ON sau.artist_user_id = au.artist_user_id 
            LEFT JOIN users u ON au.user_id = u.user_id 
            WHERE sp.playlist_id = %s 
            ORDER BY sp.added_at
        ''', (playlist_id,))
        songs = cur.fetchall()
        
        # Get all songs for adding to playlist
        cur.execute('SELECT song_id, title FROM song ORDER BY title')
        all_songs = cur.fetchall()
        
        conn.close()
        return render_template('playlists/detail.html', playlist=playlist, songs=songs, all_songs=all_songs)
        
    except psycopg2.Error as e:
        flash(f'Error loading playlist: {e}', 'error')
        conn.close()
        return redirect(url_for('playlists'))

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
        
        cur.execute('''
            INSERT INTO song_playlist (playlist_id, song_id, added_at) 
            VALUES (%s, %s, %s)
        ''', (playlist_id, song_id, datetime.now()))
        
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Song added to playlist'})
        
    except psycopg2.Error as e:
        conn.close()
        return jsonify({'success': False, 'message': str(e)})




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
            WHERE e.date >= CURRENT_DATE
            ORDER BY e.date ASC
        ''')
        events = cur.fetchall()
        conn.close()
        return render_template('events/list.html', events=events)
        
    except psycopg2.Error as e:
        flash(f'Error loading events: {e}', 'error')
        conn.close()
        return render_template('events/list.html', events=[])


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
        return render_template('events/create.html', locations=[])

    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Handle form submission
        if request.method == 'POST':
            description = request.form.get('description', '')
            date = request.form.get('date')
            conditions = request.form.get('conditions', '')
            location_id = request.form.get('location_id')

            # Insert event
            cur.execute('''
                INSERT INTO event (location_id, description, date, conditions) 
                VALUES (%s, %s, %s, %s) RETURNING event_id
            ''', (location_id, description, date, conditions))
            
            event_id = cur.fetchone()['event_id']

            # Associate event with artist if user is an artist
            if session.get('user_type') == 'artist':
                cur.execute('''
                    INSERT INTO event_artist_user (event_id, artist_user_id) 
                    SELECT %s, event_id FROM artist_user WHERE username = %s
                ''', (event_id, session['username']))

            conn.commit()
            conn.close()

            flash('Event created successfully!', 'success')
            return redirect(url_for('events'))

        # Get locations for dropdown
        cur.execute('SELECT location_id, country, region, city, address FROM location ORDER BY city')
        locations = cur.fetchall()
        conn.close()

        return render_template('events/create.html', locations=locations)

    except psycopg2.Error as e:
        flash(f'Error creating event: {e}', 'error')
        conn.close()
        return render_template('events/create.html', locations=[])





# ==================== MERCHANDISE ROUTES ====================


@app.route('/merchandise')
def merchandise():
    conn = get_db_connection()
    if not conn:
        return render_template('merchandise/list.html', products=[])
    
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute('SELECT * FROM merchandise_product ORDER BY name')
        products = cur.fetchall()
        conn.close()
        return render_template('merchandise/list.html', products=products)
        
    except psycopg2.Error as e:
        flash(f'Error loading merchandise: {e}', 'error')
        conn.close()
        return render_template('merchandise/list.html', products=[])


@app.route('/add_merchandise', methods=['GET', 'POST'])
def add_merchandise():
    login_check = require_login()
    if login_check:
        return login_check
    
    if session.get('user_type') not in ['artist', 'manager']:
        flash('Only artists and managers can add merchandise', 'error')
        return redirect(url_for('merchandise'))
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form.get('description', '')
        price = request.form['price']
        stock_quantity = request.form['stock_quantity']
        category = request.form.get('category', '')

        conn = get_db_connection()
        if not conn:
            flash('Database connection failed', 'error')
            return render_template('merchandise/add.html')
        
        try:
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO merchandise_product (name, description, price, stock_quantity, category, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (name, description, price, stock_quantity, category, datetime.now()))
            
            conn.commit()
            conn.close()
            
            flash('Merchandise added successfully!', 'success')
            return redirect(url_for('merchandise'))
            
        except psycopg2.Error as e:
            flash(f'Error adding merchandise: {e}', 'error')
            conn.close()
    
    return render_template('merchandise/add.html')



# ==================== SEARCH ROUTE ====================




@app.route('/search')
def search():
    query = request.args.get('q', '').strip()
    if not query:
        return render_template('search.html', results=None, query='')

    conn = get_db_connection()
    if not conn:
        flash('Database connection failed', 'error')
        return render_template('search.html', results=None, query=query)

    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        search_pattern = f'%{query}%'
        results = {
            'artists': [],
            'songs': [],
            'events': [],
            'playlists': []
        }

        # Search artists
        cur.execute('''
            SELECT u.username, au.genre, au.biography 
            FROM users u
            JOIN artist_user au ON u.username = au.username
            WHERE u.username ILIKE %s OR au.genre ILIKE %s OR au.biography ILIKE %s
        ''', (search_pattern, search_pattern, search_pattern))
        results['artists'] = cur.fetchall()

        # Search songs
        cur.execute('''
            SELECT s.name AS title, u.username AS artist_name
            FROM song s
            JOIN song_artist_user sau ON s.song_id = sau.song_id
            JOIN artist_user au ON sau.username = au.username
            JOIN users u ON au.username = u.username
            WHERE s.name ILIKE %s
        ''', (search_pattern,))
        results['songs'] = cur.fetchall()

        # Search events
        cur.execute('''
            SELECT e.event_id, e.description, e.date, l.city AS location_name
            FROM event e
            LEFT JOIN location l ON e.location_id = l.location_id
            WHERE e.description ILIKE %s
        ''', (search_pattern,))
        results['events'] = cur.fetchall()

        # Search playlists (public only)
        cur.execute('''
            SELECT p.playlist_id, p.name, u.username AS owner_name
            FROM playlist p
            JOIN basic_user bu ON p.basic_user_id = bu.basic_user_id
            JOIN users u ON bu.username = u.username
            WHERE p.is_public = TRUE AND p.name ILIKE %s
        ''', (search_pattern,))
        results['playlists'] = cur.fetchall()

        conn.close()
        return render_template('search.html', results=results, query=query)

    except psycopg2.Error as e:
        flash(f'Search error: {e}', 'error')
        conn.close()
        return render_template('search.html', results=None, query=query)




if __name__ == '__main__':
    app.run(debug=True)