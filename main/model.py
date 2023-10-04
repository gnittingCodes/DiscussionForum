'''
    Our Model class 
    This should control the actual "logic" of your website
    And nicely abstracts away the program logic from your page loading
    It should exist as a separate layer to any database or data structure that you might be using
    Nothing here should be stateful, if it's stateful let the database handle it
'''
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
import view
import random
import bcrypt
import bottle_session
from bottle import Bottle, request, jinja2_template as template, route, request, redirect, static_file, url, response
from requests.exceptions import SSLError
from backports.ssl_match_hostname import match_hostname, CertificateError
import collections
from base64 import b64encode, b64decode
from time import time
from gevent import sleep
import os
import urllib3
from urllib.parse import urlparse
import requests
import ssl
import certifi
import http.cookies
import os
import uuid
import gevent.monkey
import redis

gevent.monkey.patch_all()


page_view = view.View()
room = {}
keys = {}

MESSAGE_TIMEOUT = 10


sessions = {}

class Session:
   
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.data = {}

    def save(self):
        sessions[self.id] = self.data

    def load(self):
        self.data = sessions.get(self.id, {})

    def clear(self):
        sessions.pop(self.id, None)

    def set_user_data(self, user_id, user_name):
        self.data['user_id'] = user_id
        self.data['user_name'] = user_name

    def get_user_data(self):
        user_id = self.data.get('user_id')
        return user_id

    def get_username(self):
        username = self.data.get('username')
        return username


class Message(object):
    def __init__(self, nick, text):
        self.time = time()
     
        self.decrypted = False
   
        self.nick = nick
        self.text = text
    def set_text(self, text):
        self.text = text

    def json(self):
        return {'text': self.text, 'nick': self.nick, 'time': self.time}

#-----------------------------------------------------------------------------
# set up the database
#-----------------------------------------------------------------------------
db = None

#-----------------------------------------------------------------------------
# Index
#-----------------------------------------------------------------------------

def index():
    '''
        index
        Returns the view for the index
    '''
    # Get the session ID from the browser cookie
    session_id = request.get_cookie('session_id')
    # Initialize username as None
    username = None
    # Check if the session ID exists in global sessions dictionary
    if session_id in sessions:
        # Retrieve the session object from sessions dictionary
        session = sessions[session_id]
        # Get the username from the session data
        username = session.get('user_name')
    return page_view.render_jinja_template("index", username=username)


#-----------------------------------------------------------------------------
# Login
#-----------------------------------------------------------------------------


def login_form():
    '''
        login_form
        Returns the view for the login_form
    '''
    return page_view.render_jinja_template("login")

#-----------------------------------------------------------------------------
# Verificaiton
#-----------------------------------------------------------------------------

def verify_certificate():
    try:
        response = requests.get('https://localhost:8081', verify="./certs/ca.pem")
        if response.status_code == 200:
            return True
    except SSLError:
        return False
    except RequestException:
        return False
    return False
    

# Check the login credentials
def login_check(username, password):
    '''
        login_check
        Checks usernames and passwords

        :: username :: The username
        :: password :: The password

        Returns either a view for valid credentials, or a view for invalid credentials
    '''
    
    # Requests verfying rootCA
    # if verify_certificate() == False:
    #     return page_view("invalid", reason="Certificate is not valid.")
    
    login = False
    user_data = db.get_user(username)
    if user_data:
        # Verify the hashed password
        password_to_check = password.encode("utf-8")
        hashed = user_data["password"] #stored password 
        if bcrypt.checkpw(password_to_check, hashed):
            login = True
        else:
            login = False
            err_msg = "Incorrect Password."
    else:
        login = False
        err_msg = "Invalid User."
    if login:
        # Set session ID in a cookie
        session = Session()
        session.set_user_data(user_data['id'], user_data['username'])
        session.save()
        response.set_cookie('session_id', session.id)
        return redirect('/')
    else:
        # return to login page again 
        return page_view.render_jinja_template('login', error_message=err_msg)
        # return page_view.render_jinja_template("invalid", reason=err_msg)

