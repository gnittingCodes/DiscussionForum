'''
    This file will handle our typical Bottle requests and responses 
    You should not have anything beyond basic page loads, handling forms and 
    maybe some simple program logic
'''

from bottle import route,response,static_file, get, post, error, request, static_file, jinja2_template as template , redirect
import model
from time import time
import json

@get('/api/info')
def on_info():
    return {
        'server_name': 'Room Chat',
        'server_time': time(),
        'refresh_interval': 1000
    }

#-----------------------------------------------------------------------------
# Static file paths
#-----------------------------------------------------------------------------

# Allow image loading
@route('/img/<picture:path>')
def serve_pictures(picture):
    '''
        serve_pictures

        Serves images from static/img/

        :: picture :: A path to the requested picture

        Returns a static file object containing the requested picture
    '''
    return static_file(picture, root='static/img/')

#-----------------------------------------------------------------------------

# Allow CSS
@route('/css/<css:path>')
def serve_css(css):
    '''
        serve_css

        Serves css from static/css/

        :: css :: A path to the requested css

        Returns a static file object containing the requested css
    '''
    return static_file(css, root='static/css/')


#-----------------------------------------------------------------------------

# Allow javascript
@route('/js/<js:path>')
def serve_js(js):
    '''
        serve_js

        Serves js from static/js/

        :: js :: A path to the requested javascript

        Returns a static file object containing the requested javascript
    '''
    return static_file(js, root='static/js/')

#-----------------------------------------------------------------------------
# Pages
#-----------------------------------------------------------------------------

# Redirect to login
@get('/')
@get('/home')
def get_index():
    '''
        get_index
        
        Serves the index page
    '''
    return model.index()

#-----------------------------------------------------------------------------

# Display the login page
@get('/login')
def get_login_controller():
    '''
        get_login
        
        Serves the login page
    '''
    return model.login_form()

#-----------------------------------------------------------------------------

# Attempt the login
@post('/login')
def post_login():
    '''
        post_login
        
        Handles login attempts
        Expects a form containing 'username' and 'password' fields
    '''
    # Handle the form processing
    username = request.forms.get('username')
    password = request.forms.get('password')
    # Call the appropriate method
    return model.login_check(username, password)


@get('/friends')
def post_friends():
    return model.show_friends()

@get('/logout')
def get_logout():
    return model.logout()

@get('/admin-users')
def get_admin_users():
    # print("admin users")
    return model.show_admin_users()

@post('/delete-users')
def delete_users_redirect():
    # print("HELLO delete user")
    data = request.json 
    selected_users = data.get('selectedUserIDs')  
    model.delete_users(selected_users)
    return model.show_admin_users()

#-----------------------------------------------------------------------------

@get('/about')
def get_about():
    '''
        get_about
        Serves the about page
    '''
    return model.about()
#-----------------------------------------------------------------------------

# Help with debugging
@post('/debug/<cmd:path>')
def post_debug(cmd):
    return model.debug(cmd)

#-----------------------------------------------------------------------------

# 404 errors, use the same trick for other types of errors
@error(404)
def error(error): 
    return model.handle_errors(error)

#-----------------------------------------------------------------------------


# Display the register page
@get('/register')
def get_register_controller():
    '''
        get_register
        
        Serves the login page
    '''
    return model.register_form()


# Attempt to register 
@post('/register')
def post_register():
    '''
        post_register
        
        Handles register attempts
        Expects a form containing 'username' and 'password' fields
    '''
    # Handle the form processing
    username = request.forms.get('username')
    password = request.forms.get('password')
    password_confirm = request.forms.get('password_confirm')
    # Call the appropriate method
    return model.register(username, password, password_confirm)


@post('/chat')
def chat():
    friend_id = request.forms.get('friend_id')
    user_id = request.forms.get('user_id')
    return model.chat_with_friend(friend_id, user_id)


@post('/api/send_message')
def on_message():
    print(request)

    text = request.forms.get('text', '')
    friend = request.forms.get('friend_name', '')
    nick = request.forms.get('nick', '')

    return model.send_message(nick,friend, text)


def decode_body_form(body_info):
    if body_info == None:
        return None
    split = body_info.split('&')

    my_dict = {}
    for i in split:
        my_key,my_value =  i.split('=')
        my_dict[my_key] = my_value
    return my_dict
    

@get('/api/fetch')
def on_fetch():
    username=request.params.get('username')
    friend = request.params.get('friend')
    since = float(request.params.get('since', 0))
    # Fetch new messages
    return model.fetch_message(since, username,friend)


