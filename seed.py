import os
import pdb
import requests
from app import app
from models import db, Recipe
from dotenv import load_dotenv

load_dotenv() # Load the .env file

API_KEY = os.getenv("API_KEY")

BASE_URL = 'https://api.spoonacular.com/recipes'

# Define placeholder recipes
PLACEHOLDER_RECIPES = [
    {"id": 1, "title": "Spaghetti Carbonara", "image": "https://s23209.pcdn.co/wp-content/uploads/2014/03/IMG_2622edit.jpg"},
    {"id": 2, "title": "Chicken Alfredo", "image": "https://www.budgetbytes.com/wp-content/uploads/2022/07/Chicken-Alfredo-V3-768x1024.jpg"},
    {"id": 3, "title": "Beef Tacos", "image": "https://feelgoodfoodie.net/wp-content/uploads/2017/04/Ground-Beef-Tacos-9.jpg"},
    {"id": 4, "title": "Vegetable Stir Fry", "image": "https://therecipecritic.com/wp-content/uploads/2019/08/vegetable_stir_fry.jpg"},
    {"id": 5, "title": "Caesar Salad", "image": "https://natashaskitchen.com/wp-content/uploads/2019/01/Caesar-Salad-Recipe-3-600x900.jpg"},
    {"id": 6, "title": "Margherita Pizza", "image": "https://www.abeautifulplate.com/wp-content/uploads/2015/08/the-best-homemade-margherita-pizza-1-4.jpg"},
    {"id": 7, "title": "Grilled Cheese Sandwich", "image": "https://www.recipetineats.com/tachyon/2023/07/Grilled-Cheese-sandwich-photo-main.jpg?resize=900%2C1125&zoom=1"},
    {"id": 8, "title": "Tomato Soup", "image": "https://natashaskitchen.com/wp-content/uploads/2021/08/Tomato-Soup-Recipe-4-728x1092.jpg"},
    {"id": 9, "title": "BBQ Chicken Wings", "image": "https://www.jessicagavin.com/wp-content/uploads/2023/01/BBQ-chicken-wings-21-1025x1536.jpg"},
    {"id": 10, "title": "Vegetable Curry", "image": "https://www.jessicagavin.com/wp-content/uploads/2023/01/BBQ-chicken-wings-21-1025x1536.jpg"},
    {"id": 11, "title": "Pasta Primavera", "image": "https://cdn.loveandlemons.com/wp-content/uploads/2022/06/pasta-primavera-1.jpg"},
    {"id": 12, "title": "Sushi Rolls", "image": "https://hips.hearstapps.com/hmg-prod/images/spicy-tuna-roll-5-1652806800.jpg?crop=0.842xw:1.00xh;0,0&resize=980:*"},
    {"id": 13, "title": "French Toast", "image": "https://tastesbetterfromscratch.com/wp-content/uploads/2022/09/French-Toast-1-1024x1536.jpg"},
    {"id": 14, "title": "Shrimp Scampi", "image": "https://cafedelites.com/wp-content/uploads/2018/03/Garlic-Butter-Shrimp-IMAGE-15-1024x1536.jpg"},
    {"id": 15, "title": "Avocado Toast", "image": "https://cookieandkate.com/images/2012/04/avocado-toast-recipe-3.jpg"},
    {"id": 16, "title": "Chili Con Carne", "image": "https://www.allrecipes.com/thmb/XcVfbUXWJVZNfOR7KHArA9NUi-s=/750x0/filters:no_upscale():max_bytes(150000):strip_icc():format(webp)/89993-award-winning-chili-con-carne-ddmfs-3x4-4e3a48f5505a4c998415c261507b0a76.jpg"},
    {"id": 17, "title": "Falafel Wrap", "image": "https://cookingwithayeh.com/wp-content/uploads/2024/03/Falafel-Wrap-1-1024x1536.jpg"},
    {"id": 18, "title": "Chicken Noodle Soup", "image": "https://tastesbetterfromscratch.com/wp-content/uploads/2017/10/Chicken-Noodle-Soup-2.jpg"},
    {"id": 19, "title": "Beef Stew", "image": "https://www.spendwithpennies.com/wp-content/uploads/2018/09/SpendWithPennies-Homemade-Beef-Stew-21.jpg"},
    {"id": 20, "title": "Greek Salad", "image": "https://cdn.loveandlemons.com/wp-content/uploads/2019/07/greek-salad-2.jpg"}
]

with app.app_context():
    db.drop_all()
    db.create_all()

    def fetch_recipe_ids():
        """Fetch recipe IDs from the Spoonacular API."""
        url = f"{BASE_URL}/complexSearch"
        params = {
            "apiKey": API_KEY,
            "number": 100 # Specify the number of recipes you want to fetch
        }
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            recipe_ids = [recipe["id"] for recipe in data.get("results", [])]
            print(f"Fetched {len(recipe_ids)} recipe IDs")
            return recipe_ids
        else:
            print("API unavailable, using placeholder recipes.")
            return None

    def fetch_recipe_info(recipe_id):
        """Fetch detailed information for a recipe by its ID."""
        url = f"{BASE_URL}/{recipe_id}/information"
        params = {"apiKey": API_KEY}
        response = requests.get(url, params=params)
        return response.json()

    def seed_recipes():
        """Seed recipe data into the database."""
        recipe_ids = fetch_recipe_ids()
        
        if recipe_ids:
            for recipe_id in recipe_ids:
                recipe_info = fetch_recipe_info(recipe_id)
                
                # Parse the recipe information as needed
                recipe = Recipe(
                    title=recipe_info["title"],
                    image=recipe_info["image"],
                    vegetarian=recipe_info.get("vegetarian", False),
                    ketogenic=recipe_info.get("ketogenic", False),
                    vegan=recipe_info.get("vegan", False)
                )
                db.session.add(recipe)
            db.session.commit()
        else:
            # If API is unavailable, add placeholder recipes
            for placeholder in PLACEHOLDER_RECIPES:
                recipe = Recipe(
                    title=placeholder["title"],
                    image=placeholder["image"],
                    vegetarian=placeholder.get("vegetarian", False),
                    ketogenic=placeholder.get("ketogenic", False),
                    vegan=placeholder.get("vegan", False)
                )
                db.session.add(recipe)
            db.session.commit()

        print("Database seeded successfully!")

    try:
        seed_recipes()
    except Exception as e:
        pdb
        print(f"Error seeding database: {e}")