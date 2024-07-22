from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Client(db.Model):
    client_id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(255), nullable=False)

class Employee(db.Model):
    employee_id = db.Column(db.Integer, primary_key=True)
    employee_name = db.Column(db.String(255), nullable=False)
    hourly_wage = db.Column(db.Numeric, nullable=False)

class Project(db.Model):
    project_id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.client_id'), nullable=False)
    project_name = db.Column(db.String(255), nullable=False)
    budget = db.Column(db.Numeric, nullable=False)
    time_spent = db.Column(db.Numeric, nullable=True)

class Task(db.Model):
    task_id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.project_id'), nullable=False)
    task_name = db.Column(db.String(255), nullable=False)
    difficulty_level = db.Column(db.Enum('easy', 'medium', 'hard'), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.employee_id'), nullable=False)
    time_spent = db.Column(db.Numeric, nullable=True)
    status = db.Column(db.Enum('in progress', 'done'), nullable=False)

class ProjectBudget(db.Model):
    project_id = db.Column(db.Integer, db.ForeignKey('project.project_id'), primary_key=True)
    allocated_budget = db.Column(db.Numeric, nullable=False)
    spent_budget = db.Column(db.Numeric, nullable=True)
