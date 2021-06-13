import os

from flask import Flask, request, render_template,redirect,url_for
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import RadioField
from werkzeug.utils import secure_filename
from PIL import Image, ImageChops
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from numpy import transpose

UPLOAD_FOLDER = './static/images/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['SECRET_KEY']='6LcRtxQbAAAAANQ_wEKDLDmpFmUuFE4bEzB0B293'
app.config['RECAPTCHA_USE_SSL']= False
RECAPTCHA_PUBLIC_KEY='6Le59hobAAAAAFdSpa8vEvHEByDV7wIwL619sRzY'
RECAPTCHA_PRIVATE_KEY='6Le59hobAAAAAK10crhmg7kIprMx6HhFySkPNyEf'
app.config['RECAPTCHA_SECRET_KEY'] = '6Le59hobAAAAAK10crhmg7kIprMx6HhFySkPNyEf'
app.config['RECAPTCHA_PUBLIC_KEY'] = RECAPTCHA_PUBLIC_KEY
app.config['RECAPTCHA_PRIVATE_KEY'] = RECAPTCHA_PRIVATE_KEY
class Fields(FlaskForm):
    choice = RadioField(
        'Выберите опцию:', choices=[('1', 'Left/Right'), ('2', 'Up/down')],default='1')
    recaptcha = RecaptchaField()

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    form = Fields()
    if request.method == 'POST' and form.validate_on_submit():
        file = request.files['file']
        choice = int(form.choice.data)
        if file and (file.content_type.rsplit('/', 1)[1] in ALLOWED_EXTENSIONS).__bool__():
            filename = secure_filename(file.filename)
            file.save(app.config['UPLOAD_FOLDER'] + filename)
            return redirect(url_for('uploaded_file', filename=filename, option=choice))
    return render_template('index.html', form=form)


@app.route('/<filename>+<int:option>')
def uploaded_file(filename,option):
    path = './static/images/' + filename
    img = Image.open(path)
    x,y = img.size
    if option == 2:
        img=ImageChops.offset(img, 0, y//2)
    else:
        img = ImageChops.offset(img, x//2, 0)
    new_path = './static/images/new'+ filename
    img.save(new_path)
    img_arr = np.array(img)
    img_arr_graph = np.array([img_arr[:,:,0].flatten(),img_arr[:,:,1].flatten(),img_arr[:,:,2].flatten()]).transpose()
    print(img_arr_graph)
    plt.hist(img_arr_graph)
    graph_path = "./static/plots/"+filename
    plt.savefig(graph_path)
    plt.close()
    return render_template('image.html', img = path, option=option, new_img=new_path, graph = graph_path)

try:
    r = requests.get('http://localhost:5000/')
    print(r.status_code)
    if(r.status_code!=200):
        exit(1)
    print(r.text)
except:
    exit(1)

if __name__ == '__main__':
    app.run(debug=True)
