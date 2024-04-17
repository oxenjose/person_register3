from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///databas.db'  # Specifies the path to your SQLite database
db = SQLAlchemy(app)

# Person model
class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    country = db.Column(db.String(100), nullable=False)
    image_filename = db.Column(db.String(100))  # Path to image file, if any

def init_db():
    """Initializes the database and seeds it if necessary."""
    db.create_all()
    # Seed the database with some initial data if it's empty
    if not Person.query.first():  # Checks if there's any data in the database
        sample_people = [
            Person(name="Carlos Ruiz", email="carlos@example.com", age=34, country="Spain", image_filename='carlos.jpg'),
            Person(name="Maria Garcia", email="maria@example.com", age=28, country="Spain", image_filename='maria.jpg'),
            Person(name="Jose Fernandez", email="jose@example.com", age=45, country="Spain", image_filename='jose.jpg'),
            Person(name="Ana Torres", email="ana@example.com", age=32, country="Spain", image_filename='ana.jpg'),
            Person(name="Pablo Gómez", email="pablo@example.com", age=29, country="Spain", image_filename='pablo.jpg')
        ]
        db.session.add_all(sample_people)
        db.session.commit()

@app.route('/')
def home():
    """Route to display the homepage."""
    return render_template("homepage.html")

@app.route("/persons")
def persons():
    """Route to display all persons."""
    all_persons = Person.query.all()
    return render_template("persons.html", persons=all_persons)

@app.route("/person/<int:id>")
def person(id):
    """Route to display a specific person by ID, with 404 handling."""
    person = Person.query.get_or_404(id)
    return render_template("person.html", person=person)

if __name__ == "__main__":
    with app.app_context():
        init_db()  # Initialize and possibly seed the database before running the app
    app.run(debug=True)  # Consider setting debug to False in a production environment
