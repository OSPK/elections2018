from flask import Flask, render_template, request,\
                redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import simplejson as json
from collections import OrderedDict
from functools import wraps
import pygal
from sqlalchemy.sql import func

app = Flask(__name__)
app.config['SECRET_KEY'] = 'something-secret'
username = 'dp'
pwd = 'pakistan'

app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:x3nonx4@localhost/elections"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Result(db.Model):
    __tablename__="results"
    id = db.Column(db.Integer, primary_key=True)
    constituency = db.Column(db.String(80))
    province = db.Column(db.String(80))
    area = db.Column(db.String(80))
    party = db.Column(db.String(80))
    candidate = db.Column(db.String(80))
    votes = db.Column(db.Integer)
    winner = db.Column(db.String(80))
    color = db.Column(db.String(80))

    def __repr__(self):
        return 'Constituency %r | ' % self.constituency

    def _asdict(self):
        result = OrderedDict()
        for key in self.__mapper__.c.keys():
            result[key] = getattr(self, key)
        return result

constit = ["NA-1","NA-2","NA-3","NA-4","NA-5","NA-6","NA-7","NA-8","NA-9","NA-10","NA-11","NA-12","NA-13","NA-14","NA-15","NA-16","NA-17","NA-18","NA-19","NA-20","NA-21","NA-22","NA-23","NA-24","NA-25","NA-26","NA-27","NA-28","NA-29","NA-30","NA-31","NA-32","NA-33","NA-34","NA-35","NA-36","NA-37","NA-38","NA-39","NA-40","NA-41","NA-42","NA-43","NA-44","NA-45","NA-46","NA-47","NA-48","NA-49","NA-50","NA-51","NA-52","NA-53","NA-54","NA-55","NA-56","NA-57","NA-58","NA-59","NA-60","NA-61","NA-62","NA-63","NA-64","NA-65","NA-66","NA-67","NA-68","NA-69","NA-70","NA-71","NA-72","NA-73","NA-74","NA-75","NA-76","NA-77","NA-78","NA-79","NA-80","NA-81","NA-82","NA-83","NA-84","NA-85","NA-86","NA-87","NA-88","NA-89","NA-90","NA-91","NA-92","NA-93","NA-94","NA-95","NA-96","NA-97","NA-98","NA-99","NA-100","NA-101","NA-102","NA-103","NA-104","NA-105","NA-106","NA-107","NA-108","NA-109","NA-110","NA-111","NA-112","NA-113","NA-114","NA-115","NA-116","NA-117","NA-118","NA-119","NA-120","NA-121","NA-122","NA-123","NA-124","NA-125","NA-126","NA-127","NA-128","NA-129","NA-130","NA-131","NA-132","NA-133","NA-134","NA-135","NA-136","NA-137","NA-138","NA-139","NA-140","NA-141","NA-142","NA-143","NA-144","NA-145","NA-146","NA-147","NA-148","NA-149","NA-150","NA-151","NA-152","NA-153","NA-154","NA-155","NA-156","NA-157","NA-158","NA-159","NA-160","NA-161","NA-162","NA-163","NA-164","NA-165","NA-166","NA-167","NA-168","NA-169","NA-170","NA-171","NA-172","NA-173","NA-174","NA-175","NA-176","NA-177","NA-178","NA-179","NA-180","NA-181","NA-182","NA-183","NA-184","NA-185","NA-186","NA-187","NA-188","NA-189","NA-190","NA-191","NA-192","NA-193","NA-194","NA-195","NA-196","NA-197","NA-198","NA-199","NA-200","NA-201","NA-202","NA-203","NA-204","NA-205","NA-206","NA-207","NA-208","NA-209","NA-210","NA-211","NA-212","NA-213","NA-214","NA-215","NA-216","NA-217","NA-218","NA-219","NA-220","NA-221","NA-222","NA-223","NA-224","NA-225","NA-226","NA-227","NA-228","NA-229","NA-230","NA-231","NA-232","NA-233","NA-234","NA-235","NA-236","NA-237","NA-238","NA-239","NA-240","NA-241","NA-242","NA-243","NA-244","NA-245","NA-246","NA-247","NA-248","NA-249","NA-250","NA-251","NA-252","NA-253","NA-254","NA-255","NA-256","NA-257","NA-258","NA-259","NA-260","NA-261","NA-262","NA-263","NA-264","NA-265","NA-266","NA-267","NA-268","NA-269","NA-270","NA-271","NA-272"]

party_colors = {"PMLN":"#73d216", "PTI":"#ef2929", "PPP":"#5c3566", "MQM":"#000000",\
                "MMA":"#e9b96e", "PKMAP":"#f57900", "ANP":"#edd400", "PSP":"#0aa7f2",\
                "TLP":"#356c2f","BAP":"#8f5902", "IND":"#888a85", "GDA": "#af24b3",\
                "PML-Q":"#6168d6", "BNP":"#83a18f", "QWP":"#cdd004", "PAR":"#f55ba2",\
                "AML":"#40bae8"}

