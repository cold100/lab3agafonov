import os
from flask import Flask, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm, RecaptchaField
from PIL import Image, ImageDraw
import numpy as np
import matplotlib.pyplot as plt


UPLOAD_FOLDER = 'images'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])


app = Flask(__name__, template_folder="templates", static_folder="images")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["SECRET_KEY"] = "eifwkuwebfwejubfwj23123857y28wad"
app.config["RECAPTCHA_PUBLIC_KEY"] = "6LdHWLkaAAAAAFJioRgnPe-YNl4xxUhNaLTkCZno"
app.config["RECAPTCHA_PRIVATE_KEY"] = "6LdHWLkaAAAAANYhxdrrw7ujYb-3g4aZGOZcWcN8"
colours = ['Red', 'Blue', 'Black', 'Orange']

class ReCaptcha(FlaskForm):
    recaptcha = RecaptchaField()

@app.route('/img/<filename>+<color>')
def uploaded_file(filename, color):
    try:
        original = Image.open("./images/"+filename)
        original_array = np.array(original)
        original_array_r = original_array[:,:,0].flatten()
        original_array_g = original_array[:, :, 1].flatten()
        original_array_b = original_array[:, :, 2].flatten()
        original_array = np.array([original_array_r,original_array_g,original_array_b])
        original_array = original_array.transpose()
        plt.hist(original_array)
        plt.savefig("./images/plots/original_plot/"+filename+".png")
        originalplot_path = str('../images/plots/original_plot/'+filename+".png")
        new_img = original.convert('RGB')
        draw = ImageDraw.Draw(new_img)
        x,y = new_img.size
        draw.rectangle((x-int(x/4), int(y/4),int(x/4),int((x-y)/5)+int(y/4)), fill=color)
        draw.rectangle(((int((x-y)/5)+int(y/4))*2, int(y/12), x-(int((x-y)/5)+int(y/4))*2, int(y/1.2)), fill=color)
        new_array = np.array(new_img)
        new_array_r = new_array[:, :, 0].flatten()
        new_array_g = new_array[:, :, 1].flatten()
        new_array_b = new_array[:, :, 2].flatten()
        new_array = np.array([new_array_r, new_array_g, new_array_b])
        new_array = new_array.transpose()
        plt.hist(new_array)
        plt.savefig('./images/plots/new_plot/'+ filename+".png")
        new_img.save("./images/new"+filename)
        new_filename = str("../images/new"+filename)
        newplot_path = str('../images/plots/new_plot/'+filename+".png")
    except FileNotFoundError:
        print("Файл не найден")
    return render_template('/image.html', old_image=filename, new_image =new_filename,colour = color, old_plot=originalplot_path, new_plot=newplot_path)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    form = ReCaptcha()
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename) and form.validate_on_submit():
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            select = request.form['colour']
            return redirect(url_for('uploaded_file', filename=filename, color=select))
    return render_template('index.html', colours = colours, form = form)

if __name__ == '__main__':
    app.run(debug=False)