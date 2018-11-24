from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy 
from datetime import datetime

DB_USER = "yc3515"
DB_PASSWORD = "73258qvz"

DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"

DATABASEURI = "postgresql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_SERVER+"/w4111"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASEURI
db = SQLAlchemy(app)

class Event(db.Model):
    eid = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(50))
    food_info = db.Column(db.String(50))
    title = db.Column(db.String(50))
    abstract = db.Column(db.Text)
    begin_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    event_hold = db.relationship("Hold", back_populates = "hold_event")

class Area(db.Model):
    aid = db.Column(db.Integer, primary_key = True)
    aname = db.Column(db.String(50))

class Researcher(db.Model):
    rid = db.Column(db.Integer, primary_key = True)
    rname = db.Column(db.String(50))
    gender = db.Column(db.String(50))
    citations = db.Column(db.String(50))
    publications = db.Column(db.String(50))
    researcher_participate = db.relationship("Participate", back_populates = "participate_researcher")

class Institution(db.Model):
    iid = db.Column(db.Integer, primary_key = True)
    iname = db.Column(db.String(50), nullable = False)
    organizations = db.relationship('Organization', backref = 'institution', lazy = True)

class Organization(db.Model):
    oid = db.Column(db.Integer, primary_key = True)
    otitle = db.Column(db.String(50), nullable = False)
    iid = db.Column(db.Integer, db.ForeignKey(Institution.iid), nullable = False)
    organization_hold = db.relationship("Hold", back_populates = "hold_organization")

class Hold(db.Model):
    hid = db.Column(db.Integer, primary_key = True)
    oid = db.Column(db.Integer, db.ForeignKey(Organization.oid), nullable = False)
    eid = db.Column(db.Integer, db.ForeignKey(Event.eid), nullable = False)
    hold_event = db.relationship("Event", back_populates = "event_hold")
    hold_organization = db.relationship("Organization", back_populates = "organization_hold")
    hold_participate = db.relationship("Participate", back_populates = "participate_hold")

class Participate(db.Model):
    hid = db.Column(db.Integer, db.ForeignKey(Hold.hid), primary_key = True)
    rid = db.Column(db.Integer, db.ForeignKey(Researcher.rid), primary_key = True)
    ptype = db.Column(db.String(50), db.CheckConstraint('ptype in ("audience", "host", "speaker")'))
    participate_researcher  = db.relationship("Researcher", back_populates = "researcher_participate")
    participate_hold = db.relationship("Hold", back_populates = "hold_participate")

class Department(db.Model):
    did = db.Column(db.Integer, primary_key = True)
    dname = db.Column(db.String(50), nullable = False)
    iid = db.Column(db.Integer, db.ForeignKey(Institution.iid), nullable = False)

class Focus(db.Model):
    aid = db.Column(db.Integer, db.ForeignKey(Area.aid), primary_key = True)
    rid = db.Column(db.Integer, db.ForeignKey(Researcher.rid), primary_key = True)

class Relates_to(db.Model):
    aid = db.Column(db.Integer, db.ForeignKey(Area.aid), primary_key = True)
    did = db.Column(db.Integer, db.ForeignKey(Department.did), primary_key = True)

class Affiliate_with_organization(db.Model):
    oid = db.Column(db.Integer, db.ForeignKey(Organization.oid), primary_key = True)
    rid = db.Column(db.Integer, db.ForeignKey(Researcher.rid), primary_key = True)

class Affiliate_with_department(db.Model):
    did = db.Column(db.Integer, db.ForeignKey(Department.did), primary_key = True)
    rid = db.Column(db.Integer, db.ForeignKey(Researcher.rid), primary_key = True) 

class Label(db.Model):
    eid = db.Column(db.Integer, db.ForeignKey(Event.eid), primary_key = True)
    aid = db.Column(db.Integer, db.ForeignKey(Area.aid), primary_key = True)

@app.route('/')
def index():
    db.create_all()
    posts = db.session.query(Event.eid, Event.location, Event.food_info, Event.title, Event.abstract, Event.begin_time, Event.end_time, Organization.otitle, Researcher.rname, Department.dname, Department.iid).outerjoin(Hold, Hold.eid == Event.eid).outerjoin(Organization, Organization.oid == Hold.oid).outerjoin(Participate, Participate.hid == Hold.hid).outerjoin(Researcher, Researcher.rid == Participate.rid).outerjoin(Affiliate_with_department, Affiliate_with_department.rid == Researcher.rid).outerjoin(Department, Department.did == Affiliate_with_department.did).order_by(Event.begin_time.desc()).all()
    return render_template('index.html', posts=posts)


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/post/<int:post_eid>')
def post(post_eid):
    post = db.session.query(Event.eid, Event.location, Event.food_info, Event.title, Event.abstract, Event.begin_time, Event.end_time, Organization.otitle, Researcher.rname, Department.dname, Department.iid).outerjoin(Hold, Hold.eid == Event.eid).outerjoin(Organization, Organization.oid == Hold.oid).outerjoin(Participate, Participate.hid == Hold.hid).outerjoin(Researcher, Researcher.rid == Participate.rid).outerjoin(Affiliate_with_department, Affiliate_with_department.rid == Researcher.rid).outerjoin(Department, Department.did == Affiliate_with_department.did).filter(Event.eid == post_eid).one()
    return render_template('post.html', post = post)

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/add')
def add():
    return render_template('add.html')

@app.route('/addpost', methods=['POST'])
def addpost():
    location = request.form['location']
    food_info = request.form['food_info']
    title = request.form['title']
    abstract = request.form['abstract']
    begin_time = request.form['begin_time']
    end_time = request.form['end_time']

    post = Event(location = location, food_info = food_info, title = title, abstract = abstarct, begin_time = begin_time, end_time = end_time)

    db.session.add(post)
    db.session.commit()

    return redirect(url_for('index'))
if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
