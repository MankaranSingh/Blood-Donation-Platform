from flask import render_template, session, redirect, url_for, flash, redirect, current_app, abort, request, jsonify
from . import main
from .forms import Login, SignUp, Admin_editor, Profile_Edit, PostForm,SearchForm
from .. import db, login_manager, moment
from ..models.users import User, Role, Permission, Post
from werkzeug import check_password_hash, generate_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug import generate_password_hash
from flask_mail import Message
from ..decorators import permission_required, admin_required
from datetime import datetime
import smtplib


try:
    s = smtplib.SMTP('smtp.gmail.com', 587) 
    s.starttls() 
    s.login("techmitechmi@gmail.com", "do not hack")
except:
    pass


@main.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()

@main.route('/request/<blood_group>', methods=['GET', 'POST'])
def request_blood(blood_group):
    form = SearchForm()

    if blood_group in ['A+','A-','B+','B-','O+','O-','AB-', 'AB+']:
        donors =  User.query.filter_by(blood_group = blood_group, donate = 1)
    else:
        donors = User.query.filter_by(donate = 1)
    if form.validate_on_submit():
        group = form.blood_group.data
        return redirect(url_for('main.request_blood', blood_group = group))


    return render_template('Donors.html',donors = donors[::-1], form=form)

@main.route('/send/<name>/<group>', methods=['GET', 'POST'])
@login_required
def send_mail(name,group):
    user = User.query.filter_by(username = name).first()
    if not user:
        abort(404)
    message = f'Greetings {name}! \n\n \
                \
                {current_user.username} has requested blood from you. \n \
                It would be great if you donate and save someone\'s life ! \n \
                Here are the details of Person requesting blood: \n\n \
                \
                Name: {current_user.username} \n\
                Age: {current_user.age} \n\
                Address : {current_user.location} \n\
                Blood Group: {current_user.blood_group} \n\
                Email: {current_user.email} \n\
                Phone Number: {current_user.phone_number} \n\n\
                \
                Have a nice day !'
    try:
        s.sendmail("techmitechmi@gmail.com", f"{user.email}", message)
        flash('E-mail sent successfully with your details.')
    except:
        flash('Failed to send E-mail,Please try again later.')
    return redirect(f'request/{group}')

@main.route('/start', methods=['GET', 'POST'])
@login_required
def start():
    user = current_user._get_current_object()
    if not user:
        abort(404)
    user.donate = 1
    db.session.commit()
    return redirect(url_for('main.donor_dashboard'))

@main.route('/donors', methods=['GET', 'POST'])
def donors():
    donors_list = User.query.filter_by(donate = 1)
    return render_template('Donors.html', donors = donors_list)
                                       

@main.route('/stop', methods=['GET', 'POST'])
@login_required
def stop():
    user = current_user._get_current_object()
    if not user:
        abort(404)
    user.donate = 0
    db.session.commit()
    return redirect(url_for('main.donor_dashboard'))
    

@main.route('/Login', methods=['GET', 'POST'])
def login():
    form = Login()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user,form.remember.data)
            flash('Logged In')
            return redirect(url_for('main.home' , page = 1))
        else:
            flash('Login Failed, Incorrect Username or Password Entered')
    return render_template('Login.html', form = form)

@main.route('/SignUp', methods=['GET', 'POST'])
def sign_up():
    form = SignUp()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(username = form.username.data, email = form.email.data, password= hashed_password,location = 'Patiala, ' + str(form.Area.data), blood_group = form.blood_group.data, phone_number = form.phone_number.data, age = form.age.data)
        Role.insert_roles()
        if form.email.data == 'techmitechmi@gmail.com':
            user.role = Role.query.filter_by(role_name = 'Administrator').first()
        else:
            user.role = Role.query.filter_by(role_name = 'User').first()
        user.avtar_hash = user.generate_avtar_hash()
        db.session.add(user)
        db.session.commit()
        flash('Your Acount has been successfuly registered, A confirmation E-mail been sent to your emai address. ')
        #token = user.generate_confirmation_token()
        #User.send_mail(user.email, 'Confirm Account' , 'confirmation_email'
        #            , user = user, token = token)
        return redirect(url_for('main.login'))
    return render_template('Register.html', form = form)

