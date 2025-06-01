from flask import Flask, request, render_template, redirect, url_for, flash
import os
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for flashing messages

# Configure upload folder
UPLOAD_FOLDER = 'static/uploaded'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Load trained model
model = load_model('model.h5')

# Define class labels (update this list to match your model’s output)
class_labels = [
    'Apple___Black_rot', 'Apple___healthy', 'Corn___Cercospora_leaf_spot',
    'Corn___Common_rust', 'Corn___healthy', 'Potato___Early_blight',
    'Potato___Late_blight', 'Potato___healthy', 'Tomato___Bacterial_spot',
    'Tomato___healthy'
]

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Preprocess image
            img = image.load_img(file_path, target_size=(128, 128))
            img_array = image.img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0) / 255.0  # Normalize

            # Predict
            prediction = model.predict(img_array)
            predicted_class = class_labels[np.argmax(prediction)]

            # Render result page
            return render_template('result.html',
                                   prediction=predicted_class,
                                   image_url=url_for('static', filename='uploaded/' + filename))

        else:
            flash('Allowed file types are png, jpg, jpeg, gif')
            return redirect(request.url)

    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)
