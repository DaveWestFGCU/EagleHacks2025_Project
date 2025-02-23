from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import llm_query
from psycopg.errors import UniqueViolation
import auth
import db

app = Flask(__name__, static_url_path='/static')
app.secret_key = 'your_secret_key'  # Needed for session management

# ----------------- LOGIN -----------------
@app.route('/')
def login():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def authenticate():
    username = request.form.get('username')
    password = request.form.get('password')

    if not username:
        return render_template('login.html', error='Username cannot be empty')

    if not password:
        return render_template('login.html', error='Password cannot be empty')

    with db.connect() as conn, conn.cursor() as cursor:
        record = cursor.execute(
            """
            select user_id, pw_hash, salt
            from users
            where username = %s;
            """,
            (username,),
        ).fetchone()

    if not record:
        return render_template('login.html', error='Invalid credentials')

    user_id = record.user_id
    pw_hash = record.pw_hash
    salt = record.salt

    assert isinstance(user_id, int)
    assert isinstance(pw_hash, bytes)
    assert isinstance(salt, bytes)

    if auth.pw_matches_hash(pw=password, salt=salt, hash=pw_hash):
        session['user'] = user_id
        return redirect(url_for('dashboard'))

    return render_template('login.html', error='Invalid credentials')


@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')

    if not username:
        return render_template('login.html', error='Username cannot be empty')

    if not password:
        return render_template('login.html', error='Password cannot be empty')

    salt = auth.generate_salt()
    pw_hash = auth.hash_pw(pw=password, salt=salt)
    api_key = auth.generate_api_key()

    try:
        with db.connect() as conn, conn.cursor() as cursor:
            cursor.execute(
                """
                insert into users (username, pw_hash, salt, api_key)
                values (%s, %s, %s, %s);
                """,
                (username, pw_hash, salt, api_key),
            )
    except UniqueViolation:
        return render_template('login.html', error='Username taken')
    else:
        return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))


# ----------------- API KEY MANAGEMENT -----------------
@app.route('/regenerate_api_key')
def regenerate_api_key():
    if 'user' not in session:
        return 'Unauthorized', 401
    user_id = session['user']
    assert isinstance(user_id, int)
    api_key = auth.generate_api_key()
    with db.connect() as conn, conn.cursor() as cursor:
        cursor.execute(
            """
            update users
            set api_key = %s
            where user_id = %s;
            """,
            (api_key, user_id),
        )
    return api_key


# ----------------- DASHBOARD -----------------
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

# ----------------- AD GENERATION -----------------
@app.route('/new_job', methods=['GET', 'POST'])
def ad_generation():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        field1 = request.form.get('field1')
        field2 = request.form.get('field2')
        field3 = request.form.get('field3')
        
        if not field1 or not field2 or not field3:
            return jsonify({'error': 'Missing fields'}), 400
        
        data = {
            'Product/Service Overview': field1,
            'Target Audience': field2,
            'Campaign Goal': field3
        }
        
        result = llm_query.query_model('ad_gen', data)
        return jsonify({'generated_ad': result})
    
    return render_template('ad_generation.html')


@app.route('/check_status', methods=['GET'])
def check_status():
    task_id = request.args.get('task_id')
    
    return jsonify({'status': 'done'}), 200

# ----------------- MARKET DATA VIEWER -----------------
@app.route('/market_data_viewer')
def market_data_viewer():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('market_data_viewer.html')

# ----------------- ERROR HANDLING -----------------
@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True, port=5050)
