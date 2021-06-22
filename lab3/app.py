import os
from flask import Flask, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm, RecaptchaField
from PIL import Image
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


UPLOAD_FOLDER = 'images' #папка для загрузки
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])#возможные форматы

#конфигурация приложения
app = Flask(__name__, template_folder="templates", static_folder="images")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["SECRET_KEY"] = "eifwkuwebfwejubfwj23123857y28wad"
app.config["RECAPTCHA_PUBLIC_KEY"] = "6LdHWLkaAAAAAFJioRgnPe-YNl4xxUhNaLTkCZno"
app.config["RECAPTCHA_PRIVATE_KEY"] = "6LdHWLkaAAAAANYhxdrrw7ujYb-3g4aZGOZcWcN8"
types = ['Horizontal', 'Vertical']

class ReCaptcha(FlaskForm):#форма для капчи
    recaptcha = RecaptchaField()

def make_plot(arr, filename):#функция для создания графика распределения цветов
    arr_r = arr[:, :, 0].flatten()#получаем только красный
    arr_g = arr[:, :, 1].flatten()#-зелееый
    arr_b = arr[:, :, 2].flatten()#синий и преобразуем в строку
    arr = np.array([arr_r, arr_g, arr_b])#собираем все в один массив
    arr = arr.transpose()#транспонируем
    plt.hist(arr)#строим гистограмму
    plt.savefig("./images/plots/" + filename + ".png")#сохраняем
    plt.close()#закрываем
    path = "../images/plots/" + filename + ".png"
    return path#возвращаем путь к изображению

@app.route('/img/<filename>+<types>+<int:r>+<int:g>+<int:b>')
def uploaded_file(filename, types, r, g, b):#получаем название, тип, и цвет ргб
    try:
        original = Image.open("./images/"+filename).convert("RGB")#открываем картинку и конвертируем, для избежания конфликтов
        arr = np.array(original)#преобразуем в массив
        plt_path = make_plot(arr, filename)#строим график
        h,w = original.size#получаем размеры
        colour = (r,g,b)#собираем в кортеж
        if types == 'Vertical':#проверяем выбранный тип
            arr[:, int(h/2)-25:int(h/2)+25] = colour
            arr[int(w / 4) - 25:int(w / 4) + 25,:] = colour
        if types == 'Horizontal':
            arr[:, int(h/4)-25:int(h/4)+25] = colour
            arr[int(w / 2) - 25:int(w / 2) + 25,:] = colour
        img = Image.fromarray(arr, 'RGB')#собираем в картику
        new_img = "./images/new"+filename#путь
        img.save(new_img)#сохраняем картинку
        nplt_path = make_plot(arr, "new"+filename)#строим график новой картинки
    except FileNotFoundError:
        print("Файл не найден")
    return render_template('/image.html', old_image=filename, types = types, old_plot=plt_path, new_plot=nplt_path)


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
            select = request.form['types']
            r = int(request.form["r"])
            g = int(request.form["g"])
            b = int(request.form["b"])
            return redirect(url_for('uploaded_file', filename=filename, types=select, r=r, g=g,b=b))
    return render_template('index.html', types = types, form = form)

import lxml.etree as ET
@app.route("/apixml",methods=['GET', 'POST'])
def apixml():
    dom = ET.parse("./static/xml/file.xml")
    xslt = ET.parse("./static/xml/file.xslt")
    transform = ET.XSLT(xslt)
    newhtml = transform(dom)
    strfile = ET.tostring(newhtml)
    return strfile

if __name__ == '__main__':
    app.run(debug=True)