def show_friends():
    session_id = request.get_cookie('session_id')
    
    username = None
    user_id = None
    if session_id in sessions:
        session = sessions[session_id]
        username = session.get('user_name')
        user_id = session.get('user_id')

    if username == None:
        return redirect('/login')

    users = db.check_is_admin(user_id)
    if users != False:
        return show_admin_users()

    else:
        # retrieve friend list from database
        friends_list = db.get_friend_list(user_id)
        friends_list = [{'friend_id': friend[0], 'friend_name': friend[1]}
                        for friend in friends_list]
        kwargs = {
            'username': username,
            'friend_list': friends_list,
            'user_id': user_id
        }
        return page_view.render_jinja_template("show_friends", **kwargs)


def logout():
    session_id = request.get_cookie('session_id')
    if session_id in sessions:
        sessions.pop(session_id)
    return page_view.render_jinja_template("login")


#-----------------------------------------------------------------------------
# About
#-----------------------------------------------------------------------------

def about():
    '''
        about
        Returns the view for the about page
    '''
    session_id = request.get_cookie('session_id')

    # Initialize username as None
    username = None

    # Check if the session ID exists in global sessions dictionary
    if session_id in sessions:
        # Retrieve the session object from sessions dictionary
        session = sessions[session_id]
        # Get the username from the session data
        username = session.get('user_name')  
    return page_view.render_jinja_template("about", garble=about_garble(), username=username)



# Returns a random string each time
def about_garble():
    '''
        about_garble
        Returns one of several strings for the about page
    '''
    garble = ["leverage agile frameworks to provide a robust synopsis for high level overviews.", 
    "iterate approaches to corporate strategy and foster collaborative thinking to further the overall value proposition.",
    "organically grow the holistic world view of disruptive innovation via workplace change management and empowerment.",
    "bring to the table win-win survival strategies to ensure proactive and progressive competitive domination.",
    "ensure the end of the day advancement, a new normal that has evolved from epistemic management approaches and is on the runway towards a streamlined cloud solution.",
    "provide user generated content in real-time will have multiple touchpoints for offshoring."]
    return garble[random.randint(0, len(garble) - 1)]


#-----------------------------------------------------------------------------
# Debug
#-----------------------------------------------------------------------------

def debug(cmd):
    try:
        return str(eval(cmd))
    except:
        pass


#-----------------------------------------------------------------------------
# 404
# Custom 404 error page
#-----------------------------------------------------------------------------

def handle_errors(error):
    error_type = error.status_line
    error_msg = error.body
    return page_view("error", error_type=error_type, error_msg=error_msg)


#-----------------------------------------------------------------------------
# Register/ Add new users
#-----------------------------------------------------------------------------

def register_form():
    '''
        register_form
        Returns the view for the login_form
    '''
    return page_view.render_jinja_template("register")


def register(username, password, password_confirm):
      # By default assume registration is invalid
    registered = False
    
    if not username: # Empty username
        err_str = "Please enter a username."
    elif not password: # Empty password
        err_str = "Please enter a password."
    elif not password_confirm:
        err_str = "Please re-enter your password."
    else:
        if (password_confirm == password):
            pwd_bytes = password.encode("utf-8")
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(pwd_bytes, salt)
            # use salt to make it difficult for an attacker to use 
            # pre-computed hash tables or rainbow tables to crack the passwords
            db.add_user(username, hashed)
            # If registration is successful, set registered to True
            registered = True
        else:
            err_str = "Passwords didn't match. Please try again."
    if registered: 
        user_data = db.get_user(username)
        session = Session()
        session.set_user_data(user_data['id'], user_data['username'])
        session.save()
        response.set_cookie('session_id', session.id)
        # hard code: add john as friend 
        db.add_friend(2, user_data['id'])
        db.add_friend(user_data['id'], 2)
        return page_view.render_jinja_template("index", username=username)
    else:
        return page_view.render_jinja_template("register", error_message=err_str)


# ADMIN
def add_user_admin(username, pw, cfm_pw):
    # print("add user from admin")
    pwd_bytes = pw.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    db.add_user(username, hashed)
    return show_admin_users()
    
