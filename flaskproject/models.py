from flaskproject import db, login_manager
from datetime import datetime
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __table_name__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.png')
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(60), nullable=False)
    tasks = db.relationship('ToDO', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.username}','{self.first_name}','{self.last_name}')"

class ToDO(db.Model):
    todo_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20), nullable=False)
    content = db.Column(db.String(250), nullable=False)
    # have some form of way to toggle
    completed = db.Column(db.Integer, default=0)
    due_date = db.Column(db.DateTime, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"ToDO('{self.title}', '{self.content}', '{self.due_date }')"