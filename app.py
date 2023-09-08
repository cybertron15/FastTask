from flask import Flask, render_template, redirect, request
from models import db, Tasks, Projects,Project_tasks
import datetime
from uuid import uuid4
import json

app = Flask(__name__)
# create the extension
db = db
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///storage.db"
db.init_app(app)


@app.route("/")
def home():
    tasks = Tasks.query.all()
    for task in tasks:
        if 0 <= (task.due_date - datetime.datetime.now()).days < 1:
            task.color = "text-warning"
        elif (task.due_date - datetime.datetime.now()).days < 0:
            task.color = "text-danger"
    return render_template("index.html", tasks=tasks)


@app.route("/contact")
def contact():
    return "palashdhavle15@gmail.com"


@app.route("/projects")
def show_projects():
    projects = Projects.query.all()
    for project in projects:
        if 0 <= (project.due_date - datetime.datetime.now()).days < 1:
            project.color = "bg-warning-subtle"
        elif (project.due_date - datetime.datetime.now()).days < 0:
            project.color = "bg-danger-subtle"
        project.due_date = datetime.datetime.strftime(project.due_date,"%Y-%m-%d %H:%M:%S").split(' ')[0]
    return render_template("project.html", projects=projects)


@app.route("/delete/<int:id>")
def delete(id):
    task = Tasks.query.filter_by(id=id).first()
    db.session.delete(task)
    db.session.commit()
    return redirect("/")


@app.route("/update/<int:id>", methods=["GET", "POST"])
def update(id):
    if request.method == "POST":
        task = Tasks.query.filter_by(id=id).first()
        task.task = request.form.get("task")
        task.desc = request.form.get("decs")
        db.session.add(task)
        db.session.commit()
        return redirect("/")
    task = Tasks.query.filter_by(id=id).first()
    return render_template("update.html", task=task)


@app.route("/add", methods=["GET", "POST"])
def add_task():
    if request.method == "POST":
        req_due_date = f"{request.form['dueDate']} {datetime.datetime.now().isoformat().split('T')[1][:-7]}"
        due_date = datetime.datetime.strptime(req_due_date, "%Y-%m-%d %H:%M:%S")
        task = Tasks(
            task=request.form["task"], due_date=due_date, desc=request.form["decs"]
        )
    db.session.add(task)
    db.session.commit()
    return redirect("/")


@app.route("/add-project", methods=["GET", "POST"])
def add_project():
    if request.method == "POST":
        req_due_date = f"{request.form['dueDate']} {datetime.datetime.now().isoformat().split('T')[1][:-7]}"
        due_date = datetime.datetime.strptime(req_due_date, "%Y-%m-%d %H:%M:%S")
        id = str(uuid4())
        project = Projects(
            id = id,
            project=request.form["project"],
            due_date=due_date,
            desc=request.form["desc"],
            status=request.form["status"],
        )
    db.session.add(project)
    db.session.commit()
    return redirect(f"/viewProject/{id}")

@app.route("/deleteProj/<string:id>")
def delete_proj(id):
    task = Projects.query.filter_by(id=id).first()
    db.session.delete(task)
    db.session.commit()
    return redirect("/projects")

@app.route("/viewProject/<string:id>")
def view_project(id):
    project = Projects.query.filter_by(id=id).first()
    name = project.project
    due_date = project.due_date.isoformat().split('T')[0]
    id = project.id
    hts_task = Project_tasks.query.filter_by(project_id = id, task_status = 0)
    woi_task = Project_tasks.query.filter_by(project_id = id, task_status = 1)
    c_task = Project_tasks.query.filter_by(project_id = id, task_status = 2)
    return render_template('viewProject.html',projectName=name,due_date=due_date,proj_id=id,hts_task=hts_task,woi_task=woi_task,c_task=c_task)

@app.route("/add_Project_Task",methods=["GET", "POST"])
def add_project_task():
    if request.method == "POST":
        data = json.loads(request.data)
        id = data['task_id']
        task_name = data['task_name']
        task_status = data['task_status']
        project_id = data['project_id']
        new_task = Project_tasks(id=id,project_id=project_id,task_name=task_name,task_status=task_status)
        db.session.add(new_task)
        db.session.commit()
        return 'ok',200

@app.route("/remove_Project_Task",methods=["GET", "POST"])
def remove_project_task():
    if request.method == "POST":
        data = json.loads(request.data)
        id = data['id']
        task = Project_tasks.query.filter_by(id=id).first()
        db.session.delete(task)
        db.session.commit()
        return 'ok',200

@app.route("/update_Project_Task",methods=["GET", "POST"])
def update_project_task():
    if request.method == "POST":
        data = json.loads(request.data)
        id = data['id']
        task = Project_tasks.query.filter_by(id=id).first()
        task.task_status = data['status']
        db.session.add(task)
        db.session.commit()
        return 'ok',200
        

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)
