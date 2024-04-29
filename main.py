from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileRequired
from werkzeug.utils import secure_filename
import os
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'


# Banco de dados
def load_data():
  try:
    with open('series.json', 'r') as f:
      data = json.load(f)
      series_data = data.get('series', [])
  except (FileNotFoundError, json.JSONDecodeError):
    series_data = []
  return series_data


# Salvar dados no arquivo JSON
def save_data(data):
  with open('series.json', 'w') as f:
    json.dump({'series': data}, f, indent=4)


series = load_data()


# Formulário para adicionar/editar um item
class ItemForm(FlaskForm):
  name = StringField('Name', validators=[DataRequired()])
  description = StringField('Description', validators=[DataRequired()])
  notaImdb = StringField('Nota Imdb', validators=[DataRequired()])
  dataLancamento = StringField('Data de Lançamento',
                               validators=[DataRequired()])
  imagem = FileField('Imagem', validators=[FileRequired()])
  submit = SubmitField('Submit')


# Rota para a página principal (lista de itens)
@app.route('/')
def index():
  return render_template('index.html', items=series)


@app.route('/add', methods=['GET', 'POST'])
def add_item():
  form = ItemForm()
  if form.validate_on_submit():
    print("\nENTROU NO IF\n")
    imagem_filename = secure_filename(form.imagem.data.filename)
    imagem_path = os.path.join(app.root_path, 'static', imagem_filename)
    form.imagem.data.save(imagem_path)
    item = {
        "id": len(series) + 1,
        "name": form.name.data,
        "description": form.description.data,
        "notaImdb": form.notaImdb.data,
        "dataLancamento": form.dataLancamento.data,
        "imagem": imagem_filename
    }
    series.append(item)
    save_data(series)  # Salvar os dados no arquivo JSON
    flash('Serie adicionado com sucesso!', 'success')
    return redirect(url_for('index'))
  else:
    print('Erros de validação:', form.errors)
  return render_template('add_item.html', form=form)


@app.route('/item/<int:item_id>')
def item_detail(item_id):
  item = next((item for item in series if item['id'] == item_id), None)
  if item:
    return render_template('item_detail.html', item=item)
  else:
    return 'Item not found', 404


@app.route('/delete/<int:item_id>', methods=['GET', 'POST'])
def delete_item(item_id):
  item = next((item for item in series if item['id'] == item_id), None)
  if item:
    if request.method == 'POST':
      series.remove(item)
      save_data(series)  # Salvar os dados no arquivo JSON
      flash('Item deleted successfully!', 'success')
      return redirect(url_for('index'))
    return render_template('delete_item.html', item=item)
  else:
    return 'Item nao encontrado', 404


@app.route('/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_item(item_id):
  item = next((item for item in series if item['id'] == item_id), None)
  if not item:
    return 'Item not found', 404

  form = ItemForm(obj=item)  # Preenche o formulário com os dados do item

  if form.validate_on_submit():
    item['name'] = form.name.data
    item['description'] = form.description.data
    item['notaImdb'] = form.notaImdb.data
    item['dataLancamento'] = form.dataLancamento.data

    # Verifica se um novo arquivo de imagem foi enviado
    if form.imagem.data:
      imagem_filename = secure_filename(form.imagem.data.filename)
      imagem_path = os.path.join(app.root_path, 'static', imagem_filename)
      form.imagem.data.save(imagem_path)
      item['imagem'] = imagem_filename

    # Atualiza os dados no arquivo JSON
    save_data(series)
    print("AASDASDASDASDASD")
    flash('Série editada com sucesso!', 'success')
    return redirect(url_for('index'))
  else:
    # Preenche o formulário com os dados do item
    form.name.data = item['name']
    form.description.data = item['description']
    form.notaImdb.data = item['notaImdb']
    form.dataLancamento.data = item['dataLancamento']
    
  return render_template('edit_item.html', form=form, item=item)
