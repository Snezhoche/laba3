from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import FileField, FloatField, SubmitField
from wtforms.validators import InputRequired
from PIL import Image
import numpy as np
from matplotlib.pyplot import savefig, subplots
import requests
import json
from flask_wtf.recaptcha import RecaptchaField

app = Flask(__name__)

# секретный ключи
app.config['SECRET_KEY'] = 'Nthjhbcn159753'
app.config['RECAPTCHA_PUBLIC_KEY'] = '6LeqXx0mAAAAAFCegI4khFxIxOzwY1c82Bfjc2Bj'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6LeqXx0mAAAAAGmwN6Rpb0kEkpYrjDwbGFqyqQfl'

# Определение формы с полями(какие объекты будут на сайте)
class ImageBlendForm(FlaskForm):
    file1 = FileField('Image 1', validators=[InputRequired()])#передача картинки
    file2 = FileField('Image 2', validators=[InputRequired()])
    alpha = FloatField('Alpha (0-1)', validators=[InputRequired()])#коэффицент от 0 до 1
    recaptcha = RecaptchaField()#добавляем рекапчу
    submit = SubmitField('Blend')

@app.route('/', methods=['GET', 'POST'])#мтод получени и передачи чегото на сайт
def index():
    form = ImageBlendForm()
    if form.validate_on_submit():
        # Получение загруженных пользователем файлов
        file1 = request.files['file1']
        file2 = request.files['file2']
        alpha = float(request.form['alpha'])

        # Открытие и обработка изображений
        img1 = Image.open(file1)
        img2 = Image.open(file2)

        # Проверка размеров изображений
        if img1.size != img2.size:
            return render_template('index.html', form=form, error_message='Images must have the same size.')

        # Проверка количества каналов
        if img1.mode != img2.mode:
            return render_template('index.html', form=form, error_message='Images must have the same number of channels.')

        blended_img = Image.blend(img1, img2, alpha)

        # Создание графиков интенсивность распределения цветов
        fig, axes = subplots(nrows=2, ncols=2, figsize=(10, 10))
        axes[0, 0].imshow(img1)
        axes[0, 0].set_title('Image 1')
        axes[0, 1].hist(np.array(img1).flatten(), bins=256, color='red')
        axes[0, 1].set_title('Color Distribution - Image 1')
        axes[1, 0].imshow(img2)
        axes[1, 0].set_title('Image 2')
        axes[1, 1].hist(np.array(img2).flatten(), bins=256, color='blue')
        axes[1, 1].set_title('Color Distribution - Image 2')

        # Сохранение полученного изображения и графиков во временные файлы
        blended_img_path = 'static/blended_img.png'
        savefig('static/color_distributions.png')
        blended_img.save(blended_img_path)

        return render_template('result.html', blended_img_path=blended_img_path)

    return render_template('index.html', form=form)
#запуск приложения
if __name__ == '__main__':
    app.run(debug=True)