# Functions ============================================================
def get_color(party):
    if not party_colors.get(party):
        return "#666666"
    return party_colors.get(party)

def alchemyencoder(obj):
    """JSON encoder function for SQLAlchemy special classes."""
    if isinstance(obj, datetime.date):
        return obj.isoformat()
    elif isinstance(obj, decimal.Decimal):
        return float(obj)

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login')), 401
        return f(*args, **kwargs)

    return wrap

def total():
    qry = db.session.query(func.max(Result.votes).label("max_score"), 
                    func.sum(Result.votes).label("total_score"),
                    )
    # qry = qry.group_by(Result.constituency)
    for highest, total in qry:
        total = {"highest":highest, "total":total}

    return total

app.jinja_env.globals.update(get_color=get_color, total=total)
# /Functions ============================================================

@app.route('/login/', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        if request.form['password'] == pwd and request.form['username'] == username:
            session['logged_in'] = True
        else:
            flash('wrong password!')
        return redirect(url_for('upload'))
    if request.method == 'GET':
        return render_template('login.html')

@app.route("/logout/")
def logout():
    session['logged_in'] = False
    return redirect(url_for('login'))

@app.route('/upload/')
@app.route('/upload/<const>')
@login_required
def upload(const=False):
    if const:
        results = Result.query.filter_by(constituency=const).order_by(Result.votes.desc()).all()
    else:
        results = False

    return render_template('upload.html', results=results, const=const, constit=constit)


@app.route('/update/<int:id>', methods=['POST'])
@login_required
def update(id):
    data = request.form
    result = Result.query.get(id)
    result.candidate = data['candidate']
    result.votes = data['votes']
    result.party = data['party']
    db.session.commit()
    return redirect(url_for('upload', const=result.constituency))


@app.route('/results/')
def results():
    res = Result.query.all()
    return json.dumps(res)

@app.route('/colors/')
def colors():
    results = []
    for const in constit:
        results.append(Result.query.filter_by(constituency=const).order_by(Result.votes.desc()).first())

    final = []
    for result in results:

        if result.votes is None or result.votes is 0:
            continue

        if result.party not in party_colors:
            color="#666666"
        else:
            color = party_colors[result.party]

        final.append({"constituency":result.constituency, "candidate": result.candidate,\
                    "votes":result.votes, "party": result.party, "color":color,\
                    "area":result.area})

    return json.dumps(final)

@app.route("/circle")
def circle():
    cir = ""
    cx = 0
    cy = 0
    count=0
    for na in constit:
        tmpcir = """<circle
        style="opacity:1;fill:#ff2727;fill-opacity:1;stroke:none;stroke-width:3;stroke-miterlimit:4;stroke-dasharray:none"
        id="{}"
        cx="{}"
        cy="{}"
        r="10" />""".format(na,cx,cy)

        cx += 20
        count += 1
        if count == 13:
            cy += 20
            count = 0

        cir = cir + tmpcir
    return cir

@app.route('/')
@app.route('/map/<const>')
def map(const=None):
    results = {}
    if const is not None:
        results = Result.query.filter_by(constituency=const).order_by(Result.votes.desc()).limit(7).all()
    return render_template('map.html', results=results, const=const, constit=constit)


@app.route('/chart')
@app.route('/chart/<const>')
def chart(const=None):
    results = {}
    if const is not None:
        results = Result.query.filter_by(constituency=const).order_by(Result.votes.desc()).limit(7).all()
    return render_template('chart.html', results=results, const=const, constit=constit)


@app.route('/pp/')
def pp():
    parties = {}

    results = []
    for const in constit:
        results.append(Result.query.filter_by(constituency=const).order_by(Result.votes.desc()).first())

    final = []
    for result in results:

        if result.votes is None or result.votes is 0:
            continue

        if not parties.get(result.party):
            parties[result.party] = 0
        parties[result.party] += 1

    total = sum(parties.values())

    parties = sorted((value, key) for (key,value) in parties.items())

    return render_template('pp.html', parties=parties, total=total)


@app.route('/pie/')
def pie():
    parties = {}

    results = []
    for const in constit:
        results.append(Result.query.filter_by(constituency=const).order_by(Result.votes.desc()).first())

    final = []
    for result in results:

        if result.votes is None or result.votes is 0:
            continue

        if not parties.get(result.party):
            parties[result.party] = 0
        parties[result.party] += 1

    total = sum(parties.values())

    parties = sorted((value, key) for (key,value) in parties.items())
    pyconfig = pygal.Config()
    pyconfig.js = ['https://en.dailypakistan.com.pk/wp-content/themes/century/js/pygal-tooltips.min.js']
    pie_chart = pygal.Pie(pyconfig)
    pie_chart.title = 'Election Results 2018 - NA'

    parties = reversed(parties)
    for pee, v in parties:
        print(v,pee)
        pie_chart.add(v,pee)

    chart = pie_chart.render_data_uri()


    return render_template('pie.html', chart=chart)