def show_admin_users():
    users = db.get_all_users_admin()
    users_list = [{'user_id': user[0], 'user_name': user[1]} for user in users]
    kwargs = {
        'username': "admin", # should be admin
        'users_list': users_list
    }
    return page_view.render_jinja_template("admin-users", **kwargs)

# ADMIN: delete user
def delete_users(users_list):
    for user_id in users_list:
        db.delete_user(user_id)
    return page_view.render_jinja_template("loading-deleting")


#-----------------------------------------------------------------------------
# Chat
#-----------------------------------------------------------------------------

def get_room(username, friend_name):
    room_id1 = friend_name+"_"+username
    room_id2= username+"_"+friend_name
    
    if room.get(room_id1) is not None:
        return room[room_id1]
    elif room.get(room_id2)is not None:
        return room[room_id2]

  
# encrypt messages
def encrypt(message, public_key):

    ciphertext = public_key.encrypt(
        message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return ciphertext

# decrypt messages
def decrypt(encrypted_msg, private_key):
    original_message = private_key.decrypt(
        encrypted_msg,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return original_message
    
# generate public key and private key
def generate_key():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return public_pem, private_pem



def chat_with_friend(friend_id, user_id):

    user_dict = db.get_username_by_id(user_id)
    friend_dict = db.get_username_by_id(friend_id)

    username = user_dict['username']
    friend_name = friend_dict['username']
    kwargs = {
        'username': username,
        'friend_name':friend_name
    }
        
    # generate user key
    key_not_exist = db.check_key_exist( user_id)
    if key_not_exist:
        upublic_pem , uprivate_pem =  generate_key()
        db.update_key(upublic_pem, uprivate_pem, user_id)
        
    # generate friend keys
    key_not_exist_f = db.check_key_exist(friend_id)
    if key_not_exist_f :
        fpublic_pem , fprivate_pem =  generate_key()
        db.update_key(fpublic_pem, fprivate_pem, friend_id)
 
    return page_view.render_jinja_template("room", **kwargs)



def send_message(nick, friend,text):

    friend_id = db.get_id_by_username(friend)
  
    # encrypt message using friend's public key 
    public_friendpem = db.get_user_key(friend_id)[0]
    friend_public_key = serialization.load_pem_public_key(public_friendpem,backend=default_backend())
   
    # encrypt message
    data = bytes(text,"utf-8")
    encrypted_mesg = encrypt(data, friend_public_key)

    timeout = time()-MESSAGE_TIMEOUT

    db.delete_overflow(nick,friend,timeout)

    db.add_msg(nick, friend, encrypted_mesg, time())
    
    return {'status': 'OK'}


# fetch messages from server
def fetch_message(since, username, friend):
    
    private_key = None
    fd_priv = None 

    if username != None and friend != None :
        
        friend_id = db.get_id_by_username(friend)
        user_id = db.get_id_by_username(username)
        private_pem = db.get_private_key(user_id) # user can only access user private key
        fd_private_pem = db.get_private_key(friend_id) # friend can only access friend private key
        
        if private_pem is not None :
            private_key = serialization.load_pem_private_key(private_pem,password=None,backend=default_backend())
        if fd_private_pem is not None :
            fd_priv = serialization.load_pem_private_key(fd_private_pem,password=None,backend=default_backend())
    
    if private_key is not None or fd_priv is not None:
        updates = []
        msg = db.get_msg(username, friend)
        if msg != None:
        
            for i in msg :
                from_name = i[0]
                my_text = i[2]
                my_time =i[3]
                my_json= {'text': None, 'nick':from_name, 'time': my_time}
                if my_time > since :
                    if from_name == friend: # if message sent by friend open with user private key cant be accessed by anyone
                        decrypt_msg = decrypt(my_text, private_key).decode("utf-8") 
                        my_json['text'] = decrypt_msg
                    elif from_name == username: # if friends opening messages sent by use using its own private key
                        decrypt_msg = decrypt(my_text, fd_priv).decode("utf-8") 
                        my_json['text'] = decrypt_msg
            
            updates.append(my_json)

        return { 'messages': updates[:10] }


#-----------------------------------------------------------------------------
# Knowledge Repository
#-----------------------------------------------------------------------------

def add_new_post(title, message):
    # Check if the user is logged in by retrieving their session data
    session_id = request.get_cookie('session_id')
    username = None
    user_id = None

    if session_id in sessions:
        session = sessions[session_id]
        username = session.get('user_name')
        user_id = session.get('user_id')

    if username == None:
        redirect('/login')

    db.add_post(username, title, message)
    kwargs = {
        'username': username,
    }
    return page_view.render_jinja_template('post-success', **kwargs)

    
def create_new_post():
    # Check if the user is logged in by retrieving their session data
    session_id = request.get_cookie('session_id')
    username = None
    user_id = None
    if session_id in sessions:
        session = sessions[session_id]
        username = session.get('user_name')
        user_id = session.get('user_id')
    if username == None:
        redirect('/login')

    kwargs = {
        'username': username,
    }
    return page_view.render_jinja_template("post", **kwargs)

def edit_post_knowledge_repo(new_title, new_content, post_id):
    db.update_post(post_id, new_title, new_content)


def knowledge_repository():
    # Check if the user is logged in by retrieving their session data
    session_id = request.get_cookie('session_id')

    # Initialize username as None
    username = None
    user_id = None

    # Check if the session ID exists in global sessions dictionary
    if session_id in sessions:
        # Retrieve the session object from sessions dictionary
        session = sessions[session_id]

        # Get the user data from the session data
        username = session.get('user_name')
        user_id = session.get('user_id')

    if username == None:
        redirect('/login')

    # retrieve posts from database
    posts = db.show_posts()
    posts = [{'post_id': post[0], 'username': post[1], 'title': post[2], 'content': post[3]} for post in posts]
    kwargs = {
        'username': username,  # user whos logged in 
        'posts': posts
    }
    return page_view.render_jinja_template("knowledge-repository", **kwargs)


def delete_post_knowledge_repo(post_id):
    db.delete_post(post_id)
    return redirect("/knowledge-repository")



#-----------------------------------------------------------------------------
# HELP: FAQ & CONTACT
#-----------------------------------------------------------------------------
def faq():
    # faq does not require log in
    session_id = request.get_cookie('session_id')
    username = None
    if session_id in sessions:
        session = sessions[session_id]
        username = session.get('user_name')  
    return page_view.render_jinja_template("faq", username=username)

def contact():
    session_id = request.get_cookie('session_id')
    username = None
    if session_id in sessions:
        session = sessions[session_id]
        username = session.get('user_name')  
    return page_view.render_jinja_template("contact", username=username)


#-----------------------------------------------------------------------------
# Tutorial Notes
#-----------------------------------------------------------------------------

def tutorial_notes():
    session_id = request.get_cookie('session_id')
    username = None
    user_id = None
    if session_id in sessions:
        session = sessions[session_id]
        username = session.get('user_name')
        user_id = session.get('user_id')

    if username == None:
        redirect('/login')

    users = db.check_is_admin(user_id)
    if users != False:
        # admin can upload / delete 
        return tutorial_notes_admin()
    else:
        # students
        notes = db.show_notes()
        notes = [{'note_id': note[0], 'section_heading': note[1], 'file_link': note[2], 'file_name': note[3]} for note in notes]
        kwargs = {
            'username': username,
            'notes': notes
        }
        return page_view.render_jinja_template("tutorial-notes", **kwargs)

#admin
def tutorial_notes_admin():
    notes = db.show_notes()
    section_headings = [item[0] for item in db.show_notes_sections()]
    notes = [{'note_id': note[0], 'section_heading': note[1], 'file_link': note[2], 'file_name': note[3]} for note in notes]
    kwargs = {
        'username': "admin",
        'notes': notes, 
        'section_headings': section_headings
    }
    return page_view.render_jinja_template("tutorial-notes-admin", **kwargs)

#admin
def edit_name_tutorial_notes(new_name, note_id):
    db.edit_link_name(new_name, note_id)
    sections = {}
    notes = db.show_notes()
    notes = [{'note_id': note[0], 'section_heading': note[1], 'file_link': note[2], 'file_name': note[3]} for note in notes]
    # print(notes)
    kwargs = {
        'username': "admin",
        'notes': notes, 
        'sections': sections, 
        'section_headings': db.show_notes_sections()
    }
    return page_view.render_jinja_template("tutorial-notes-admin", **kwargs)

#admin
def edit_link_tutorial_notes(new_link, note_id):
    db.edit_link(new_link, note_id)
    sections = {}
    notes = db.show_notes()
    notes = [{'note_id': note[0], 'section_heading': note[1], 'file_link': note[2], 'file_name': note[3]} for note in notes]
    kwargs = {
        'username': "admin",
        'notes': notes, 
        'sections': sections, 
        'section_headings': db.show_notes_sections()
    }
    return page_view.render_jinja_template("tutorial-notes-admin", **kwargs)


def add_new_note(section_heading, file_name, file_link):
    db.add_note(section_heading, file_name, file_link)
    sections = {}
    notes = db.show_notes()
    notes = [{'note_id': note[0], 'section_heading': note[1], 'file_link': note[2], 'file_name': note[3]} for note in notes]
    kwargs = {
        'username': "admin",
        'notes': notes, 
        'sections': sections, 
        'section_headings': db.show_notes_sections()
    }
    return page_view.render_jinja_template("tutorial-notes-admin", **kwargs)


def delete_note(note_id):
    db.delete_note(note_id)
    sections = {}
    notes = db.show_notes()
    notes = [{'note_id': note[0], 'section_heading': note[1], 'file_link': note[2], 'file_name': note[3]} for note in notes]
    kwargs = {
        'username': "admin",
        'notes': notes, 
        'sections': sections, 
        'section_headings': db.show_notes_sections()
    }
    return page_view.render_jinja_template("tutorial-notes-admin", **kwargs)
    

#-----------------------------------------------------------------------------
# Course guide
#-----------------------------------------------------------------------------

def course_guide():
    session_id = request.get_cookie('session_id')
    username = None
    user_id = None

    if session_id in sessions:
        session = sessions[session_id]
        username = session.get('user_name')
        user_id = session.get('user_id')
    if username == None:
        redirect('/login')

    course_guide = db.get_course_guide()
    objectives = db.get_objectives(1)
    topics = db.get_topics(1)

    kwargs = {
        'username': username,
        "course_guide": course_guide, 
        'objectives' : objectives, 
        'topics': topics, 
    }
    return page_view.render_jinja_template("course-guide", **kwargs)

# topic
def delete_topic(topic):
    db.delete_topic(topic)
    return course_guide()

def edit_topic(topic_id, topic):
    db.update_topic(topic_id, 1, topic)
    return course_guide()

# objective
def delete_objective(obj_id):
    db.delete_objective(obj_id)
    return course_guide()

def edit_objective(obj_id, objective):
    db.update_objective(obj_id, 1, objective)
    return course_guide()

# overview
def edit_overview(overview):
    db.update_cg_overview(1, overview)
    return course_guide()

# add objective
def add_new_objective(objective):
    db.add_objective(1, objective)
    return course_guide()

# add topic 
def add_new_topic(topic):
    db.add_topic(1, topic)
    return course_guide()


#-----------------------------------------------------------------------------
# Account settings
#-----------------------------------------------------------------------------

def account_settings():
    user_id = None
    session_id = request.get_cookie('session_id')
    username = None

    if session_id in sessions:
        session = sessions[session_id]
        username = session.get('user_name')  
        user_id = session.get('user_id')
        
    if username == None:
        redirect('/login')
    return page_view.render_jinja_template("account", username=username, user_id=user_id)


def validate_current_pw(current_password, username):
    user_data = db.get_user(username)
    change_pw = False
    if user_data:
        # Verify the hashed password
        password_to_check = current_password.encode("utf-8")
        hashed = user_data["password"] #current stored password 
        if bcrypt.checkpw(password_to_check, hashed):
            change_pw = True
        else:
            change_pw = False
    return change_pw
    
            
def change_password(new_password, username):
    user_data = db.get_user(username)
    user_id = user_data["id"]
    pwd_bytes = new_password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    db.update_pw(user_id, hashed)
    
    