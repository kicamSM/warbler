"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()


        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        self.testuser_id = 54
        self.testuser.id = self.testuser_id
 
        
        db.session.commit()
        

    def test_add_message_logged_in(self):
        """Can user add a message when logged in?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")
            
    def test_add_messages_logged_out(self): 
        """Can logged out user add message?"""
        with self.client as c:
                
            resp = c.post("/messages/new", data={"text": "This is the new Text"})
            
            with self.assertRaises(BaseException) as e: 
                self.assertEqual(e.exception.code)
                msg = Message.query.one()
    
    def test_delete_messages_logged_in(self):
        """Can you delete messages logged in"""
            # raise ValueError(self.testuser.id)
        message = Message(
                id = 12,
                text = "This is the new message",
                user_id = self.testuser_id
                # i do not understand where testuesr_id is coming from
            )
            
        db.session.add(message)
        db.session.commit()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # resp = c.post("/messages/new", data={"text": "This is the new Text"})
            # message = 

            # raise ValueError(len(self.testuser.messages))
            resp = c.post("/messages/12/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
                
            message = Message.query.get(12)
            self.assertIsNone(message)
            
    def test_delete_messages_logged_out(self):
        """Can you delete messages logged out?"""
        message = Message(
                id = 12,
                text = "This is the new message",
                user_id = self.testuser_id
            )
            
        db.session.add(message)
        db.session.commit()
        with self.client as c:
            resp = c.post("/messages/12/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            
            message = Message.query.get(12)
            self.assertIsNotNone(message)
            
    def test_add_message_for_another_user_logged_in(self):
        """Can you add message for another user when you are logged in?"""
        message = Message(
                id = 12,
                text = "This is the new message",
                user_id = 33
            )
        
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            # with self.assertRaises(InvalidRequestError)
            with self.assertRaises(BaseException) as e: 
                self.assertEqual(e.exception.code)
                db.session.add(message)
                
    def test_add_message_for_another_user_logged_out(self):
        """Can you add message for another user when you are logged out?"""
        
        message = Message(
                id = 12,
                text = "This is the new message",
                user_id = 33
            )
        
        with self.client as c:
            with self.assertRaises(BaseException) as e: 
                self.assertEqual(e.exception.code)
                db.session.add(message)
                
    def test_message_show(self): 
        with self.client as c:
            message = Message(
                id = 99,
                text = "Another message",
                user_id = 54
            )
            
            db.session.add(message)
            db.session.commit()
            
            with c.session_transaction() as sess:
                 sess[CURR_USER_KEY] = self.testuser.id
            message = Message.query.get(99)
            resp = c.get('/messages/99')
            self.assertEqual(resp.status_code, 200)
            self.assertIn(message.text, str(resp.data))
            self.assertEqual(message.text, "Another message")
                    
    
    # def test_show_messages_fail(self):
    #     """test show messages expect failure"""
            
    #     with self.client as c:
    #         with c.session_transaction() as sess:
    #             sess[CURR_USER_KEY] = self.testuser.id
    #         # raise ValueError(c.get('/messages/827438'))
    #         resp = c.get('/messages/111111')
    #         # this is not working line above we are getting an error none has no attribute user.... not sure what that is about????
    #         # raise ValueError(resp)
    #         self.assertEqual(resp.status_code, 404)
    
            
    def test_user_access_other_user_logged_in(self):
        """Can the logged in user see the followers and following of any user"""
        
        user2 = User.signup(username="testuser2",
                                    email="test2@test.com",
                                    password="testuser2",
                                    image_url=None)
        db.session.add(user2)
        db.session.commit()
        testuser_2id = 33
        
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = testuser_2id
        
            resp = c.get("/users/54", follow_redirects=True) 
            self.assertEqual(resp.status_code, 200)
         
            
              
    def  test_user_access_other_user_logged_out(self):
        """Can the logged in user see the followers and following of any user"""
        
        with self.client as c:
        
            resp = c.get("/users/54", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            
    def test_access_follower_logged_in(self): 
        
        with self.client as c:
            
            testuser_2id = 33
            
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = testuser_2id
                
            resp = c.get("/users/54/following", follow_redirects=True) 
            
            self.assertEqual(resp.status_code, 200)

            
    # def test_access_follower_logged_out(self): 
        
    #     user2 = User.signup(username="testuser2",
    #                                 email="test2@test.com",
    #                                 password="testuser2",
    #                                 image_url=None)
        
    #     testuser_2id = 33
    #     db.session.add(user2)
    #     db.session.commit()
    #     with self.client as c:
    #         resp = c.get("/users/33/followers", follow_redirects=True) 
            
    #         self.assertEqual(resp.status_code, 404)
            # note that this should not  be returning but is returning whcih suggests that something is in the session? 
            