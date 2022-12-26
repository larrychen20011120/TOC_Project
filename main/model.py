from main import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    line_id = db.Column(db.String(128), unique=True)
    art_count = db.Column(db.Integer)
    name = db.Column(db.String(128))
    block = db.Column(db.Boolean, nullable=False)
    art1 = db.Column(db.String(128), unique=True)
    art2 = db.Column(db.String(128), unique=True)
    art3 = db.Column(db.String(128), unique=True)
    art4 = db.Column(db.String(128), unique=True)
    art5 = db.Column(db.String(128), unique=True)
    use_buffer = db.Column(db.Boolean, nullable=False)
    # "idle", "wait_<style_id>", "draw"
    draw_state = db.Column(db.String(128), nullable=False)
    def __repr__(self):
        return f'<User {self.id}>'

class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    style_id = db.Column(db.Integer, nullable=False)
    content_url = db.Column(db.String(128), nullable=False)
    line_id = db.Column(db.String(128), nullable=False, unique=True)
    art_id = db.Column(db.Integer, nullable=False)
    def __repr__(self):
        return f'<Task {self.id}>'

class Exhibit(db.Model):
    __tablename__ = 'exhibitions'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    detail_url = db.Column(db.String(128), nullable=False)
    start_time = db.Column(db.String(16), nullable=False)
    end_time =  db.Column(db.String(16), nullable=False)
    name = db.Column(db.String(128), nullable=False, unique=True)
    img_url = db.Column(db.String(128), nullable=False)
