from flask import Flask, render_template,redirect,request
from models import db, Tasks
import datetime

app = Flask(__name__)
# create the extension
db = db
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///storage.db"
db.init_app(app)

@app.route('/')
def home():
    tasks = Tasks.query.all()
    for task in tasks:
        print((task.due_date - datetime.datetime.now()).days)
        if 0 <= (task.due_date - datetime.datetime.now()).days < 1:
            task.color = "text-warning"
        elif (task.due_date - datetime.datetime.now()).days < 0:
            task.color = "text-danger"
    return render_template('index.html',tasks=tasks)

@app.route('/contact')
def contact():
    return 'palashdhavle15@gmail.com'

@app.route('/projects')
def about():
    return render_template('project.html')

@app.route('/delete/<int:id>')
def delete(id):
    task = Tasks.query.filter_by(id=id).first()
    db.session.delete(task)
    db.session.commit()
    return redirect("/")

@app.route('/update/<int:id>',methods = ["GET","POST"])
def update(id):
    if request.method == 'POST':
        task = Tasks.query.filter_by(id=id).first()
        task.task = request.form.get('task')
        task.desc = request.form.get('decs')
        db.session.add(task)
        db.session.commit()
        return redirect("/")
    task = Tasks.query.filter_by(id=id).first()
    return render_template('update.html',task=task)

@app.route('/add',methods = ["GET","POST"])
def showhtml():
    if request.method == "POST":
        print(datetime.datetime.now().isoformat().split(' '))
        req_due_date = f"{request.form['dueDate']} {datetime.datetime.now().isoformat().split('T')[1][:-7]}"
        due_date = datetime.datetime.strptime(req_due_date,"%Y-%m-%d %H:%M:%S")
        task = Tasks(task=request.form['task'],due_date=due_date,desc=request.form['decs'])
        print(task)
    db.session.add(task)
    db.session.commit()
    return redirect("/")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True,port=5001)
   
   

