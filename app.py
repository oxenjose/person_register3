from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'byt-ut-denna-till-en-hemlig-nyckel'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///personalregister.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Databasmodeller ---

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)  # 'Man', 'Kvinna', 'Annat'
    employee_number = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    position = db.Column(db.String(100), nullable=False)
    comments = db.relationship('Comment', backref='employee', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Employee {self.first_name} {self.last_name}>'

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)

# --- Routes ---

@app.route('/')
def index():
    """Startsida som visar alla anställda."""
    employees = Employee.query.order_by(Employee.last_name).all()
    return render_template('index.html', employees=employees)

@app.route('/add', methods=['GET', 'POST'])
def add_employee():
    """Lägg till en ny anställd."""
    if request.method == 'POST':
        # Enkel validering
        if not request.form.get('first_name') or not request.form.get('last_name'):
            flash('För- och efternamn är obligatoriska!', 'error')
            return redirect(url_for('add_employee'))

        new_employee = Employee(
            first_name=request.form['first_name'],
            last_name=request.form['last_name'],
            age=int(request.form['age']),
            gender=request.form['gender'],
            employee_number=request.form['employee_number'],
            email=request.form['email'],
            position=request.form['position']
        )
        try:
            db.session.add(new_employee)
            db.session.commit()
            flash('Anställd har lagts till!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Ett fel uppstod: {e}', 'error')
            return redirect(url_for('add_employee'))
    return render_template('add_employee.html')

@app.route('/employee/<int:id>', methods=['GET', 'POST'])
def employee_detail(id):
    """Visa detaljer för en anställd och hantera kommentarer."""
    employee = Employee.query.get_or_404(id)

    if request.method == 'POST':
        # Lägg till kommentar
        comment_text = request.form.get('comment_text')
        if comment_text:
            new_comment = Comment(text=comment_text, employee_id=employee.id)
            db.session.add(new_comment)
            db.session.commit()
            flash('Kommentar tillagd!', 'success')
            return redirect(url_for('employee_detail', id=employee.id))

    return render_template('employee_detail.html', employee=employee)

@app.route('/delete/<int:id>', methods=['POST'])
def delete_employee(id):
    """Ta bort en anställd."""
    employee = Employee.query.get_or_404(id)
    try:
        db.session.delete(employee)
        db.session.commit()
        flash(f'{employee.first_name} {employee.last_name} har tagits bort.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Kunde inte ta bort: {e}', 'error')
    return redirect(url_for('index'))

@app.route('/search')
def search():
    """Sök efter anställda."""
    query = request.args.get('q', '').strip()
    results = []
    if query:
        # Sök i flera fält samtidigt
        search_term = f'%{query}%'
        results = Employee.query.filter(
            db.or_(
                Employee.first_name.ilike(search_term),
                Employee.last_name.ilike(search_term),
                Employee.email.ilike(search_term),
                Employee.employee_number.ilike(search_term),
                Employee.position.ilike(search_term)
            )
        ).all()
    return render_template('search.html', query=query, results=results)

# --- Initiering av databasen ---

def init_db():
    """Skapar databastabellerna och lägger till exempeldata."""
    with app.app_context():
        db.create_all()
        # Kontrollera om det redan finns data
        if not Employee.query.first():
            sample_employees = [
                Employee(first_name='Anna', last_name='Andersson', age=32, gender='Kvinna',
                         employee_number='JY001', email='anna.andersson@jysk.se', position='Butikschef'),
                Employee(first_name='Erik', last_name='Johansson', age=28, gender='Man',
                         employee_number='JY002', email='erik.johansson@jysk.se', position='Säljare'),
                Employee(first_name='Maria', last_name='Lindberg', age=41, gender='Kvinna',
                         employee_number='JY003', email='maria.lindberg@jysk.se', position='Lagerarbetare'),
                Employee(first_name='Karl', last_name='Svensson', age=35, gender='Man',
                         employee_number='JY004', email='karl.svensson@jysk.se', position='Säljare'),
            ]
            db.session.add_all(sample_employees)
            db.session.commit()
            print("Databasen har initierats med exempeldata.")

# --- Kör applikationen ---

if __name__ == '__main__':
    init_db()
    app.run(debug=True)