"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User, Follows

from bs4 import BeautifulSoup
# this allows you to pull out the html from the resp.data (parse)

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

import re


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
        self.testuser1.id = self.testuser_id1
        
        self.testuser2 = User.signup(username="testuser2",
                                    email="test2@test.com",
                                    password="testuser2",
                                    image_url=None)
        self.testuser_id2 = 222
        self.testuser2.id = self.testuser_id2
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
        
    #would like to be able to test the html with this below but still working on it 
    
    # def contains_link_1(html_string):
    # # The regex pattern r'<a>\s*1\s*</a>' means:
    # # '<a>' - match the literal string '<a>'
    # # '\s*' - match zero or more whitespace characters
    # # '1'   - match the literal character '1'
    # # '\s*' - match zero or more whitespace characters
    # # '</a>' - match the literal string '</a>'
    #     return bool(re.search(r'<a>\s*1\s*</a>', html_string))
    
    # still having issues with the ones below 
        
    # def test_user_show_following_logged_in(self):
    #     """test show following users"""
    #     following1 = Follows(user_being_followed_id=self.testuser1.id, user_following_id=self.testuser2.id)
    #     db.session.add(following1)
    #     db.session.commit()
        
    #     with self.client as c:
    #         with c.session_transaction() as sess:
    #             sess[CURR_USER_KEY] = self.testuser1.id
    #         resp = c.get(f"/users/{self.testuser1.id}/following",  follow_redirects=True)
            
    #     self.assertEqual(resp.status_code, 200)
    #     # self.assertIn("@testuser2", str(resp.data))
    #     self.contains_link_1(str(resp.data))
        
        # self.assertIn("<a>1</a>", str(resp.data))
        # couple of options here you can return the user id of the original user and then tru and say that that user has one follower 
        # you can return the id of the testuser2 but that is saying it is not bound to session
        
        # note I did try and add a user in there which did return somehitng but it did not look like it was returning what I expected. 
        
        # soup = BeautifulSoup(str(resp.data), 'html.parser')
        # found = soup.find_all("a", "1")
        # self.assertEqual(len(found), 1)
 
        
        
        
    def test_user_show_following_logged_out(self):
        """test show following users fails"""
        following1 = Follows(user_being_followed_id=self.testuser1.id, user_following_id=self.testuser2.id)
        
        with self.client as c:
            resp = c.get(f"/users/{self.testuser1.id}/following",  follow_redirects=True)
            
        self.assertEqual(resp.status_code, 200)
        self.assertNotIn("@testuser2", str(resp.data))
        # unsure if this one is working the way its supposed to. I did remove it in session and it is not returning but it is just giving me an assertion error and still is giving me a 200 status code which is not what I would have expected 
        
    def test_user_show_followed(self): 
        """test show followed users"""
        followedUser = Follows(user_being_followed_id=self.testuser1.id, user_following_id=self.testuser2.id)
        db.session.add(followedUser)
        db.session.commit()
        
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1.id
            resp = c.get(f"/users/{self.testuser1.id}/followers")
        
        self.assertEqual(resp.status_code, 200)
        self.assertIn("@testuser1", str(resp.data))
        
    def test_unauthorized_following_page_access(self):
        """test the unathorized following page"""
            # self.setup_followers()
        f1 = Follows(user_being_followed_id=self.testuser2.id, user_following_id=self.testuser1.id)
        db.session.add(f1)
        db.session.commit()
        with self.client as c:

            resp = c.get(f"/users/{self.testuser1.id}/following", follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        # self.assertNotIn("@testuser2", str(resp.data))
        self.assertIn("Access unauthorized", str(resp.data))        

    
            
        
            