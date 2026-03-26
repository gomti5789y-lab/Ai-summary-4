import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from PIL import Image
import pytesseract
import google.generativeai as genai

app = Flask(__name__)
app.secret_key = "my_secret_key_786" # Isse badal sakte hain

# Database Setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

# Gemini AI Setup (Yahan apni API Key dalein)
genai.configure(api_key="YOUR_GEMINI_API_KEY")
model = genai.GenerativeModel('gemini-pro')

# User Table
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = User(username=request.form['username'], password=request.form['password'])
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username'], password=request.form['password']).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session: return redirect(url_for('login'))
    
    extracted_text = ""
    if request.method == 'POST':
        file = request.files['file']
        if file:
            img = Image.open(file)
            extracted_text = pytesseract.image_to_string(img)
    return render_template('dashboard.html', text=extracted_text)

@app.route('/summarize', methods=['POST'])
def summarize():
    data = request.json
    raw_text = data.get('text')
    response = model.generate_content(f"Summarize this text clearly: {raw_text}")
    return jsonify({"summary": response.text})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
