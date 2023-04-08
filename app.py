from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_pymongo import PyMongo
from flask_wtf.file import FileField, FileRequired, FileAllowed
from flask_wtf import FlaskForm
from wtforms import StringField, FileField, SubmitField, validators
from wtforms.validators import DataRequired
from PIL import Image
import os
from werkzeug.utils import secure_filename
from random import shuffle
from flask import flash
from bson import json_util
from flask_sqlalchemy import SQLAlchemy
from pymongo import MongoClient
from bson.objectid import ObjectId
from flask import json
import random
import html
import bson

class YourImageUploadForm(FlaskForm):
    title = StringField('Image Title', validators=[DataRequired()])
    image = FileField('Image', validators=[FileRequired(), FileAllowed(['jpg', 'png'], 'Images only!')])
    submit = SubmitField('Upload')

client = MongoClient('mongo_database')
db = client['mydatabase']


app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb:mongo_URI'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'your_secret_key'
mongo = PyMongo(app)

db = SQLAlchemy(app)

@app.template_filter('tojson')
def tojson(obj):
    return json.dumps(obj)


class ImageUploadForm(FlaskForm):
    title = StringField('Title', [validators.Length(min=1, max=100)])
    image = FileField('Image', [validators.DataRequired()])
    submit = SubmitField('Upload')

class FilterForm(FlaskForm):
    min_elo = StringField('Min ELO')
    max_elo = StringField('Max ELO')
    submit = SubmitField('Filter')

def save_image(file, size=(1024, 1024)):
    filename = secure_filename(file.filename)
    img = Image.open(file)
    img.thumbnail(size)
    img.save(os.path.join('static', 'images', filename))
    return filename    

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_two_random_images():
    images = mongo.db.images
    count = images.count_documents({})

    if count < 2:
        return None, None

    # Select two distinct random indices
    random_indices = random.sample(range(0, count), 2)

    cursor = images.aggregate([{"$sample": {"size": count}}])
    all_images = list(cursor)

    img_a = all_images[random_indices[0]]
    img_b = all_images[random_indices[1]]

    return img_a, img_b

@app.route('/compare', methods=['GET', 'POST'])
def compare_images():
    if request.method == 'POST':
        winner_id = request.form['winner']
        loser_id = request.form['loser']
        winner = mongo.db.images.find_one({'_id': ObjectId(winner_id)})
        loser = mongo.db.images.find_one({'_id': ObjectId(loser_id)})
        winner_elo = winner['elo']
        loser_elo = loser['elo']
        winner_new_elo, loser_new_elo = update_elo(winner_elo, loser_elo)
        mongo.db.images.update_one({'_id': ObjectId(winner_id)}, {'$set': {'elo': winner_new_elo}})
        mongo.db.images.update_one({'_id': ObjectId(loser_id)}, {'$set': {'elo': loser_new_elo}})

    img_a, img_b = get_two_random_images()

    if img_a is not None:
        img_a_data = json.loads(json_util.dumps(img_a))
    else:
        img_a_data = None

    if img_b is not None:
        img_b_data = json.loads(json_util.dumps(img_b))
    else:
        img_b_data = None

    if request.method == 'GET':
        return render_template('compare.html', img_a=img_a_data, img_b=img_b_data)
    else:
        return render_template('compare.html', img_a=img_a_data, img_b=img_b_data)

@app.route('/delete-image/<image_id>', methods=['POST'])
def delete_image(image_id):
    print(f"Deleting image with ID: {image_id}")
    result = mongo.db.images.delete_one({'_id': ObjectId(image_id)})
    print(result.deleted_count)
    return redirect(url_for('home'))

@app.route('/', methods=['GET', 'POST'])
def home():
    print("Home route called")
    form = YourImageUploadForm()  # Create the form instance
    filter_form = FilterForm()
    min_elo = None
    max_elo = None

    if form.validate_on_submit():
        image = form.image.data
        title = form.title.data
        filename = save_image(image)
        print(f"Image saved: {filename}")  # Add this line
        result = mongo.db["images-elo"].insert_one({
            'title': title,
            'filename': filename,
            'elo': 1000
        })
        print(f"Image inserted with ID: {result.inserted_id}")  # Move this line inside the if block

    if filter_form.validate_on_submit():
        min_elo = int(filter_form.min_elo.data) if filter_form.min_elo.data else None
        max_elo = int(filter_form.max_elo.data) if filter_form.max_elo.data else None

    query = {}

    if min_elo is not None:
        query['elo'] = {'$gte': min_elo}

    if max_elo is not None:
        query['elo'] = query.get('elo', {})
        query['elo']['$lte'] = max_elo

    print("Query:", query)

    images_cursor = mongo.db.images.find(query).sort("elo", -1)
    images = list(images_cursor)

    print("Images in home route:", [img for img in images])
    return render_template('home.html', images=images, filter_form=filter_form, form=form)

@app.route("/upload", methods=["POST"])
def upload_image():
    form = YourImageUploadForm()

    if form.validate_on_submit():
        image = form.image.data
        title = form.title.data
        filename = save_image(image)
        result = mongo.db.images.insert_one({
            'title': title,
            'filename': filename,
            'elo': 1000
        })
        print(f"Image inserted with ID: {result.inserted_id}")  # Add this line
        image_url = url_for("static", filename=f"images/{filename}")
        return jsonify({"url": image_url, "filename": filename})

    print("Image URL and filename:", image_url, filename)
    return jsonify({"error": "Invalid form data"})

from flask import jsonify, request

@app.route('/update-elo', methods=['POST'])
def update_elo_route():
    print('update_elo endpoint reached')
    # Get the selected image ID and the winning image ID from the request data
    selected_image_id = request.json['id_a']
    winning_image_id = request.json['winner']

    # Get the image data for the selected and winning images from the database
    selected_image = mongo.db.images.find_one({'_id': ObjectId(selected_image_id)})
    winning_image = mongo.db.images.find_one({'_id': ObjectId(winning_image_id)})

    # Calculate the new ELO values for the selected and winning images
    k_factor = 32
    selected_elo = selected_image['elo']
    winning_elo = winning_image['elo']
    expected_win = 1 / (1 + 10**((winning_elo - selected_elo) / 400))
    actual_win = 1
    selected_new_elo = selected_elo + k_factor * (actual_win - expected_win)
    winning_new_elo = winning_elo + k_factor * (1 - actual_win + expected_win)

    # Update the ELO values for the selected and winning images in the database
    mongo.db.images.update_one({'_id': ObjectId(selected_image_id)}, {'$set': {'elo': selected_new_elo}})
    mongo.db.images.update_one({'_id': ObjectId(winning_image_id)}, {'$set': {'elo': winning_new_elo}})

    # Return a JSON response indicating success
    return jsonify({'success': True})

def update_elo(winner_elo, loser_elo, k=32):
    winner_expected = 1 / (1 + 10 ** ((loser_elo - winner_elo) / 400))
    loser_expected = 1 / (1 + 10 ** ((winner_elo - loser_elo) / 400))

    winner_new_elo = winner_elo + k * (1 - winner_expected)
    loser_new_elo = loser_elo + k * (0 - loser_expected)

    return winner_new_elo, loser_new_elo


if __name__ == '__main__':
    app.run(debug=True, port=5000)
