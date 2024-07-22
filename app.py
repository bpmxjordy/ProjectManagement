from flask import Flask, jsonify, request
from flask_cors import CORS
from models import db, Client, Project, Task, Employee, ProjectBudget

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project_management.db'
db.init_app(app)

@app.route('/projects', methods=['GET'])
def get_projects():
    projects = Project.query.all()
    results = []
    for project in projects:
        tasks = Task.query.filter_by(project_id=project.project_id).all()
        task_list = [{
            'task_id': task.task_id,
            'task_name': task.task_name,
            'difficulty_level': task.difficulty_level,
            'employee_name': Employee.query.get(task.employee_id).employee_name,
            'time_spent': round(task.time_spent, 1),  # Format time spent per task
            'status': task.status
        } for task in tasks]

        # Calculate the cumulative time spent on the project
        total_time_spent = sum(task.time_spent for task in tasks)
        
        # Calculate the amount spent so far
        amount_spent = sum(task.time_spent * Employee.query.get(task.employee_id).hourly_wage for task in tasks)

        results.append({
            'project_id': project.project_id,
            'project_name': project.project_name,
            'client_name': Client.query.get(project.client_id).client_name,
            'budget': round(project.budget, 2),  # Format the budget to 2 decimal places
            'time_spent': round(total_time_spent, 1),  # Format the total time to 1 decimal place
            'amount_spent': round(amount_spent, 2),  # Format the amount spent to 2 decimal places
            'tasks': task_list
        })
    return jsonify(results)

@app.route('/projects/<int:project_id>', methods=['GET'])
def get_project(project_id):
    project = Project.query.get_or_404(project_id)
    tasks = Task.query.filter_by(project_id=project_id).all()
    return jsonify({
        'project': {
            'project_id': project.project_id,
            'project_name': project.project_name,
            'client_name': Client.query.get(project.client_id).client_name,
            'budget': project.budget,
            'time_spent': project.time_spent
        },
        'tasks': [{
            'task_id': task.task_id,
            'task_name': task.task_name,
            'time_spent': task.time_spent,
            'status': task.status
        } for task in tasks]
    })

@app.route('/projects/<int:project_id>', methods=['PUT'])
def update_project(project_id):
    data = request.get_json()
    project = Project.query.get_or_404(project_id)
    project.project_name = data['project_name']
    project.budget = data['budget']
    project.client_id = Client.query.filter_by(client_name=data['client_name']).first().client_id
    db.session.commit()
    return jsonify({'message': 'Project updated successfully'})

@app.route('/employees', methods=['GET'])
def get_employees():
    employees = Employee.query.all()
    return jsonify([{'employee_id': employee.employee_id, 'employee_name': employee.employee_name, 'hourly_wage': employee.hourly_wage} for employee in employees])

@app.route('/clients', methods=['GET'])
def get_clients():
    clients = Client.query.all()
    return jsonify([{
        'client_id': client.client_id,
        'client_name': client.client_name
    } for client in clients])

@app.route('/clients/<int:client_id>', methods=['GET'])
def get_client(client_id):
    client = Client.query.get_or_404(client_id)
    projects = Project.query.filter_by(client_id=client_id).all()
    return jsonify({
        'client': {
            'client_id': client.client_id,
            'client_name': client.client_name
        },
        'projects': [{
            'project_id': project.project_id,
            'project_name': project.project_name,
            'budget': project.budget,
            'time_spent': project.time_spent
        } for project in projects]
    })

@app.route('/clients', methods=['POST'])
def add_client():
    data = request.get_json()
    new_client = Client(client_name=data['client_name'])
    db.session.add(new_client)
    db.session.commit()
    return jsonify({'message': 'Client added successfully'})


