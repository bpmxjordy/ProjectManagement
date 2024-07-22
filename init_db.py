from app import app, db
from models import Client, Employee, Project, Task, ProjectBudget

with app.app_context():
    db.create_all()
    print("Database tables created.")
