"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


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




class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
       
        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        # db.drop_all()
        # db.create_all()
        
        userOne = User.signup("testUser1", "JaneDoe@email.com", "password", None)
        userid1 = 1111
        userOne.id = userid1
        
        userTwo = User.signup("testUser2", "JohnDOe@email.com", "password", None)
        userid2 = 2222
        userTwo.id = userid2
        
        db.session.commit()
        
        user1 = User.query.get(userid1)
        user2 = User.query.get(userid2)
        
        self.user1 = user1
        self.userid1 = userid1
        
        self.user2 = user2
        self.userid2 = userid2
        
        self.client = app.test_client()
        
    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
        
    # def test_user_create(self):
    #     """test creation of user"""
    #     User.create
    
    def test_repr(self):
        """Test repr of class"""
        u = User(
            id='3',
            email="janeDoe100@test.com",
            username="JaneDoe",
            password="HASHED_PASSWORD"
           )
        
        self.assertTrue(len(repr(u)) > 0)
        self.assertTrue(u.username in repr(u))

        
    
    def test_is_followed_by(self): 
        """Does is followed by work?"""  
        # other_user = User(
        #     email="otherUser@test.com",
        #     username="otherUser"
        #     id=2
        #     # password="HASHED_PASSWORD",
        # )
        
        # u = User(
        #     email="test@test.com",
        #     username="testuser",
        #     password="HASHED_PASSWORD"
        #     id=1

        # )
        
        # followers = Follows(
        #     user_being_followed_id=1
        #     user_following_id=2
        # )
        
        # found_user_list = [user for user in self.followers if user == other_user]
        self.user1.following.append(self.user2)
        db.session.commit()
        
        # self.assertEquals(userOne.email, "testFollowed@test.com")
        # self.assertEquals(other_user.username, "testFollowedBy")
        # self.assertTrue(len(found_user_list) == 1)
        
        self.assertEqual(len(self.user2.following), 0)
        self.assertEqual(len(self.user2.followers), 1)
        
        
        
    def test_is_following(self):
        """Does is is following detect user following?"""
        self.user2.following.append(self.user1)
        db.session.commit()
        # u = User(
        #     email="test@test.com",
        #     username="testuser",
        #     password="HASHED_PASSWORD"
        # )
        self.assertEqual(len(self.user2.following), 1)
        self.assertEqual(len(self.user2.followers), 0)

        # db.session.add(u)
        # db.session.commit()
        
        # self.assertEqual(self.userOne.email, "JaneDoe@email.com")
        # self.assertEqual(self.userOne.userid1, 1111)
        # self.assertEqual(self.userOne.password, None)
        

      