"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/
This file creates your application.
"""
import os
import re
from app import app
from flask import render_template, request, redirect, url_for, flash, session, abort
from forms import UploadForm
from werkzeug.utils import secure_filename, CombinedMultiDict


###
# Routing for your application.
###
image_file = re.compile(r'^.+\.(?:jpg|jpeg|png|gif|jpe|svg|bmp)$')


def get_uploaded_images(rootdir):
    for root, dirs, files in os.walk(rootdir):
        for file in files:
            yield os.path.join(root[root.index("static")+7:], file).replace("\\", "/")
        for directory in dirs:
            yield get_uploaded_images(directory)


@app.route('/files')
def files():
    return render_template('files.html', static_files=get_uploaded_images(app.config['UPLOADED_IMAGES_DEST']))

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')


@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html', name="Mary Jane")


@app.route('/upload', methods=['POST', 'GET'])
def upload():
    if not session.get('logged_in'):
        abort(401)

    # Instantiate your form class

    if request.method == 'POST':
        form = UploadForm()
        if form.is_submitted() and form.photo.data:
            if not image_file.match(form.photo.data.filename):
                return render_template('upload.html', form=UploadForm(), error=True)
            photo = form.photo.data
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config['UPLOADED_IMAGES_DEST'], filename))

            flash('File Saved', 'success')
            return redirect(url_for('home'))

    return render_template('upload.html', form=UploadForm(), error=False)


@app.route('/login', methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME'] or request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid username or password'
        else:
            session['logged_in'] = True
            
            flash('You were logged in', 'success')
            return redirect(url_for('upload'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out', 'success')
    return redirect(url_for('home'))


###
# The functions below should be applicable to all Flask apps.
###

# Flash errors from the form if validation fails
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
), 'danger')

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port="8080")
