import os
from unittest import TestCase
from models import db, User, Recipe, Favorites
from flask import session
from app import app, CURR_USER_KEY

class UserViewsTestCase(TestCase):
    
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
      Favorites.query.delete()
      User.query.delete()
      Recipe.query.delete()

      # Create a test user
      self.user = User.signup(
          first_name="new",
          last_name="user",
          email="newuser@test.com",
          username="newuser",
          password="HASHED_PASSWORD"
        )
      recipe = Recipe(title='About recipe', image="https://lh3.googleusercontent.com/uIqpDMxdNfITOle5E_H88hFLvbochZVmXpyM6ey4e-MQcBeHFbDCWSsTkc5t1rP_50xaXdzWh6fc0NGjW8_amXw=w343-h343-c-rw-v1-e365" ,user_id=self.user.id)
      db.session.add(self.user)
      db.session.add(recipe)
      db.session.commit()

      favorites = Favorites(user_id=self.user.id, recipe_id=recipe.id)

      self.client = app.test_client()


    def tearDown(self):
        """Clean up fouled transactions."""
        db.session.rollback()  

    def test_show_favorites(self):
        """Test that favorites page displays correctly for a logged-in user."""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user.id  # Assuming user is the test user logged in
            # access the following page
            response = c.get('/favorites')
            html = response.get_data(as_text=True)

            self.assertEqual(response.status_code, 200)# Ensure the page loads
            self.assertIn('Favorites', html)# Ensure testuser2 (who is followed by user1) is on the page


    def test_access_without_logging_in(self):
        """Test that unauthorized users cannot access the favorites page."""
        with self.client as c:
            response = c.get('/favorites', follow_redirects=True)
            html = response.get_data(as_text=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn('Access unauthorized', html)

        