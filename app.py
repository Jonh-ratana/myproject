from flask import Flask, request , render_template,url_for,redirect, flash,session
from flask_mysqldb import MySQL
import os
from werkzeug.utils import secure_filename
from flask_bcrypt import Bcrypt

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'project_flask'
UPLOAD_FOLDER = 'static/image'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
mysql = MySQL(app)

app.secret_key = 'a_very_secure_secret_key'      
bcrypt = Bcrypt(app) # Initialize Bcrypt
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@app.route('/')
@app.route('/home')
def home():
    return render_template('home_page.html')
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if the username already exists
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM users WHERE username = %s', [username])
        existing_user = cur.fetchone()
        cur.close()

        if existing_user:
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('register'))

        # Hash the password using Flask-Bcrypt
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        # Insert into the database
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, hashed_password))
        mysql.connection.commit()
        cur.close()

        # Set session variables (avoid storing passwords)
        session['username'] = username

        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('home'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        cur = mysql.connection.cursor()
        cur.execute('SELECT password FROM users WHERE username = %s', [username])
        data = cur.fetchone()
        cur.close()
        
        if data and bcrypt.check_password_hash(data[0], password):
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('form'))
        else:
            flash('Login failed. Check your username and/or password.', 'danger')
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/logout', methods = ['GET','POST'])
def logout():
    session.pop('username', None)  # Remove the username from the session
    flash('You have been logged out.', 'info')  # Provide feedback to the user
    return redirect(url_for('home'))  # Redirect to the login page

@app.route('/dashboard', methods = ['GET' , 'POST'])
def form():
    if 'username' not in session:
        flash('You need to log in to access this page.', 'warning')
        return redirect(url_for('login'))
    

    if request.method == 'POST':
        name = request.form['name']
        community = request.form['community']
        village = request.form['village']
        discription = request.form['discription']
        file = request.files['file']
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
        else:
            filename = None
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO client (name, community, village, discription, file_path) VALUES (%s, %s, %s,%s, %s)', (name, community, village,discription, filename))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('show'))
    return redirect(url_for('show'))

@app.route('/show')
def show():
    if 'username' not in session:
        flash('You need to log in to access this page.', 'warning')
        return redirect(url_for('login'))


    cur = mysql.connection.cursor()
    cur.execute('SELECT id,name,community,village,discription,file_path FROM client')
    data = cur.fetchall()
    cur.close()
    return render_template('table.html', data=data)

@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    if 'username' not in session:
        flash('You need to log in to access this page.', 'warning')
        return redirect(url_for('login'))
        
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM client WHERE id = %s', [id])
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('show'))  # Redirect to show after successful deletion

@app.route('/detail/<int:id>')
def detail(id):
    if 'username' not in session:
        flash('You need to log in to access this page.', 'warning')
        return redirect(url_for('login'))   
        
    cur = mysql.connection.cursor()
    cur.execute('SELECT id,name,community,village,discription, file_path FROM client WHERE id = %s', [id])
    data = cur.fetchall()

    if data:
        return render_template('detail.html', data = data)
    else:
        flash('Record not found', 'warning')
        return redirect(url_for('detail'))
        

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):

    if 'username' not in session:
        flash('You need to log in to access this page.', 'warning')
        return redirect(url_for('login'))
    

    cur = mysql.connection.cursor()
    if request.method == 'POST':
        name = request.form['name']
        community = request.form['community']
        village = request.form['village']
        discription = request.form['discription']  # Note the change here
        file = request.files['file']

        # Check if a new file was uploaded
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
        else:
            # Keep the old file path if no new file is uploaded
            filename = request.form['existing_file_path']

        # Update record in the database
        cur.execute(
            'UPDATE client SET name=%s, community=%s, village=%s, discription=%s, file_path=%s WHERE id=%s',
            (name, community, village, discription, filename, id)  # Note the change here
        )
        mysql.connection.commit()
        cur.close()
        flash('Record updated successfully!', 'success')
        return redirect(url_for('show'))

    else:
        # Retrieve the existing record to pre-fill the form
        cur.execute('SELECT id, name, community, village, discription, file_path FROM client WHERE id=%s', [id])  # Note the change here
        data = cur.fetchone()
        cur.close()

        if data:
            return render_template('edit.html', data=data)
        else:
            flash('Record not found', 'warning')
            return redirect(url_for('show'))


@app.route('/add')
def add():
    if 'username' not in session:
        flash('You need to log in to access this page.', 'warning')
        return redirect(url_for('login'))
    return render_template('form.html')


if __name__ == '__main__':

    app.run(debug=True)