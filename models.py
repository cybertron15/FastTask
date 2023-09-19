from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()
current_date = datetime.datetime.now().strftime('%Y-%m-%d')
formated_date = datetime.datetime.strptime(current_date,'%Y-%m-%d')

class Tasks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usr_id = db.Column(db.String(200), nullable=False, default="admin")
    task = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=formated_date)
    due_date = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        """this method is used to represent the class when its printed"""
        return f"{self.id}, {self.task} , {self.desc}, {self.date_created}, {self.due_date}"

class Projects(db.Model):
    id = db.Column(db.String(100),primary_key=True)
    usr_id = db.Column(db.String(100), nullable=False, default="admin")
    project = db.Column(db.String(100), nullable=False)
    desc = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=formated_date)
    due_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(15), nullable=False, default="active")

    def __repr__(self):
        """this method is used to represent the class when its printed"""
        return f"{self.id}, {self.project} , {self.desc}, {self.date_created}, {self.due_date}"

class Project_tasks(db.Model):
    id = db.Column(db.String(100),primary_key=True)
    usr_id = db.Column(db.String(100), nullable=False, default="admin")
    project_id = db.Column(db.String(100),db.ForeignKey('projects.id'),nullable=True)
    task_name = db.Column(db.String(100), nullable=False)
    task_status = db.Column(db.String(15), nullable=False, default="active")
    date_created = db.Column(db.DateTime, nullable=False, default=formated_date)
    due_date = db.Column(db.DateTime)

class Users(db.Model):
    id = db.Column(db.String(100),primary_key=True)
    usr_name = db.Column(db.String(100), nullable=False, default="admin")
    usr_pass = db.Column(db.String(100), nullable=False, default="admin")
    usr_email = db.Column(db.String(100), nullable=False, default="admin@gmail.com")

class InvitedProjects(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usr_id = db.Column(db.String(100),nullable=False)
    project_owner_id = db.Column(db.String(100),nullable=False)
    project_id = db.Column(db.String(100),nullable=False)
    request_accepted = db.Column(db.Boolean,nullable=False,default=False)
    privlage = db.Column(db.String(20),nullable=False ,default='basic')