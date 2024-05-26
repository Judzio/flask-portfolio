from flask import Flask, render_template, request
import git
import os

app = Flask(__name__)

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


@app.errorhandler(404)
def page_not_found(error):
    return render_template('error404.html'), 404

@app.errorhandler(Exception)
def server_error(error):
    return render_template('error.html'), 500

if __name__ == '__main__':
    app.run(debug=True)
