from flask import Flask, request, render_template, redirect, url_for, jsonify
from PIL import Image, ImageOps, ExifTags
import os
import subprocess

# inicijalizacija
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploaded_images'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# korekcija slike
def correct_orientation(image):
    rotation_info = ""
    try:
        exif = image._getexif()
        if exif is not None:
            orientation_key = next((k for k, v in ExifTags.TAGS.items() if v == 'Orientation'), None)
            orientation = exif.get(orientation_key)
            print(f"Orginalna EXIF orijentacija: {orientation}")
            if orientation == 3:
                image = image.rotate(180, expand=True)
                rotation_info = "Rotiram 180 stepeni"
            elif orientation == 6:
                image = image.rotate(270, expand=True)
                rotation_info = "Rotiram 270 stepeni"
            elif orientation == 8:
                image = image.rotate(90, expand=True)
                rotation_info = "Rotiram 90 stepeni"
            else:
                rotation_info = "Rotacija nije potrebna"
        else:
            rotation_info = "EXIF oorijentacija nije pronadjena"
    except Exception as e:
        rotation_info = f"greska: {e}"
    print(rotation_info)
    return image, rotation_info

# renderuj htlm.index
@app.route('/')
def index():
    return render_template('index.html')

# upload
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:  # ovo je sve provjera
        return redirect('/')
    file = request.files['file']
    if file.filename == '':
        return redirect('/')
    if file:
        filename = file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Otvori sliku ,Pillow
        img = Image.open(file_path)
        original_width, original_height = img.size
        print(f"Orginalna velicina slike: {original_width}x{original_height}")

        # ispravi orijentaciju
        img, rotation_info = correct_orientation(img)


        width, height = img.size
        print(f"Prepravljena na: {width}x{height}")

        if height > width:  # verticalan slika
            target_size = (1080, 1920)
            resize_info = "Promijenjen u : 1080x1920"
        else:  # horizontalna
            target_size = (1920, 1080)
            resize_info = "Promijenjen u 1920x1080"

        # promjeni velicnu (resize-uj ih)
        img = ImageOps.fit(img, target_size, Image.LANCZOS)
        resized_width, resized_height = img.size
        print(f"{resize_info}, Promijenjen u: {resized_width}x{resized_height}")

        # sacuvaj je
        resized_path = os.path.join(app.config['UPLOAD_FOLDER'], 'resized_' + filename)
        img.save(resized_path)

        return render_template('index.html', filename='resized_' + filename)
    return redirect(url_for('index'))

# pozovi predikcija.py
@app.route('/process', methods=['POST'])
def process_file():
    filename = request.form.get('filename')
    if not filename:
        return redirect(url_for('index'))

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    # pozovi
    result = subprocess.run(['python', 'predikcija.py', file_path], capture_output=True, text=True)

    # Sacuvaj
    processed_image_path = file_path.replace(".", "_obradjena.")

    if os.path.exists(processed_image_path):
        return jsonify({'processed_image_url': url_for('static', filename='uploaded_images/' + os.path.basename(processed_image_path))})
    else:
        return jsonify({'error': result.stderr})

if __name__ == '__main__':
    app.run(debug=True)
