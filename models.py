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