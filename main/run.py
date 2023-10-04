'''
    This is a file that configures how your server runs
    You may eventually wish to have your own explicit config file
    that this reads from.

    For now this should be sufficient.

    Keep it clean and keep it simple, you're going to have
    Up to 5 people running around breaking this constantly
    If it's all in one file, then things are going to be hard to fix

    If in doubt, `import this`
'''
#-----------------------------------------------------------------------------
import os
import sys
from bottle import run
import sql
#-----------------------------------------------------------------------------

import model
import view
import controller
import http.server
import ssl
#-----------------------------------------------------------------------------

# It might be a good idea to move the following settings to a config file and then load them
# Change this to your IP address or 0.0.0.0 when actually hosting
host = 'localhost'

# Test port, change to the appropriate port to host
port = 7777

# Turn this off for production
debug = True

def run_server():    
    '''
        run_server
        Runs a bottle server
    ''' 
    # run(server='gunicorn',keyfile='./newcert/localhost-key.pem',ssl_version='TLS_SERVER', 
    #     certfile='./newcert/localhost.pem', host=host, port=port, debug=debug, workers=4) 
    run(server='wsgiref', ssl_version='TLS_SERVER',host=host, port=port, debug=debug, workers=4)

#-----------------------------------------------------------------------------
# SQL support
def manage_db():
    '''
        manage_db
        Starts up and re-initialises an SQL databse for the server
    '''
    database_args = "data.db" # Currently runs in RAM, might want to change this to a file if you use it
    sql_db = sql.SQLDatabase(database_args)
    sql_db.database_setup()
    return sql_db

#-----------------------------------------------------------------------------

# What commands can be run with this python file
# Add your own here as you see fit

command_list = {
    'manage_db' : manage_db,
    'server'       : run_server
}

# The default command if none other is given
default_command = 'server'

def run_commands(args):
    '''
        run_commands
        Parses arguments as commands and runs them if they match the command list

        :: args :: Command line arguments passed to this function
    '''
    commands = args[1:]
    model.db = manage_db()

    # Default command
    if len(commands) == 0:
        commands = [default_command]

    for command in commands:
        if command in command_list:
            command_list[command]()
        else:
            print("Command '{command}' not found".format(command=command))

   
#-----------------------------------------------------------------------------
run_commands(sys.argv)
# 