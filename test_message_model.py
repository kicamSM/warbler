"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_message_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

class MessageModelTestCase(TestCase):
    """Test views for messages."""
    
    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()
        
        userOne = User.signup("testUser1", "JaneDoe@email.com", "password", None)
        self.user_id = 1111
        userOne.id = self.user_id
        db.session.commit()
        self.userOne = User.query.get(self.user_id)

        # this is setting up a user_id for that user 
        
        message = Message(user_id=1111, text="This is the first message for user one")
        self.message_id = 23
        message.id = self.message_id
        db.session.add(message)
        db.session.commit()


        self.client = app.test_client()
        
    def tearDown(self):
        """Returns to setUp for next function"""
        res = super().tearDown()
        # this is saying we can tear down anything created and we are accessing the method of the baseclass?
        
        db.session.rollback()
        return res
        
    def test_messages_add(self):
        """test add messages"""
        # each message has only text 
        
        userTwo = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        
        self.user_id = 2222
        userTwo.id = self.user_id
        db.session.add(userTwo)
        db.session.commit()
        self.userTwo = User.query.get(self.user_id)

        # userTwo = User.signup("testUser2", "JaneDoe@email.com", "password", None)
        message1 = Message(user_id=2222, text="This is the first message for user two")
        message2 = Message(user_id=2222, text="This is the second message for user two")
        
        db.session.add(message1)
        db.session.add(message2)
        db.session.commit()
        
        self.assertEqual(len(userTwo.messages), 2)
        
        
# ************************************************************************
# note that I think technically these should be in the user views model 
        
    def test_messages_add_fail(self):
        """Fails adding a message when no user id exists""" 
        
        with self.assertRaises(BaseException) as e: 
            self.assertEqual(e.exception.code)
            message1 = Message(user_id=1111, text=None)
            
    # def test_messages_show(self): 
    #     with app.test_client() as client:
    #         resp = client.get('/messages/23')
    #         self.assertIn('<p>This is the first message for user one</p>', html)
    
    def test_add_likes(self): 
        """adds a like to a message"""
        # raise ValueError(len(self.userOne.likes))
        message = Message.query.get(self.message_id)
        # raise ValueError(message)
        self.userOne.likes.append(message)
        db.session.commit()
        self.assertEqual(len(self.userOne.likes), 1)
    
    def test_messages_destroy(self): 
        """Deletes message"""
        message = self.userOne.messages[0]
        # raise ValueError(message)
        db.session.delete(message)
        db.session.commit()
        self.assertEqual(len(self.userOne.messages), 0)
    
        
    
        