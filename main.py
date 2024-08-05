from __future__ import print_function
from flask_bootstrap import Bootstrap
import config
import os
from flask import Flask, flash, request, redirect, url_for, render_template
from app import app
from app import routes

from werkzeug.utils import secure_filename
import binascii
from PIL import Image
import numpy as np
import scipy
import scipy.misc
import scipy.cluster
import imageio

path_to_file = input('what is the path to the image? :  ')
im = Image.open(path_to_file)
NUM_CLUSTERS = 5

app.config['UPLOAD_FOLDER'] = path_to_file + '\cluster.png'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1920 * 1080

app = Flask(__name__)
app.config.from_object('config')
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def common_colors(im):
    ar = np.asarray(im)
    shape = ar.shape
    ar = ar.reshape(scipy.product(shape[:2]), shape[2]).astype(float)
    codes, dist = scipy.cluster.vq.kmeans(ar, NUM_CLUSTERS)

    vecs, dist = scipy.cluster.vq.vq(ar, codes)
    counts, bins = scipy.histogram(vecs, len(codes))

    index_max = scipy.argmax(counts)
    peak = codes[index_max]
    colour = binascii.hexlify(bytearray(int(c) for c in peak).decode('ascii'))

    most_common = ('most frequent is %s (#%s)' % (peak, colour))

    c = ar.copy()

    for i, code in enumerate(codes):
        c[scipy.r_[scipy.where(vecs == i), :]] = code
    imageio.imwrite('clusters.png', c.reshape(*shape).astype(np.uint8))


common_colors(im)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def upload_form():
    return render_template('upload.html')


@app.route('/', methods=["POST"])
def upload_image():
    if 'file' not in request.files:
        flash("No such File Part")
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No Image Selected For Upload')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        print('upload_image filename: ' + filename)
        flash("uploaded successfully")
        return render_template('upload.html', filename=filename)
    else:
        flash("Allowed image extensions include: jpg, png, jpeg, gif")
        return redirect(request.url)


@app.route('/display/<filename>')
def display_final(filename):
    return redirect(url_for('Static', filename=path_to_file + filename), code=301)


if __name__ == "__main__":
    app.run(debug=False)
