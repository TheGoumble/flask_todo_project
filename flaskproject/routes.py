import os
import secrets
from PIL import Image
from flask import redirect, flash, url_for, render_template, abort, request
from flaskproject import app, bcrypt
from flaskproject.forms import *
from flaskproject.models import *
from flask_login import login_user, logout_user, current_user, login_required


@app.route("/")
@app.route("/home", methods=["POST", "GET"])
def home():
    page = request.args.get('page', 1, type=int)
    tasks = []
    if current_user.is_authenticated:
        tasks = ToDO.query.filter_by(author=current_user).order_by(ToDO.date_created.desc()).paginate(page=page,per_page=9)
        image_file = url_for(
            'static', filename='profile_pics/' + current_user.image_file)
    else:
        image_file = url_for('static', filename='profile_pics/default.png')
    return render_template("home.html", tasks=tasks, image_file=image_file)


@app.route("/register", methods=['POST', "GET"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user = User(first_name=form.first_name.data, last_name=form.last_name.data,
                    username=form.username.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html', title='Sign Up', form=form)


@app.route("/login", methods=['POST', "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful, Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(
        app.root_path, 'static/profile_pics', picture_fn)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn


@app.route("/account", methods=["POST", "GET"])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.username = form.username.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        image_file = url_for(
            'static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)


@app.route("/task/new", methods=["POST", "GET"])
@login_required
def new_task():
    form = TaskForm()
    if current_user.is_authenticated:
        tasks = ToDO.query.filter_by(author=current_user).all()
        image_file = url_for(
            'static', filename='profile_pics/' + current_user.image_file)
    else:
        image_file = url_for('static', filename='profile_pics/default.png')

    if form.validate_on_submit():
        task = ToDO(title=form.title.data, content=form.content.data,
                    due_date=form.due_date.data, author=current_user)
        db.session.add(task)
        db.session.commit()
        flash('Your post has been created', 'success')
        return redirect(url_for('home'))
    return render_template('task.html', title='Add Task', form=form, legend='Add Task', image_file=image_file)


@app.route("/update/<int:task_id>", methods=["POST", "GET"])
@login_required
def update_task(task_id):
    task = ToDO.query.get_or_404(task_id)
    if task.author != current_user:
        abort(403)
    form = TaskForm()
    if form.validate_on_submit():
        task.title = form.title.data
        task.content = form.content.data
        task.due_date = form.due_date.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('home'))
    elif request.method == 'GET':
        form.title.data = task.title
        form.content.data = task.content
        form.due_date.data = task.due_date
    return render_template('task.html', title='Update Post', form=form, legend='Update Task')


@app.route("/delete/<int:remove_id>", methods=["POST"])
@login_required
def delete_task(remove_id):
    task = ToDO.query.get_or_404(remove_id)
    if task.author != current_user:
        abort(403)
    db.session.delete(task)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))

@app.route("/complete/<int:complete_id>", methods=["POST"])
@login_required
def complete_task(complete_id):
    task = ToDO.query.get_or_404(complete_id)
    if task.author != current_user:
        abort(403)
    task.completed = True
    db.session.commit()
    
    db.session.commit()
    flash('Your post has been marked as compelete!', 'success')
    return redirect(url_for('home'))

@app.route("/home/closedue", methods=["POST", "GET"])
def close_due():
    page = request.args.get('page', 1, type=int)
    tasks = []
    if current_user.is_authenticated:
        tasks = ToDO.query.filter_by(author=current_user).order_by(ToDO.due_date.asc()).paginate(page=page,per_page=9)
        image_file = url_for(
            'static', filename='profile_pics/' + current_user.image_file)
    else:
        image_file = url_for('static', filename='profile_pics/default.png')
    return render_template("home.html", tasks=tasks, image_file=image_file)

@app.route("/home/newest", methods=["POST", "GET"])
def newest():
    page = request.args.get('page', 1, type=int)
    tasks = []
    if current_user.is_authenticated:
        tasks = ToDO.query.filter_by(author=current_user).order_by(ToDO.date_created.desc()).paginate(page=page,per_page=9)
        image_file = url_for(
            'static', filename='profile_pics/' + current_user.image_file)
    else:
        image_file = url_for('static', filename='profile_pics/default.png')
    return render_template("home.html", tasks=tasks, image_file=image_file)

@app.route("/home/oldest", methods=["POST", "GET"])
def oldest():
    page = request.args.get('page', 1, type=int)
    tasks = []
    if current_user.is_authenticated:
        tasks = ToDO.query.filter_by(author=current_user).order_by(ToDO.date_created.asc()).paginate(page=page,per_page=9)
        image_file = url_for(
            'static', filename='profile_pics/' + current_user.image_file)
    else:
        image_file = url_for('static', filename='profile_pics/default.png')
    return render_template("home.html", tasks=tasks, image_file=image_file)

@app.route("/home/completed", methods=["POST", "GET"])
def completed():
    page = request.args.get('page', 1, type=int)
    tasks = []
    if current_user.is_authenticated:
        tasks = ToDO.query.filter_by(author=current_user).order_by(ToDO.completed.desc()).paginate(page=page,per_page=9)
        image_file = url_for(
            'static', filename='profile_pics/' + current_user.image_file)
    else:
        image_file = url_for('static', filename='profile_pics/default.png')
    return render_template("home.html", tasks=tasks, image_file=image_file)

@app.route("/home/uncompleted", methods=["POST", "GET"])
def uncompleted():
    page = request.args.get('page', 1, type=int)
    tasks = []
    if current_user.is_authenticated:
        tasks = ToDO.query.filter_by(author=current_user).order_by(ToDO.completed.asc()).paginate(page=page,per_page=9)
        image_file = url_for(
            'static', filename='profile_pics/' + current_user.image_file)
    else:
        image_file = url_for('static', filename='profile_pics/default.png')
    return render_template("home.html", tasks=tasks, image_file=image_file)
