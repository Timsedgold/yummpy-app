import requests
from flask import Flask, render_template, redirect, session, flash, url_for, g, request
import os
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, Recipe, User, Favorites
from sqlalchemy.exc import IntegrityError
from forms import SignupForm, LoginForm, AddRecipeForm, EditRecipeForm
from dotenv import load_dotenv

load_dotenv() # Load the .env file

API_KEY = os.getenv("API_KEY")

CURR_USER_KEY = "curr_user"


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'SUPABASE_DB_URL', "postgresql:///foodrecipe_db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

print("SQLALCHEMY_DATABASE_URI:", app.config['SQLALCHEMY_DATABASE_URI'])


connect_db(app)

toolbar = DebugToolbarExtension(app)


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None
    

def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

@app.route("/")
def home_page():
    if g.user: 
        recipes = Recipe.query.limit(100).all()
        # Get IDs of all recipes that are favorited by the current user
        favorite_ids = {fav.recipe_id for fav in Favorites.query.filter_by(user_id=g.user.id).all()}

        return render_template("home.html", recipes=recipes, favorite_ids=favorite_ids)
    
    else:
        return render_template("home-anon.html")

@app.route("/signup", methods=["GET", "POST"])
def register():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """

    form = SignupForm()
    if form.validate_on_submit():
        try:
            user = User.signup(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                username=form.username.data,
                email=form.email.data,
                password=form.password.data
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template("signup.html", form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template("signup.html", form=form)
       
@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('login.html', form=form)


@app.route("/recipes")
def list_recipes():
    """List recipes and show favorite status for the current user."""
    # if g.user:
    #     favorite_ids = {fav.recipe_id for fav in Favorites.query.filter_by(user_id=g.user.id).all()}
    # else:
    #     favorite_ids = set()

    search = request.args.get('q')

    if not search:
        # Display a default list of recipes if no search term is provided
        recipes = Recipe.query.limit(100).all()

    else:
        # Try to find recipes in the database
        recipes = Recipe.query.filter(Recipe.title.ilike(f"%{search}%")).all()

        if not recipes:
            # If no recipes found in the database, make an API request
            response = requests.get(
                url="https://api.spoonacular.com/recipes/complexSearch",
                params={
                    "query": search,
                    "apiKey": API_KEY
                }
            )
            if response.status_code == 200:
                data = response.json()
                recipes = data.get('results', [])

                for api_recipe in recipes:
                    new_recipe = Recipe(
                        id=api_recipe["id"],
                        title=api_recipe["title"],
                        image=api_recipe["image"],
                    )
                    db.session.add(new_recipe)
                db.session.commit()    
            else:
                flash("Error fetching recipes from the API.", "danger")        

    return render_template("index.html", recipes=recipes)  

@app.route("/recipes/add", methods=["GET", "POST"])
def add_recipes():
    """Add new recipe to database""" 
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    form = AddRecipeForm() 

    def generate_unique_id():
        """Generate an ID above 100000 for user-submitted recipes."""
        max_id = db.session.query(db.func.max(Recipe.id)).scalar() or 100000
        return max_id + 1


    if form.validate_on_submit():
        title = form.title.data
        image = form.image.data
        vegetarian = form.vegetarian.data
        vegan = form.vegan.data
        ketogenic = form.ketogenic.data

        new_recipe = Recipe(
            id=generate_unique_id(), # Custom function for generating non-conflicting IDs
            title=title, 
            image=image,
            vegetarian=vegetarian,
            vegan=vegan,
            ketogenic=ketogenic,
            user_id=g.user.id # Associate the recipe with the current user
            )
        db.session.add(new_recipe)
        db.session.commit()

        flash("Recipe added successfully!", "success")
        return redirect("/")

    return render_template("add.html", form=form)  

@app.route("/recipes/<int:recipe_id>/edit", methods=["GET", "POST"])
def edit_recipe(recipe_id):
    """Allow the owner of the recipe to edit it.""" 
    recipe = Recipe.query.get_or_404(recipe_id)
     # Check if the logged-in user is the owner of the recipe
    if recipe.user_id != g.user.id :
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    form = EditRecipeForm(obj=recipe) 


    if form.validate_on_submit():
        recipe.title = form.title.data
        recipe.image = form.image.data
        recipe.vegan = form.vegan.data
        recipe.vegetarian = form.vegetarian.data
        recipe.ketogenic = form.ketogenic.data
        
        db.session.commit()
        flash("Recipe edited successfully!", "success")
        return redirect("/")

    return render_template("edit.html", form=form, recipe=recipe)


@app.route("/recipes/<int:recipe_id>/delete", methods=["GET", "POST"])
def delete_recipe(recipe_id):
    """Allow the owner of the recipe to delete it.""" 
    recipe = Recipe.query.get_or_404(recipe_id)
    if recipe.user_id != g.user.id:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    db.session.delete(recipe)
    db.session.commit()
    
    return redirect("/")


@app.route("/recipes/<int:recipe_id>/info")
def recipe_info(recipe_id):
    """Get information about a recipe based on it's id"""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    recipe = Recipe.query.get_or_404(recipe_id)

    return render_template("recipe-infor.html", recipe=recipe)


@app.route("/recipes/<int:recipe_id>/favorites", methods=["POST"])
def add_to_favorites(recipe_id):
    """Add a recipe to the user's favorites."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    recipe = Recipe.query.get_or_404(recipe_id)

    # Check if the recipe is already in favorites
    favorite = Favorites.query.filter_by(user_id=g.user.id, recipe_id=recipe.id).first()
    
    if favorite:
        db.session.delete(favorite)

    else:
        new_fav = Favorites(user_id=g.user.id, recipe_id=recipe_id)
        db.session.add(new_fav)
    
    
    db.session.commit()

    return redirect("/")


@app.route("/favorites")
def show_favorites():
    """Show all favorite recipes for the current user."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    # Get all favorite recipes for the logged-in user
    favorite_recipes = Recipe.query.join(Favorites, Favorites.recipe_id == Recipe.id)\
                               .filter(Favorites.user_id == g.user.id).all()


    return render_template("favorites.html", recipes=favorite_recipes)

       


@app.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()
    flash('successfully logged out', 'success')
    return redirect('/login')    
      
    
























