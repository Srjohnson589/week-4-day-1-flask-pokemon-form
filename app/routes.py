from flask import request, render_template, redirect, url_for, flash
import requests
from app import app
from .forms import PokemonInput, SignUpInput, LoginInput
from app.models import User
from werkzeug.security import check_password_hash
from flask_login import login_user, logout_user

# Home route, greeting page
@app.route('/')
def home():
    return render_template('home.html')

# Login route
@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginInput()
    if request.method == 'POST' and form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        queried_user = User.query.filter(User.username == username).first()
        if queried_user and check_password_hash(queried_user.password, password):
            flash('Success! You have logged in.', 'success')
            login_user(queried_user)
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'danger')
            return render_template('login.html', form=form)
    else:
        return render_template('login.html', form=form)

# Logout
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

# Signup route
@app.route('/signup', methods=["GET", "POST"])
def signup():
    form = SignUpInput()
    if request.method == 'POST' and form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        
        queried_user = User.query.filter(User.username == username).first()
        if queried_user:
            flash('Username already exists. Please choose another.', 'danger')
            return render_template('signup.html', form=form)
        queried_email = User.query.filter(User.email == email).first()
        if queried_email:
            flash('Email already exists.', 'danger')
            return render_template('signup.html', form=form)
        
        new_user = User(username, email, password)
        new_user.save()
        flash('Success! Thank you for signing up!', 'success')
        return redirect(url_for('login'))
        
    else:
        return render_template('signup.html', form=form)

# Pokemon API function and route to get and return info
def pokemon_info(name_or_id):
    url = f'https://pokeapi.co/api/v2/pokemon/{name_or_id}'
    response = requests.get(url)
    if response.ok:
        data = response.json()
        info_dict = {
            'name' : data['name'].title(),
            'hp': data['stats'][0]['base_stat'],
            'attack': data['stats'][1]['base_stat'],
            'defense': data['stats'][2]['base_stat'],
            'sprite_img': data['sprites']['front_shiny'],
            'abilities' : [data['abilities'][x]['ability']['name'] for x in range(0, len(data['abilities']))]
        }
        return info_dict
    return False

@app.route('/pokemon', methods=['GET','POST'])
def pokemon():
    form = PokemonInput()
    if request.method == 'POST' and form.validate_on_submit():
        pokemon = form.pokemon.data
        pokedata = pokemon_info(pokemon)
        return render_template('pokemon.html', pokedata=pokedata, form=form)
    else:
        return render_template('pokemon.html', form=form)