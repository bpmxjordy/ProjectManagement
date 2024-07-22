from app import app, db
from models import Client, Employee, Project, Task, ProjectBudget
from random import choice, randint, uniform
from faker import Faker

fake = Faker()

# Helper function to generate random data
def random_choice(choices):
    return choice(choices)

def random_time_spent():
    return round(uniform(1, 20), 2)

def random_budget():
    return round(uniform(5000, 50000), 2)

def create_clients(num):
    clients = []
    for _ in range(num):
        client = Client(client_name=fake.company())
        clients.append(client)
        db.session.add(client)
    db.session.commit()
    return clients

def create_employees(num):
    employees = []
    for _ in range(num):
        employee = Employee(
            employee_name=fake.name(),
            hourly_wage=round(uniform(20, 100), 2)
        )
        employees.append(employee)
        db.session.add(employee)
    db.session.commit()
    return employees

def create_projects(clients, num):
    projects = []
    for _ in range(num):
        project = Project(
            client_id=random_choice(clients).client_id,
            project_name=fake.bs().capitalize(),
            budget=random_budget(),
            time_spent=random_time_spent()
        )
        projects.append(project)
        db.session.add(project)
    db.session.commit()
    return projects

def create_tasks(projects, employees, num_tasks_per_project=10):
    tasks = []
    for project in projects:
        for _ in range(num_tasks_per_project):
            task = Task(
                project_id=project.project_id,
                task_name=fake.sentence(nb_words=4),
                difficulty_level=random_choice(['easy', 'medium', 'hard']),
                employee_id=random_choice(employees).employee_id,
                time_spent=random_time_spent(),
                status=random_choice(['in progress', 'done'])
            )
            tasks.append(task)
            db.session.add(task)
    db.session.commit()
    return tasks

def create_project_budgets(projects):
    for project in projects:
        spent_budget = sum(
            task.time_spent * Employee.query.get(task.employee_id).hourly_wage
            for task in Task.query.filter_by(project_id=project.project_id).all()
        )
        project_budget = ProjectBudget(
            project_id=project.project_id,
            allocated_budget=project.budget,
            spent_budget=round(spent_budget, 2)
        )
        db.session.add(project_budget)
    db.session.commit()

with app.app_context():
    db.drop_all()
    db.create_all()

    # Create clients, employees, projects, tasks, and project budgets
    clients = create_clients(10)
    employees = create_employees(50)
    projects = create_projects(clients, 20)
    tasks = create_tasks(projects, employees)
    create_project_budgets(projects)

    print("Database populated with sample data.")
