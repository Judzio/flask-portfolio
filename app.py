from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import git
import os

# Import Flask-Dance and necessary components for GitHub OAuth
from flask_dance.contrib.github import make_github_blueprint, github

# Initialize Flask app and SQLAlchemy
app = Flask(__name__)
app.secret_key = 'mati123'  # Replace with your secret key

# Configure SQLAlchemy database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///guestbook.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Import database models
from models import GuestbookEntry

# Flask-Dance GitHub Blueprint
github_bp = make_github_blueprint(client_id='Ov23lilWC6wCAowW6oTr',  # Replace with your GitHub OAuth app client ID
                                  client_secret='26072e8e5b47ace7d545c25f7d9267010fa54ca3',  # Replace with your GitHub OAuth app client secret
                                  redirect_to='github_login')

app.register_blueprint(github_bp, url_prefix='/github_login')

# GitHub OAuth callback route
@app.route('/github_login')
def github_login():
    if not github.authorized:
        return redirect(url_for('github.login'))
    resp = github.get('/user')
    assert resp.ok, resp.text
    # You can access user information like username using resp.json()['login']
    return redirect(url_for('home'))

# Example route to initiate GitHub OAuth login
@app.route('/login')
def login():
    return redirect(url_for('github.login'))

@app.route('/git_update', methods=['POST'])
def git_update():
    try:
        repo_path = './flask-portfolio'
        if not os.path.exists(repo_path):
            return 'Repository path does not exist', 404

        repo = git.Repo(repo_path)
        origin = repo.remotes.origin

        repo.create_head('main', origin.refs.main).set_tracking_branch(origin.refs.main).checkout()
        origin.pull()

        return 'Repository updated successfully', 200
    except git.exc.GitCommandError as e:
        return f'An error occurred while updating the repository: {str(e)}', 500
    except Exception as e:
        return f'An unexpected error occurred: {str(e)}', 500

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/aboutme')
def about_me():
    return render_template('aboutme.html')

@app.route('/gallery')
def gallery():
    return render_template('gallery.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    if request.method == 'POST':
        print("Form submitted successfully")
    return render_template('submit_contact.html')

@app.route('/guestbook')
def guestbook():
    messages = GuestbookEntry.query.order_by(GuestbookEntry.date.desc()).all()
    return render_template('guestbook.html', messages=messages)

@app.route('/submit_guestbook', methods=['POST'])
def submit_guestbook():
    nick = request.form['nick']
    text = request.form['text']
    date = datetime.now()
    new_entry = GuestbookEntry(nick=nick, text=text, date=date)
    db.session.add(new_entry)
    db.session.commit()
    return redirect(url_for('guestbook'))

@app.route('/delete_message/<int:message_id>', methods=['DELETE'])
def delete_message(message_id):
    try:
        message = GuestbookEntry.query.get(message_id)
        if not message:
            return 'Message not found', 404

        db.session.delete(message)
        db.session.commit()

        return 'Message deleted successfully', 200
    except Exception as e:
        return f'An unexpected error occurred: {str(e)}', 500

@app.route('/update_message/<int:message_id>', methods=['POST'])
def update_message(message_id):
    try:
        message = GuestbookEntry.query.get(message_id)
        if not message:
            return 'Message not found', 404

        nick = request.form['nick']
        text = request.form['text']

        message.nick = nick
        message.text = text

        db.session.commit()

        return 'Message updated successfully', 200
    except Exception as e:
        return f'An unexpected error occurred: {str(e)}', 500

@app.route('/edit_message/<int:message_id>', methods=['GET'])
def edit_message(message_id):
    try:
        message = GuestbookEntry.query.get(message_id)
        if not message:
            return 'Message not found', 404

        return render_template('edit_message.html', message=message)
    except Exception as e:
        return f'An unexpected error occurred: {str(e)}', 500

@app.errorhandler(404)
def page_not_found(error):
    return render_template('error404.html'), 404

@app.errorhandler(Exception)
def server_error(error):
    return render_template('error.html'), 500

if __name__ == '__main__':
    app.run(debug=True)
