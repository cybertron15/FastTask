from flask import Flask, render_template, redirect, request, session, url_for, jsonify
from models import db, Tasks, Projects, Project_tasks, Users, InvitedProjects
import datetime
from uuid import uuid4
import json

app = Flask(__name__)
# create the extension
db = db
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///storage.db"
app.secret_key = "test_key"
db.init_app(app)

whitelist = ["/static/", "/public/", "/login/"]

@app.route("/")
def home():
    tasks = Tasks.query.filter_by(usr_id=session["user_id"]).all()
    for task in tasks:
        if 0 <= (task.due_date - datetime.datetime.now()).days < 1:
            task.color = "text-light"
        elif (task.due_date - datetime.datetime.now()).days < 0:
            task.color = "text-danger"

        task.date_created = task.date_created.isoformat().split("T")[0]
        task.due_date = task.due_date.isoformat().split("T")[0]
    return render_template("index.html", tasks=tasks)

@app.before_request
def login_check():
    logged_in = session.get("logged_in")
    path = request.path
    whitelisted_paths = ["/login","/signup","/static"]
    if not logged_in:
        for wlp in whitelisted_paths:
            if path.startswith(wlp):
                return
        return redirect(url_for("login", signed_up=0))

@app.route("/contact")
def contact():
    return "palashdhavle15@gmail.com"

@app.route("/projects")
def show_projects():
    user_projects = Projects.query.filter_by(usr_id=session["user_id"]).all()
    invited_projects = InvitedProjects.query.filter_by(usr_id=session["user_id"],request_accepted=True).all()
    invited_project_ids = [invited_project.project_id for invited_project in invited_projects]
    invited_project_list = Projects.query.filter(Projects.id.in_(invited_project_ids)).all()

    for pro in user_projects:
        if 0 <= (pro.due_date - datetime.datetime.now()).days < 1:
            pro.color = "theme-warning"
        elif (pro.due_date - datetime.datetime.now()).days < 0:
            pro.color = "theme-danger"
        pro.due_date = datetime.datetime.strftime(pro.due_date, "%Y-%m-%d %H:%M:%S").split(" ")[0]

        # shortening the description if its too long
        if len(pro.desc) > 100:
            pro.full_desc = pro.desc
            pro.desc = pro.desc[:100] + "..."

    for pro in invited_project_list:
        if 0 <= (pro.due_date - datetime.datetime.now()).days < 1:
            pro.color = "theme-warning"
        elif (pro.due_date - datetime.datetime.now()).days < 0:
            pro.color = "theme-danger"
        pro.due_date = datetime.datetime.strftime(pro.due_date, "%Y-%m-%d %H:%M:%S").split(" ")[0]

        # shortening the description if its too long
        if len(pro.desc) > 100:
            pro.full_desc = pro.desc
            pro.desc = pro.desc[:100] + "..."
    
    return render_template("project.html", projects=user_projects,invited_projects=invited_project_list)

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
            task=request.form["task"],
            due_date=due_date,
            desc=request.form["decs"],
            usr_id=session["user_id"],
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
            id=id,
            project=request.form["project"],
            due_date=due_date,
            desc=request.form["desc"],
            usr_id=session["user_id"],
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
    project = Projects.query.filter_by(id=id, usr_id=session["user_id"]).first()
    # added for security reason if someone tries to check out other peoples project
    if not project:
        invited_project = InvitedProjects.query.filter_by(project_id=id,usr_id=session["user_id"])
        project = Projects.query.filter_by(id=id).first()
        if not invited_project:
            return "You are not allowed to view this project"
    owner = Users.query.filter_by(id=project.usr_id).first()
    user_name = session["user_name"].title()
    name = project.project
    status = project.status
    due_date = project.due_date.isoformat().split("T")[0]
    id = project.id
    hts_task = Project_tasks.query.filter_by(project_id=id, task_status=0)
    woi_task = Project_tasks.query.filter_by(project_id=id, task_status=1)
    c_task = Project_tasks.query.filter_by(project_id=id, task_status=2)
    return render_template(
        "viewProject.html",
        projectName=name,
        due_date=due_date,
        proj_id=id,
        hts_task=hts_task,
        woi_task=woi_task,
        c_task=c_task,
        owner_name=owner.usr_name,
        status=status,
    )

@app.route("/add_Project_Task", methods=["GET", "POST"])
def add_project_task():
    if request.method == "POST":
        data = json.loads(request.data)
        id = data["task_id"]
        task_name = data["task_name"]
        task_status = data["task_status"]
        project_id = data["project_id"]
        new_task = Project_tasks(
            id=id, project_id=project_id, task_name=task_name, task_status=task_status
        )
        db.session.add(new_task)
        db.session.commit()
        return "ok", 200

@app.route("/remove_Project_Task", methods=["GET", "POST"])
def remove_project_task():
    if request.method == "POST":
        data = json.loads(request.data)
        id = data["id"]
        task = Project_tasks.query.filter_by(id=id).first()
        db.session.delete(task)
        db.session.commit()
        return "ok", 200

