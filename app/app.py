from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_from_directory
import llm_query
from psycopg.errors import UniqueViolation
import auth
import db
import requests
import os
import shutil


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

    # Find information about the given username.
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

    # Only login if the password and hash match.
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

    # Hash the password before putting it in the database.
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
        # We're relying on the `username` column's `unique` constraint.
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
    # You must be logged in to regenerate your API key.
    if 'user' not in session:
        return 'Unauthorized', 401
    user_id = session['user']
    assert isinstance(user_id, int)
    # Generate a new key and insert it into the database.
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
    # Return the new API key.
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
        
        # API endpoint of the FastAPI service
        api_url = "http://localhost:8000/new_job"  # Adjust if hosted elsewhere

        # Send the request to FastAPI's /new_job endpoint
        response = requests.post(api_url, data={
            'product': field1,
            'audience': field2,
            'goal': field3
        })

        if response.status_code == 201:
            job_id = response.json().get('id')
            return jsonify({'message': 'Job started', 'job_id': job_id})
        else:
            return jsonify({'error': 'Failed to create job', 'details': response.json()}), response.status_code

    return render_template('ad_generation.html')




@app.route('/check_status', methods=['GET'])
def check_status():
    task_id = request.args.get('task_id')

    if not task_id:
        return jsonify({'error': 'Missing task_id'}), 400

    api_url = f"http://localhost:8000/job/{task_id}"

    response = requests.get(api_url)

    if response.status_code == 200:
        print(response.json())

        src_folder = f"/home/wcward/Documents/EagleHacks2025_Project/api/api/static/{task_id}"
        dest_folder = f"/home/wcward/Documents/EagleHacks2025_Project/app/static/{task_id}"

        try:
            if os.path.exists(src_folder):
                if not os.path.exists(dest_folder):
                    os.makedirs(dest_folder)  
                
                for item in os.listdir(src_folder):
                    src_path = os.path.join(src_folder, item)
                    dest_path = os.path.join(dest_folder, item)
                    
                    if os.path.isdir(src_path):
                        shutil.copytree(src_path, dest_path, dirs_exist_ok=True)
                    else:
                        shutil.copy2(src_path, dest_path)
            else:
                print("Source folder does not exist")
        except Exception as e:
            print(f"File copy failed: {e}")

        return jsonify(response.json()), 200

    elif response.status_code == 202:
        return jsonify({'message': 'Job is still in progress'}), 202
    elif response.status_code == 404:
        return jsonify({'error': 'Job not found'}), 404
    else:
        return jsonify({'error': 'Failed to fetch job status', 'details': response.json()}), response.status_code



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

# --------------- CSV FILE DOWNLOAD -----------------
@app.route("/marketing_data.csv")
def serve_csv():
    if os.path.exists("marketing_data.csv"):
        return send_from_directory(".", "marketing_data.csv", mimetype="text/csv")


    else:
        return jsonify({"error": "CSV file not found"}), 404 
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5050)