@main.route('/super/<name>', methods=['GET', 'POST'])
@admin_required
@login_required
def Admin_edit(name):
    user = User.query.filter_by(username = name).first()
    if not user:
        abort(404)
    form = Admin_editor()
    if form.validate_on_submit():
        if user.username!=form.username.data and User.query.filter_by(username = form.username.data).first():
            flash('Username already in use.')
            return redirect(url_for('main.Admin_edit', name = name))
        if user.email!=form.email.data and User.query.filter_by(email = form.email.data).first():
            flash('Email already in use.')
            return redirect(url_for('main.Admin_edit', name = name))
        new_role = Role.query.filter_by(role_name = form.role.data).first()
        if not new_role:
            flash('Invaid role entered.Only Administrator, User and Moderator roles available.')
            return redirect(url_for('main.Admin_edit', name = name))
        user.username = form.username.data
        user.email = form.email.data
        user.role = new_role
        db.session.commit()
        flash('Account details updated successfully.')
    form.username.data = user.username
    form.email.data = user.email
    form.role.data = user.role.role_name
    return render_template('Admin.html', form = form)

@main.route('/profile/<name>', methods=['GET', 'POST'])
def Profile(name):
    user = User.query.filter_by(username = name).first()
    if not user:
        abort(404)
    return render_template('Profile.html', current_time = datetime.utcnow(), user = user)

@main.route('/Edit_Profile',methods=['GET', 'POST'])
@login_required
def edit_profile():
    user = current_user._get_current_object()
    if not user:
        abort(404)
    form = Profile_Edit()
    if form.validate_on_submit():
        if user.username!=form.username.data and User.query.filter_by(username = form.username.data).first():
            flash('Username already in use.')
            return redirect(url_for('main.edit_profile'))
        if user.email!=form.email.data and User.query.filter_by(email = form.email.data).first():
            flash('Email already in use.')
            return redirect(url_for('main.edit_profile'))

        user.username = form.username.data
        user.email = form.email.data
        user.location = form.location.data
        user.about_me = form.about_me.data

        db.session.commit()
        flash('Account details updated successfully.')
    form.username.data = user.username
    form.email.data = user.email
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('Profile_Edit.html', form = form)





@main.route('/confirm/<token>')
@login_required
def confirm_id(token):
    if current_user.confirmed:
        return redirect(url_for('main.home', page = 1))
    if current_user.confirm(token):
        flash('You have confirmed your account.')
    else:
        flash('The confirmation link is invalid or has expired.')
        return redirect(url_for('main.home', page = 1))

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged Out')
    return redirect(url_for('main.home', page = 1))

@main.route('/admin')
@login_required
@admin_required
def for_admins_only():
    User.generate_fake()
    Post.generate_fake()
    return "DB modifications made"


@main.route('/moderator')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def for_moderators_only():
    return "For comment moderators!"

@main.route('/Home/Dashboard', methods=['GET', 'POST'])
@login_required
def donor_dashboard():
    return render_template('Donor_Dashboard.html')

@main.route('/Home/', methods=['GET', 'POST'])
def home():
    return render_template('HomePage.html')

@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post_viewer(id):

    post = Post.query.get_or_404(id)
    return render_template('Post.html', posts = [post])

@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def post_editor(id):

    post = post = Post.query.get_or_404(id)
    if not (post.author == current_user._get_current_object() or current_user.can(Permission.MODERATE_COMMENTS)):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.commit()
        flash('Post edited successfully.')
        return redirect(url_for('main.post_viewer', id = post.id))
    form.body.data = post.body
    return render_template('Post_Edit.html' ,form = form)










