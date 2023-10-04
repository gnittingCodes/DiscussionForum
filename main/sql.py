import sqlite3

# This class is a simple handler for all of our SQL database actions
# Practicing a good separation of concerns, we should only ever call 
# These functions from our models

import bcrypt

class SQLDatabase():
    '''
        Our SQL Database

    '''

    # Get the database running
    def __init__(self, database_arg):
        self.conn = sqlite3.connect(database_arg)
        self.cur = self.conn.cursor()

    # SQLite 3 does not natively support multiple commands in a single statement
    # Using this handler restores this functionality
    # This only returns the output of the last command
    def execute(self, sql_string):
        out = None
        for string in sql_string.split(";"):
            try:
                out = self.cur.execute(string)
            except:
                pass
        return out

    # Commit changes to the database
    def commit(self):
        self.conn.commit()

    #-----------------------------------------------------------------------------
    
    # Sets up the database
    # Default admin password
    def database_setup(self, admin_password='admin'):

        # Clear the database if needed
        self.execute("DROP TABLE IF EXISTS Users")
        self.execute("DROP TABLE IF EXISTS Friends")
        self.execute("DROP TABLE IF EXISTS Room")
        self.execute("DROP TABLE IF EXISTS PostsKR")
        self.execute("DROP TABLE IF EXISTS tutorialFiles")
        self.execute("DROP TABLE IF EXISTS course_guide")
        self.execute("DROP TABLE IF EXISTS objectives")
        self.execute("DROP TABLE IF EXISTS topics")
        self.execute("DROP TABLE IF EXISTS assessments")
        self.commit()

       # Create the users table
        self.execute("""CREATE TABLE Users(
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            public_key VARCHAR(2048) NULL,
            private_key VARCHAR(2048) NULL,
            admin INTEGER DEFAULT 0
        )""")
        self.commit()
        
        # Create the tutorial files  table
        self.execute(""" CREATE TABLE IF NOT EXISTS tutorialFiles (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            section_heading TEXT,
            file_link TEXT,
            file_name TEXT
        )""")
        self.commit()

        # create posts table for knowledge repo. 
        # post id, username, title of post, and content 
        self.execute("""CREATE TABLE PostsKR(
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            title TEXT,
            content TEXT,
            FOREIGN KEY (username) REFERENCES Users(Id)
        )""")
        self.commit()
        
        # create for course guide content 
        self.execute("""CREATE TABLE course_guide (
            id INTEGER PRIMARY KEY,
            title TEXT,
            overview TEXT
        );""")
        self.commit()
        self.execute("""CREATE TABLE objectives (
            id INTEGER PRIMARY KEY,
            course_guide_id INTEGER,
            objective TEXT,
            FOREIGN KEY (course_guide_id) REFERENCES course_guide(id)
        );""")
        self.commit()
        self.execute("""CREATE TABLE topics (
            id INTEGER PRIMARY KEY,
            course_guide_id INTEGER,
            topic TEXT,
            FOREIGN KEY (course_guide_id) REFERENCES course_guide(id)
        );""")
        self.commit()
        # self.execute("""CREATE TABLE assessments (
        #     id INTEGER PRIMARY KEY,
        #     course_guide_id INTEGER,
        #     name TEXT,
        #     percentage INTEGER,
        #     FOREIGN KEY (course_guide_id) REFERENCES course_guide(id)
        # );""")
        # self.commit()
        
        # hard code for course guide
        self.execute("""INSERT INTO course_guide (title, overview)
                     VALUES ('INFO2222: Computing 2 Usability and Security', 
                     'This unit provides an integrated treatment of two critical topics for a computing professional: 
                     human computer interaction (HCI) and security.');""")
        self.commit()
        self.add_topic(1, "Cryptography basics I")
        self.add_topic(1, "Cryptography basics II")
        # self.add_assessment(1, "Monitored exam ", 50)
        # self.add_assessment(1, "Online Task", 20)
        # self.add_assessment(1, "Assignment 1", 15)
        # self.add_assessment(1, "Assignment 2", 15)
        self.add_objective(1, "produce written reports that evaluate a web site for usability and security")
        self.add_objective(1, "use iterative prototyping, with design and evaluation cycles, to explore a design space")
        self.add_objective(1, "evaluate interfaces, following a user-based technique")
        #
        
        # Create the room chat table
        self.execute("""CREATE TABLE Room(
            from_name TEXT,
            to_name TEXT,
            text TEXT,
            time DOUBLE PRECISION,
            FOREIGN KEY (from_name) REFERENCES Users(username),
            FOREIGN KEY (to_name) REFERENCES Users(username)
        )""")
        self.commit()
        
        # create friends
        # public_key  = user_id public key
        # private_key = user_id private key can only be accessed by user_id
        self.execute("""CREATE TABLE Friends(
                user_id INTEGER ,
                friend_id INTEGER,
                public_key VARCHAR(2048) DEFAULT NULL, 
                private_key VARCHAR(2048) DEFAULT NULL,
                FOREIGN KEY(user_id) REFERENCES Users(Id),
                FOREIGN KEY(friend_id) REFERENCES Users(Id))""")
        self.commit()
        
        # hard code for KR
        self.add_post("admin", "Deadline for Assignment 2", "Please note that this assignment is due THIS SUNDAY.")
        self.add_post("john", "LeetCode: two sums problem", "https://leetcode.com/problems/two-sum/")
        self.add_post("mary", "Top 10 Free Coding Resources for Students that will Change Your Classroom", "https://gocoderz.com/blog/10-free-coding-resources-for-students/")
        self.add_post("bob", "W3Schools recommended", "Hi I am bob. I suggest beginners who are just getting started into front-end development to check out this resource and follow its tutorials. Here is the link: https://www.w3schools.com/")
        self.add_post("mary", "New Computer Science & IT courses", "Hi I am Mary. I would like to recommend this site: https://www.coursera.org/collections/popular-new-computer-science-courses")
        

        # hard code for tutorial notes
        self.add_note("Admins", "https://www.sydney.edu.au/content/dam/students/documents/student-wall-calendar.pdf", "USYD calendar 2023")
        self.add_note("Lab 1", "https://jeffe.cs.illinois.edu/teaching/algorithms/book/Algorithms-JeffE.pdf", "Data Structures and Algorithm Textbook")
        self.add_note("Lab 1", "https://www.africau.edu/images/default/sample.pdf", "Sample PDF")
        
        # hard code: add users: "admin", "john", "mary" 
        pwd_bytes = admin_password.encode("utf-8")
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(pwd_bytes, salt)
        self.add_user("admin", hashed, 1)
        
        # user id 2
        pwd_bytes = "1234".encode("utf-8")
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(pwd_bytes, salt)
        self.add_user("john", hashed)
        
        # user id 3
        pwd_bytes = "1111".encode("utf-8")
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(pwd_bytes, salt)
        self.add_user("mary", hashed)
        
        # user id 4
        pwd_bytes = "iloveunicorn".encode("utf-8")
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(pwd_bytes, salt)
        self.add_user("bob", hashed)
        
        self.add_friend(2, 3)
        self.add_friend(2, 4)
        self.add_friend(4, 2)
        self.add_friend(3, 2)
        
    #-----------------------------------------------------------------------------
    # keys
    #-----------------------------------------------------------------------------
    def update_private_key(self,pbkey,privkey, username_id):
        sql_query = """UPDATE Friends SET  public_key= ? ,private_key = ?  WHERE user_id = ?"""
        self.cur.execute(sql_query, (pbkey, privkey, username_id))
        self.conn.commit()
        return True


    def check_key_exist(self, username_id):
        sql_query = """SELECT *
            FROM Users
            WHERE Id = ? AND public_key IS NULL AND private_key IS NULL"""
        self.cur.execute(sql_query, (username_id,))
        records = self.cur.fetchone()
        if records:
            return True
        else:
            return False
        
    def get_user_key(self,user_id):
        sql_query = """SELECT * 
                    FROM Users
                    WHERE Id=?"""
        self.cur.execute(sql_query, (user_id,))
        records = self.cur.fetchone()
        if records:
            return records[3], records[4]
        else:
            return None
    

    #-----------------------------------------------------------------------------
    # User handling
    #-----------------------------------------------------------------------------

    # Add a user to the database
    def add_user(self, username, password, admin=0):
        sql_query = """INSERT INTO Users (username, password, admin)
                    VALUES (?, ?, ?)"""
        self.cur.execute(sql_query, (username, password, admin))
        self.conn.commit()
        return True
    
    
    def delete_user(self, user_id):
        sql_query = """DELETE FROM Users WHERE Id=?"""
        self.cur.execute(sql_query, (user_id,))
        self.conn.commit()
        return True

    
    def add_friend(self, username_id, friend_id):
        sql_query = """INSERT INTO Friends (user_id, friend_id) VALUES (?, ?)"""
        self.cur.execute(sql_query, (username_id, friend_id))
        self.conn.commit()
        return True
    
    def update_pw(self, user_id, new_password):
        sql_query = """UPDATE Users SET password = ? WHERE Id = ?"""
        self.cur.execute(sql_query, (new_password, user_id))
        self.conn.commit()
        return True
    

    def update_key(self,pubkey,privkey,user_id):
        sql_query = """UPDATE Users SET public_key=?, private_key = ?  WHERE Id = ? """
        self.cur.execute(sql_query, (pubkey,privkey,user_id))
        self.conn.commit()
        return True
 
    def update_private_key(self,privkey, username_id, friends_id):
        sql_query = """UPDATE Friends SET  private_key = ?  WHERE user_id = ? AND friend_id = ?"""
        self.cur.execute(sql_query, (privkey,username_id, friends_id))
        self.conn.commit()
        return True
    
    def update_public_key(self,pbkey, username_id, friends_id):
        sql_query = """UPDATE Friends SET  public_key = ?  WHERE user_id = ? AND friend_id = ?"""
        self.cur.execute(sql_query, (pbkey,username_id, friends_id))
        self.conn.commit()
        return True
    
    #-----------------------------------------------------------------------------

    # get user information from username
    def get_user(self, check_username):

        sql_query = """SELECT * 
                    FROM Users
                    WHERE username=?"""
        self.cur.execute(sql_query, (check_username,))
        records = self.cur.fetchone()

        if records:
            user = {"id": records[0], "username": records[1], "password": records[2]}
            return user
        else:
            return None
        

    def check_is_admin(self, user_id):
        sql_query = """SELECT * 
                    FROM Users
                    WHERE admin=1 and Id=?"""
        self.cur.execute(sql_query, (user_id,))
        records = self.cur.fetchone()
        if records:
            user = {"id": records[0], "username": records[1], "users": self.get_all_users_admin}
            return user
        else:
            return False
        
        
    def get_username_by_id(self, user_id):

        sql_query = """SELECT * 
                    FROM Users
                    WHERE Id=?"""
        self.cur.execute(sql_query, (user_id,))
        records = self.cur.fetchone()
        if records:
            user = {"id": records[0], "username": records[1], "password": records[2]}
            return user
        else:
            return None
        
    def get_id_by_username(self, username):
        sql_query = """SELECT * 
                    FROM Users
                    WHERE username=?"""
        self.cur.execute(sql_query, (username,))
        records = self.cur.fetchone()
        if records:
            return records[0]
        else:
            return None


    def get_friend_list(self, user_id):
        self.cur.execute("""SELECT friend_id FROM Friends WHERE user_id=?""", (user_id,))
        friend_ids = [row[0] for row in self.cur.fetchall()]

        friend_list = []
        for friend_id in friend_ids:
            self.cur.execute("""SELECT username FROM Users WHERE id=?""", (friend_id,))
            friend_name = self.cur.fetchone()[0]
            friend_list.append((friend_id, friend_name))

        return friend_list
    

    def get_all_users_admin(self):
        self.cur.execute("""SELECT Id, username FROM Users""")
        user_ids = [row[0] for row in self.cur.fetchall()]
        
        users = []
        for user_id in user_ids:
            self.cur.execute("""SELECT username FROM Users WHERE id=?""", (user_id,))
            user_name = self.cur.fetchone()[0]
            users.append((user_id, user_name))
        return users
    
    #------------------------ message--------------------

    def add_msg(self,user, friend,  msg, time):
        sql_query = """INSERT INTO Room (from_name,to_name,text, time) VALUES (?, ?, ?,?)"""
        self.cur.execute(sql_query, (user, friend, msg, time))
        self.conn.commit()
        return True
    
    def get_msg(self,user, friend):
        sql_query = """SELECT * 
            FROM Room
            WHERE (from_name=? AND to_name=?) OR (from_name=? AND to_name=?) ORDER BY time"""
        self.cur.execute(sql_query, (user,friend,friend, user,))
        records = self.cur.fetchall()
        if records:
            return records
        else:
            return None
        
    def get_room(self):
        sql_query = """SELECT * 
            FROM Room ORDER BY time"""
        self.cur.execute(sql_query)
        records = self.cur.fetchall()
        if records:
        
            return records
        else:
            return None
        
    def get_private_key(self , owner): # only let owner access private keys
        sql_query = """SELECT private_key 
                    FROM Users
                    WHERE Id=?"""
        self.cur.execute(sql_query, (owner,))
        records = self.cur.fetchone()

        if records:
            return records[0]
        else:
            return None


    def delete_overflow(self,user, friend, timeout):
        sql_query = """DELETE FROM Room
        where (from_name=? and to_name=? and time <?) OR (from_name =? and to_name =? and time < ?)"""
        self.cur.execute(sql_query, (user,friend,timeout ,friend, user,timeout,))
        return True


  
    #-----------------------------------------------------------------------------
    # Posts 

    def show_posts(self):
        self.cur.execute("""SELECT * FROM PostsKR""")
        post_ids = [row[0] for row in self.cur.fetchall()]
        posts = []
        for post_id in post_ids:
            self.cur.execute("""SELECT id, username, title, content FROM PostsKR WHERE id=?""", (post_id,))
            post_info = self.cur.fetchone()
            posts.append((post_info))
        return posts


    def add_post(self, username, title, content):
        sql_query = """INSERT INTO PostsKR (username, title, content) VALUES (?, ?, ?)"""
        self.cur.execute(sql_query, (username, title, content))
        self.conn.commit()
        return True
    
    # user can edit own post (error correction)
    def update_post(self, post_id, new_title, new_content):
        if not new_title and new_content:
            self.cur.execute("""UPDATE PostsKR SET content = ? WHERE Id = ?""", (new_content, post_id))
        elif not new_content and new_title:
            self.cur.execute("""UPDATE PostsKR SET title = ? WHERE Id = ?""", (new_title, post_id))
        else:
            sql_query = """UPDATE PostsKR SET title = ?, content = ? WHERE Id = ?"""
            self.cur.execute(sql_query, (new_title, new_content, post_id))
        self.conn.commit()
        return True

    # only user who posted this, and admin can delete posts
    def delete_post(self, post_id):
        # id of the post 
        sql_query = """DELETE FROM PostsKR WHERE Id = ?"""
        self.cur.execute(sql_query, (post_id,))
        self.conn.commit()
        return True


    #===============================
    # tutorial notes: tutorialFiles
    def show_notes(self):
        self.cur.execute("""SELECT id, section_heading, file_link, file_name FROM tutorialFiles""")
        notes = []
        for row in self.cur.fetchall():
            notes.append((row))
        return notes
    
    def show_notes_sections(self):
        self.cur.execute("""SELECT DISTINCT section_heading FROM tutorialFiles""")
        sections = []
        for row in self.cur.fetchall():
            sections.append((row))
        return sections

    def add_note(self, section_heading, file_link, file_name):
        sql_query = """INSERT INTO tutorialFiles (section_heading, file_link, file_name) VALUES (?, ?, ?)"""
        self.cur.execute(sql_query, (section_heading, file_link, file_name))
        self.conn.commit()
        return True
    
    def delete_note(self, note_id):
        sql_query = """DELETE FROM tutorialFiles WHERE Id = ?"""
        self.cur.execute(sql_query, (note_id, ))
        self.conn.commit()
        return True
    
    # user can edit own post (error correction)
    def edit_link_name(self, new_name, note_id):
        sql_query = """UPDATE tutorialFiles SET file_name = ? WHERE Id = ?"""
        self.cur.execute(sql_query, (new_name, note_id))
        self.conn.commit()
        return True

    def edit_link(self, new_link, note_id):
        sql_query = """UPDATE tutorialFiles SET file_link =? WHERE Id = ?"""
        self.cur.execute(sql_query, (new_link, note_id))
        self.conn.commit()
        return True


    # course guide for admin to edit 
    # course guide is already created -- only one course guide 
    
    def update_cg_title(self, course_guide_id, title):
        query = """UPDATE course_guide SET title=? WHERE id=?"""
        values = (title, course_guide_id)
        self.cur.execute(query, values)
        self.conn.commit()
        return True
    
    def update_cg_overview(self, course_guide_id, overview):
        query = """UPDATE course_guide SET overview=? WHERE id=?"""
        values = (overview, course_guide_id)
        self.cur.execute(query, values)
        self.conn.commit()
        return True
        
    def delete_course_guide(self, course_guide_id):
        query = "DELETE FROM course_guide WHERE id=?"
        values = (course_guide_id,)
        self.cur.execute(query, values)
        self.conn.commit()
        return True


    def get_course_guide(self):
        self.cur.execute("""SELECT * FROM course_guide""")
        course_guide_data = self.cur.fetchone()
        if course_guide_data:
            course_guide = {
                'id': course_guide_data[0],
                'title': course_guide_data[1],
                'overview': course_guide_data[2]
            }
            return course_guide
        return None
    
    
    def get_objectives(self, course_guide_id):
        self.cur.execute("""SELECT * FROM objectives WHERE course_guide_id = ?""", (course_guide_id,))
        objectives_data = self.cur.fetchall()
        objectives = []
        for objective_data in objectives_data:
            objective = {
                'id': objective_data[0],
                'course_guide_id': objective_data[1],
                'objective': objective_data[2]
            }
            objectives.append(objective)

        return objectives
    
    def update_objective(self, objective_id, course_guide_id, objective):
        query = """UPDATE objectives SET course_guide_id=?, objective=? WHERE id=?"""
        values = (course_guide_id, objective, objective_id)
        self.cur.execute(query, values)
        self.conn.commit()
        return True
    
    def add_objective(self, course_guide_id, objective):
        self.cur.execute("""INSERT INTO objectives (course_guide_id, objective) VALUES (?, ?)""", (course_guide_id, objective))
        self.conn.commit()
        return True
    
    def delete_objective(self, objective_id):
        query = """DELETE FROM objectives WHERE id=?"""
        values = (objective_id,)
        self.cur.execute(query, values)
        self.conn.commit()
        return True
    
    
    def get_topics(self, course_guide_id):
        self.cur.execute("""SELECT * FROM topics WHERE course_guide_id = ?""", (course_guide_id,))
        topics_data = self.cur.fetchall()
        topics = []
        for topic_data in topics_data:
            topic = {
                'id': topic_data[0],
                'course_guide_id': topic_data[1],
                'topic': topic_data[2]
            }
            topics.append(topic)

        return topics
    
    def add_topic(self, course_guide_id, topic):
        self.cur.execute("""INSERT INTO topics (course_guide_id, topic) VALUES (?, ?)""", (course_guide_id, topic))
        self.conn.commit()
        return True
    
    def update_topic(self, topic_id, course_guide_id, topic):
        query = """UPDATE topics SET course_guide_id=?, topic=? WHERE id=?"""
        values = (course_guide_id, topic, topic_id)
        self.cur.execute(query, values)
        self.conn.commit()
        return True
    
    def delete_topic(self, topic_id):
        query = """DELETE FROM topics WHERE id=?"""
        values = (topic_id,)
        self.cur.execute(query, values)
        self.conn.commit()
        return True

    
    
    # def get_assessments(self, course_guide_id):
    #     self.cur.execute("SELECT * FROM assessments WHERE course_guide_id = ?", (course_guide_id,))
    #     assessments_data = self.cur.fetchall()
    #     assessments = []
    #     for assessment_data in assessments_data:
    #         assessment = {
    #             'id': assessment_data[0],
    #             'course_guide_id': assessment_data[1],
    #             'name': assessment_data[2],
    #             'percentage': assessment_data[3]
    #         }
    #         assessments.append(assessment)
    #     return assessments
    
    # def add_assessment(self, course_guide_id, assessment_name, assessment_percentage):
    #     self.cur.execute("INSERT INTO assessments (course_guide_id, name, percentage) VALUES (?, ?, ?)", 
    #                     (course_guide_id, assessment_name, assessment_percentage))
    #     self.conn.commit()
    #     return True
    
   
    
    
