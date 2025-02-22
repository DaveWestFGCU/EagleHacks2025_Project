from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import llm_query

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
    
    if username == 'admin' and password == 'password':  # Replace with real authentication logic
        session['user'] = username
        return redirect(url_for('dashboard'))
    
    return render_template('login.html', error='Invalid credentials')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# ----------------- DASHBOARD -----------------
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

# ----------------- AD GENERATION -----------------
@app.route('/ad_generation', methods=['GET', 'POST'])
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