@app.route("/update_Project_Task", methods=["GET", "POST"])
def update_project_task():
    if request.method == "POST":
        data = json.loads(request.data)
        id = data["id"]
        task = Project_tasks.query.filter_by(id=id).first()
        task.task_status = data["status"]
        db.session.add(task)
        db.session.commit()
        return "ok", 200

@app.route("/login/<int:signed_up>", methods=["GET", "POST"])
def login(signed_up):
    usr_msg = ""
    if request.method == "POST":
        data = request.form
        user = Users.query.filter_by(
            usr_email=data["email"], usr_pass=data["password"]
        ).first()
        if user:
            session["user_id"] = user.id
            session["logged_in"] = True
            session["user_name"] = user.usr_name
            return redirect("/")
        else:
            usr_msg = "Login failed!"
    return render_template("login.html", usr_msg=usr_msg, just_signed_up=signed_up)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        id = str(uuid4())
        data = request.form
        usr_name = data["name"]
        email = data["email"]
        password = data["password"]
        new_usr = Users(id=id, usr_name=usr_name, usr_pass=password, usr_email=email)
        db.session.add(new_usr)
        db.session.commit()
        return redirect("/login/1")
    return redirect("/login/0")

@app.route("/logout", methods=["GET", "POST"])
def log_out():
    session.clear()
    return redirect(url_for("login", signed_up=0))

@app.route("/update-status", methods=["GET", "POST"])
def update_status():
    if request.method == "POST":
        data = json.loads(request.data)
        id = data["id"]
        project = Projects.query.filter_by(id=id).first()
        project.status = data["status"]
        db.session.add(project)
        db.session.commit()
        return "ok", 200

@app.route("/get_user_suggestions", methods=["POST"])
def get_suggestions():
    if request.method == 'POST':
        data = json.loads(request.data)
        partial_email = data["partial_email"]
        project_id = data["project_id"]
        projects = InvitedProjects.query.filter_by(project_id=project_id).all()
        existing_users = [project.usr_id for project in projects if project.request_accepted] #list of users who are already present in the project
        suggestions = Users.query.filter(Users.usr_email.ilike(f"%{partial_email}%")).limit(
            5
        )
        pending_users = [project.usr_id for project in projects if not project.request_accepted]
        print(pending_users)
        suggestions_list = []
        for user in suggestions:
            if user.id != session["user_id"] and user.id not in existing_users:
                is_invited = False
                if user.id in pending_users:
                    is_invited = True
                suggestions_list.append([user.id, user.usr_email, is_invited])
        return jsonify({"suggestions": suggestions_list})

@app.route("/invite_user", methods=["POST"])
def invite_user():
     if request.method == 'POST':
        data = json.loads(request.data)
        user_id = data["user_id"]
        project_id = data["project_id"]
        owner_id = session["user_id"]
        new_invite = InvitedProjects(usr_id=user_id,project_owner_id=owner_id,project_id=project_id)
        db.session.add(new_invite)
        db.session.commit()
        return jsonify('ok')
     
@app.route("/get_invites", methods=["POST"])
def get_user_invites():
     if request.method == 'POST':
        user_id = session["user_id"]
        invites = InvitedProjects.query.filter_by(usr_id=user_id,request_accepted=False).all()
        invite_list = []
        for invite in invites:
            project = Projects.query.filter_by(id=invite.project_id).first().project
            owner = Users.query.filter_by(id=invite.project_owner_id).first().usr_name
            invite_list.append({"project":project,"owner":owner,'id':invite.id})
        return jsonify({"invites": invite_list})

@app.route("/update_invites",methods=["POST"])
def update_user_invites():
    if request.method == "POST":
        data = json.loads(request.data)
        user = session['user_id']
        kick_user = request.args.get('kick_user')
        if kick_user == 'true':
            # making sure that the user owns the project before kicking anyone
            invite = InvitedProjects.query.filter_by(id=data['id'],project_owner_id=user).first()
        else:
            # making sure that the user is invited to the project
            invite = InvitedProjects.query.filter_by(id=data['id'],usr_id=user).first()
        if invite:
            if not (kick_user == 'true') and data['action'] == "accept":
                invite.request_accepted = True
                db.session.add(invite)
            if data['action'] == "reject":
                db.session.delete(invite)
            db.session.commit()
            return jsonify('ok')
        else:
            return jsonify('request rejected')

@app.route("/get_users_for_project",methods=["POST"])
def users_for_project():
    if request.method == "POST":
        data = json.loads(request.data)
        invites = InvitedProjects.query.filter_by(project_id=data['project_id'],request_accepted=True).all()
        invited_users_list = []
        if invites:
            for invite in invites:
                invited_user = Users.query.filter_by(id=invite.usr_id).first()
                invited_users_list.append([invite.id,invited_user.usr_name])
            print(invited_users_list)
            return jsonify({"users":invited_users_list})
        else:
            return jsonify({"users":invited_users_list})

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True,port=5001)