@app.route('/employees/<int:employee_id>', methods=['GET'])
def get_employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    tasks = Task.query.filter_by(employee_id=employee_id).all()
    project_ids = {task.project_id for task in tasks}
    projects = Project.query.filter(Project.project_id.in_(project_ids)).all()

    project_list = []
    for project in projects:
        project_tasks = [task for task in tasks if task.project_id == project.project_id]
        task_list = [{
            'task_id': task.task_id,
            'task_name': task.task_name,
            'difficulty_level': task.difficulty_level,
            'time_spent': task.time_spent,
            'status': task.status
        } for task in project_tasks]
        project_list.append({
            'project_id': project.project_id,
            'project_name': project.project_name,
            'client_name': Client.query.get(project.client_id).client_name,
            'budget': project.budget,
            'tasks': task_list
        })

    return jsonify({
        'employee': {
            'employee_id': employee.employee_id,
            'employee_name': employee.employee_name,
            'hourly_wage': employee.hourly_wage,
        },
        'projects': project_list
    })


@app.route('/add_project', methods=['POST'])
def add_project():
    data = request.json
    project = Project(
        client_id=data['client_id'],
        project_name=data['project_name'],
        budget=data['budget'],
        time_spent=0.0
    )
    db.session.add(project)
    db.session.commit()
    return jsonify({'message': 'Project added successfully!'})

@app.route('/add_task', methods=['POST'])
def add_task():
    data = request.json
    print(data)  # Debugging line
    task = Task(
        project_id=data['project_id'],
        task_name=data['task_name'],
        difficulty_level=data['difficulty_level'],
        employee_id=data['employee_id'],
        time_spent=data['time_spent'],
        status=data['status']
    )
    db.session.add(task)
    db.session.commit()
    return jsonify({'message': 'Task added successfully!'})

@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.get_json()
    task = Task.query.get_or_404(task_id)
    task.task_name = data['task_name']
    task.time_spent = data['time_spent']
    task.status = data['status']
    db.session.commit()
    return jsonify({'message': 'Task updated successfully'})

@app.route('/employees/<int:employee_id>', methods=['PUT'])
def update_employee(employee_id):
    data = request.get_json()
    employee = Employee.query.get_or_404(employee_id)
    employee.employee_name = data['employee_name']
    employee.hourly_wage = data['hourly_wage']
    db.session.commit()
    return jsonify({'message': 'Employee updated successfully'})



@app.route('/add_employee', methods=['POST'])
def add_employee():
    data = request.json
    employee = Employee(
        employee_name=data['employee_name'],
        hourly_wage=data['hourly_wage']
    )
    db.session.add(employee)
    db.session.commit()
    return jsonify({'message': 'Employee added successfully!'})

@app.route('/projects/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    project = Project.query.get(project_id)
    if project:
        db.session.delete(project)
        db.session.commit()
        app.logger.info(f'Project with ID {project_id} deleted successfully')
        return jsonify({'message': 'Project deleted successfully'})
    else:
        app.logger.error(f'Project with ID {project_id} not found')
        return jsonify({'error': 'Project not found'}), 404

@app.route('/clients/<int:client_id>', methods=['DELETE'])
def delete_client(client_id):
    client = Client.query.get(client_id)
    if client:
        projects = Project.query.filter_by(client_id=client_id).all()
        for project in projects:
            db.session.delete(project)
        db.session.delete(client)
        db.session.commit()
        app.logger.info(f'Client with ID {client_id} and their projects deleted successfully')
        return jsonify({'message': 'Client and their projects deleted successfully'})
    else:
        app.logger.error(f'Client with ID {client_id} not found')
        return jsonify({'error': 'Client not found'}), 404
    
@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = Task.query.get(task_id)
    if task:
        db.session.delete(task)
        db.session.commit()
        app.logger.info(f'Task with ID {task_id} deleted successfully')
        return jsonify({'message': 'Task deleted successfully'})
    else:
        app.logger.error(f'Task with ID {task_id} not found')
        return jsonify({'error': 'Task not found'}), 404
    
if __name__ == '__main__':
    app.run(debug=True)