"""Recipe model tests."""
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Recipe, Favorites
from sqlalchemy.exc import IntegrityError

os.environ['DATABASE_URL'] = "postgresql:///food-recipe-test"

from app import app


class RecipeModelTestCase(TestCase):
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

        # Create a test user
        self.user = User.signup(
            first_name="new",
            last_name="user",
            email="newuser@test.com",
            username="newuser",
            password="HASHED_PASSWORD"
        )
        db.session.commit()

        self.client = app.test_client()  

    def tearDown(self):
        """Rollback session after each test to prevent side effects."""
        db.session.rollback()

    def test_recipe_creation(self):
        """Test if recipe can successfully be created"""
        recipe = Recipe(title='About recipe', image="https://lh3.googleusercontent.com/uIqpDMxdNfITOle5E_H88hFLvbochZVmXpyM6ey4e-MQcBeHFbDCWSsTkc5t1rP_50xaXdzWh6fc0NGjW8_amXw=w343-h343-c-rw-v1-e365" ,user_id=self.user.id)   
        self.assertEqual(recipe.title, 'About recipe')
        self.assertTrue(recipe.user_id, self.user.id) 

    def test_recipe_without_title(self):
        """Test that creating a message without text fails"""
        
        recipe = Recipe(title=None, image="https://lh3.googleusercontent.com/uIqpDMxdNfITOle5E_H88hFLvbochZVmXpyM6ey4e-MQcBeHFbDCWSsTkc5t1rP_50xaXdzWh6fc0NGjW8_amXw=w343-h343-c-rw-v1-e365" ,user_id=self.user.id)
        # Expect an IntegrityError because title is required
        with self.assertRaises(IntegrityError):
            db.session.add(recipe)
            db.session.commit()

    def test_recipe_without_user(self):
        """Test that creating a recipe without user fails"""
        
        recipe = Recipe(title='About recipe', image="https://lh3.googleusercontent.com/uIqpDMxdNfITOle5E_H88hFLvbochZVmXpyM6ey4e-MQcBeHFbDCWSsTkc5t1rP_50xaXdzWh6fc0NGjW8_amXw=w343-h343-c-rw-v1-e365", user_id=None)
        # Expect an IntegrityError because user is required
        with self.assertRaises(IntegrityError):
            db.session.add(recipe)
            db.session.commit()    