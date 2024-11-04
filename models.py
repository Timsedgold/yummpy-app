"""Models for Food Recipe app."""
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy


bcrypt = Bcrypt()
db = SQLAlchemy()

class Recipe(db.Model):
    __tablename__ = "recipes"

    id = db.Column(db.Integer,
                   primary_key=True)
    title = db.Column(db.Text,
                      nullable=False)
    image = db.Column(db.Text,
                      nullable=False)
    vegetarian = db.Column(db.Boolean,
                            default=False)
    ketogenic = db.Column(db.Boolean,
                            default=False)
    vegan = db.Column(db.Boolean,
                            default=False)
    user_id = db.Column(db.Integer,
                        db.ForeignKey("users.id"))
    user = db.relationship("User", backref="recipes")
    
class Favorites(db.Model):
    """Model for favorite recipes"""    
    __tablename__ = "favorites"

    id = db.Column(db.Integer,
                   primary_key=True)
    
    user_id = db.Column(db.Integer,
                        db.ForeignKey("users.id"))
    recipe_id = db.Column(db.Integer,
                          db.ForeignKey("recipes.id"))
    user = db.relationship("User", backref="favorites")
        



class User(db.Model):
    """Users in the system"""

    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )
  
    first_name = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    ) 

    last_name = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    def __repr__(self):
        return f"<User #{self.id}: {self.first_name}, {self.last_name}, {self.username}, {self.email}>"
    
    @classmethod
    def signup(cls, first_name, last_name, username, email, password,  ):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            password=hashed_pwd
        )

        db.session.add(user)
        return user
    

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False



    
    







def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)






























