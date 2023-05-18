"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py


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


class UserViewTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()


        self.client = app.test_client()

        self.testuser1 = User.signup(username="testuser1",
                                    email="test1@test.com",
                                    password="testuser1",
                                    image_url=None)
        self.testuser_id1 = 111
        self.testuser1.id1 = self.testuser_id1
        
        self.testuser2 = User.signup(username="testuser2",
                                    email="test2@test.com",
                                    password="testuser2",
                                    image_url=None)
        self.testuser_id2 = 222
        self.testuser2.id2 = self.testuser_id2
 
        db.session.commit()
        
    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp

        
    def test_signup(self):
        """test signing up user"""
        with self.client as c:
            new_user = User.signup(username="testuser3",
                                    email="test@test3.com",
                                    password="testuser3",
                                    image_url=None)
        db.session.add(new_user)
        db.session.commit()
        
        users = User.query.all()
        
        self.assertEqual(len(users), 3)
        
    def test_list_users(self): 
        with self.client as c:
            resp = c.get("/users")
            
        self.assertIn("@testuser1", str(resp.data))
        self.assertIn("@testuser2", str(resp.data))
        self.assertEqual(resp.status_code, 200)
        
    
            
        
            