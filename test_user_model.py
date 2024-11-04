"""User model tests."""
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Recipe, Favorites
from sqlalchemy.exc import IntegrityError

os.environ['DATABASE_URL'] = "postgresql:///food-recipe-test"

from app import app


class UserModelTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up an application context and create tables once for all tests."""
        cls.app_context = app.app_context()
        cls.app_context.push()
        db.create_all()

    @classmethod
    def tearDownClass(cls):
        """Clean up the database and remove the application context."""
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()

    def setUp(self):
        """Clear data before each test."""
        Favorites.query.delete()
        User.query.delete()
        Recipe.query.delete()
        db.session.commit()

        self.client = app.test_client()  

    def tearDown(self):
        """Rollback session after each test to prevent side effects."""
        db.session.rollback()      

    def test_user_model(self):
        """Test basic user model functionality."""
        u = User(
            first_name="test",
            last_name="user",
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )    
        db.session.add(u)
        db.session.commit() 

        # User should have no recipes & no favorites
        self.assertEqual(len(u.recipes), 0)
        self.assertEqual(len(u.favorites), 0)

    def test_user_repr(self):
        """Test that the repr method works as expected."""
    
        u = User(
            first_name="test",
            last_name="user",
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        self.assertEqual(repr(u), f"<User #{u.id}: test, user, testuser, test@test.com>")   


    def test_signup_success(self):
        # Call signup to create a user
        u = User.signup(
            first_name="new",
            last_name="user",
            email="newuser@test.com",
            username="newuser",
            password="HASHED_PASSWORD"
        )
        # Commit the session to add the user to the database
        db.session.commit()

        # Check if user is created successfully
        self.assertIsNotNone(u)
        self.assertEqual(u.first_name, 'new')
        self.assertEqual(u.last_name, 'user')
        self.assertEqual(u.username, 'newuser')
        self.assertEqual(u.email, 'newuser@test.com')
        self.assertTrue(u.password.startswith('$2b$')) #Bcrypt hash starts with $2b$

    def test_signup_fail(self):

        with self.assertRaises(IntegrityError):
            u = User.signup(
            first_name="new",
            last_name="user",
            email=None, #missing email
            username="newuser",
            password="HASHED_PASSWORD"
        )
            db.session.commit()
        db.session.rollback()  

        with self.assertRaises(IntegrityError):
            u = User.signup(
            first_name="new",
            last_name="user",
            email="newuser@test.com",
            username=None,
            password="HASHED_PASSWORD"
        )
            db.session.commit()
        db.session.rollback()   

    def test_authenticate_success(self):
        """Test that authenticate returns the user with valid credentials."""

        # Create a test user
        user = User.signup('test', 'user', 'testuser', 'test@test.com', 'password123')
        db.session.commit()
         
        # Test that valid username and password return the user 
        auth_user = User.authenticate('testuser', 'password123')
        self.assertIsNotNone(auth_user)
        self.assertEqual(auth_user.username, 'testuser')

    def test_authenticate_invalid_username(self):
        """Test that authenticate returns False when username is invalid."""

        #create a test user
        user = User.signup('test', 'user', 'testuser', 'test@test.com', 'password123')
        db.session.commit()

        auth_user = User.authenticate('invaliduser', 'password123')
        self.assertFalse(auth_user)

    def test_authenticate_invalid_password(self):
        """Test that authenticate returns False when username is invalid."""

        #create a test user
        user = User.signup('test', 'user', 'testuser', 'test@test.com', 'password123')
        db.session.commit()

        auth_user = User.authenticate('testuser', 'invalidpassword')
        self.assertFalse(auth_user)    