#-----------------------------------------------------------------------------
# Knowledge Repository
#-----------------------------------------------------------------------------

@get('/knowledge-repository')
def get_knowledge_repository():
    return model.knowledge_repository()

@get('/post')
def get_knowledge_repo_post():
    '''
        get_post
    '''
    return model.create_new_post()

@post('/post')
def post_post():
    '''
        post_post
    '''
    # Handle the form processing
    title = request.forms.get('title')
    message = request.forms.get('message')
    return model.add_new_post(title, message)

# own user can delete 
@post('/delete-post')
def delete_post():
    data = request.json 
    post_id = data.get('postId')  
    return model.delete_post_knowledge_repo(post_id)

@post('/edit-post')
def edit_post():
    data = request.json
    new_title = data.get('title')
    new_content = data.get('content')
    post_id = data.get('postId')
    return model.edit_post_knowledge_repo(new_title, new_content, post_id)
    

#-----------------------------------------------------------------------------
# Help:faq, contact 
#-----------------------------------------------------------------------------

@get('/faq')
def get_faq():
    return model.faq()

@get('/contact')
def get_contact():
    return model.contact()

# end faq

#-----------------------------------------------------------------------------
# Tutorial Notes
#-----------------------------------------------------------------------------

# user 
@get('/tutorial-notes')
def get_faq():
    return model.tutorial_notes()


@post('/save-name')
def save_name_notes():
    # print("HELLLOO save name tutorial notes")
    data = request.json  # Extract the JSON data from the request body
    new_name = data.get('name')  # Retrieve the new name
    note_id = data.get('noteId')  # Retrieve the note ID
    return model.edit_name_tutorial_notes(new_name, note_id)
    
@post('/save-link')
def save_link_notes():
    data = request.json 
    new_link = data.get('link')  # Retrieve the new name
    note_id = data.get('noteId')  # Retrieve the note ID
    return model.edit_link_tutorial_notes(new_link, note_id)

# add new note 
@post('/new-note')
def save_link_notes():
    data = request.json 
    new_section_heading = data.get('sectionHeading')  
    note_name = data.get('newFileName')  
    note_link= data.get('newFileLink')  
    return model.add_new_note(new_section_heading, note_name, note_link)

@post('/delete-note')
def delete_note():
    data = request.json 
    note_id = data.get('noteId') 
    return model.delete_note(note_id)


#-----------------------------------------------------------------------------
# Course guide
#-----------------------------------------------------------------------------

@get('/course-guide')
def course_guide_post():
    return model.course_guide()

@post('/delete-topic')
def delete_topic():
    data = request.json 
    topic = data.get('topicId') 
    return model.delete_topic(topic)

@post('/delete-obj')
def delete_objective():
    data = request.json 
    obj_id = data.get('objId') 
    return model.delete_objective(obj_id)

@post('/edit-topic')
def edit_topic():
    data = request.json 
    topic_id = data.get('topicId') 
    topic = data.get('topic') 
    return model.edit_topic(topic_id, topic)

@post('/edit-obj')
def edit_objective():
    data = request.json 
    obj_id = data.get('objId') 
    objective = data.get('objective') 
    return model.edit_objective(obj_id, objective)

@post('/edit-overview')
def edit_overview():
    data = request.json 
    overview = data.get('overview') 
    return model.edit_overview(overview)
   
   
@post('/add-objective')
def add_objective():
    data = request.json 
    objective = data.get('newObjective') 
    return model.add_new_objective(objective)


@post('/add-topic')
def add_topic():
    data = request.json 
    topic = data.get('newTopic') 
    return model.add_new_topic(topic)

@post('/add-user-admin')
def add_user_admin():
    print('add new user admin')
    data = request.json 
    username = data.get('usernameInput')
    pw = data.get('passwordInput') 
    cfm_pw = data.get('confirmPasswordInput') 
    # print(username)
    return model.add_user_admin(username, pw, cfm_pw)


#-----------------------------------------------------------------------------
# Account settings 
#-----------------------------------------------------------------------------
@get('/account')
def get_account_page():
    return model.account_settings()

@post('/validate-current-password')
def check_current_password():
    data = request.json 
    current_password = data.get('currentPassword')
    username = data.get('username')
    valid = model.validate_current_pw(current_password, username)
    return {'valid': valid}

@post('/update-password')
def update_password():
    data = request.json 
    username = data.get('username')
    new_password = data.get('newPassword')
    return model.change_password(new_password, username)

