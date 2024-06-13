from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class GuestbookEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nick = db.Column(db.String(80), nullable=False)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
