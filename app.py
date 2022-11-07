
from crypt import methods

from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
import infermedica_api

from apikey import APP_id, APP_key
from models import db, connect_db, User, Member, Diagnose, Disease
from forms import UserAddForm, UserEditForm, LoginForm, MemberAddForm, EvidenceForm, ChoiceForm, DeleteForm




CURR_USER_KEY = "curr_user"
app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///symptomcheck'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False

connect_db(app)
db.drop_all()
db.create_all()

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = 'it`s secret'
toolbar = DebugToolbarExtension(app)


api = infermedica_api.APIv3Connector(app_id=APP_id, app_key=APP_key)
#results = api.search("headache", age=32)






@app.before_request
def add_user_to_g():
    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
    else:
        g.user = None


def do_login(user):
    session[CURR_USER_KEY] = user.id

def do_logout():
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]



@app.route('/')
def homepage():
    if g.user:
        """Return all the members of a user."""
        members = Member.query.all()
        return render_template('home.html', members = members)
    else:
        return render_template('home-anon.html')




@app.route('/signup', methods=['GET', "POST"])
def signup():

    """Handle user signup.
    Create new user and add to DB. Redirect to home page"""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
    form = UserAddForm()

    if form.validate_on_submit():

        email = form.email.data
        password = form.password.data
        user = User.signup(email, password)
        db.session.add(user)
        db.session.commit()

        do_login(user)
        
        return redirect("/")

    else:
        return render_template('users/signup.html', form=form)





@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.email.data,
                                 form.password.data)

        if user:
            do_login(user)
            return redirect("/")

        flash("Invalid credentials.", 'danger')
    return render_template('users/login.html', form=form)



@app.route('/logout')
def logout():
    """Handle logout of users."""

    do_logout()
    flash("You have successfully logged out.", 'success')
    return redirect("/login")





@app.route("/members/add", methods=["GET", "POST"])
def add_member():
    """Handle add member form"""
    form = MemberAddForm()

    if form.validate_on_submit():
        name = form.name.data
        gender = form.gender.data
        age = form.age.data

        member = Member(
            name = name,
            gender = gender,
            age = age,
            user_id = session[CURR_USER_KEY],
        )

        db.session.add(member)
        db.session.commit()

        return redirect("/")
    else:
        return render_template("new_member.html", form=form)




@app.route("/members/<int:member_id>/initialsymptoms", methods=["GET", "POST"])
def survey_start(member_id):
    
    form = EvidenceForm()
    if form.validate_on_submit():
        symptom = form.symptom.data 
        member = Member.query.get_or_404(member_id)
        sym = api.search(symptom, age = 30, sex=member.gender)
        evidence = [ 
          {"id": sym[0]["id"], "choice_id": "present", "source": "initial"},
        ]
        extras = {"diable_groups": True}

        response = api.diagnosis(evidence=evidence, sex=member.gender, age = member.age, extras = extras)
        if response["should_stop"]:
            diagnose_name = response["conditions"][0]["name"]
            diagnose_probability = response["conditions"][0]["probability"]
            members = Member.query.all()
            disease = Disease(
                name = diagnose_name,
                probability = diagnose_probability,
                members = members
            )

            db.session.add(disease)
            db.session.commit()

            return render_template('results.html', diagnose_name=diagnose_name, diagnose_probability=diagnose_probability )

        else:
            session["evidence"] = evidence
            session["member.id"] = member.id
            return redirect("/survey")
            

    else:    
        return render_template('symptoms.html', form=form, member_id = member_id)



@app.route("/survey", methods=["GET", "POST"])
def survey_show():
    evidence = session["evidence"]
    extras = {"diable_groups": True}
    member_id = session["member.id"]
    member = Member.query.get_or_404(member_id)
    response = api.diagnosis(evidence=evidence, sex=member.gender, age = member.age, extras = extras)

    if response["should_stop"]:
        diagnose_name = response["conditions"][0]["name"]
        diagnose_probability = response["conditions"][0]["probability"]
        members = Member.query.all()
        disease = Disease(
            name = diagnose_name,
            probability = diagnose_probability,
            members = members 
            )

        db.session.add(disease)
        db.session.commit()
        return render_template('results.html', diagnose_name=diagnose_name, diagnose_probability=diagnose_probability )
    else:
        question = response["question"]["text"]
        answer = response["question"]["items"][0]["name"]
        form = ChoiceForm()
        form.choice.choices = [
        (response["question"]["items"][0]["choices"][0]["id"], response["question"]["items"][0]["choices"][0]["label"]),
        (response["question"]["items"][0]["choices"][1]["id"], response["question"]["items"][0]["choices"][1]["label"]),
        (response["question"]["items"][0]["choices"][2]["id"], response["question"]["items"][0]["choices"][2]["label"])
        ]
            
        if form.validate_on_submit():
            choice_id = form.choice.data
            evidence.append({
             "id": response["question"]["items"][0]["id"],
             "choice_id": choice_id
            })
            session["evidence"] = evidence
            return redirect("/survey")
        else:
            return render_template('questions.html', form=form, question=question, answer=answer)




@app.route("/members/<int:member_id>")
def member_details(member_id):
    """Show detail on a member."""
    member = Member.query.get_or_404(member_id)
    diagnoses = Diagnose.query.all()
    diseases = []

    for diagnose in diagnoses:
        if member.id == diagnose.member_id:
            disease = Disease.query.get(diagnose.disease_id)
            diseases.append(disease.name)

    return render_template('member.html', member = member, diseases = diseases)



@app.route("/members/<int:member_id>/edit", methods=["GET", "POST"])
def edit_member(member_id):
    """Edit existing member"""
    member = Member.query.get_or_404(member_id)

    form = MemberAddForm(obj=member)

    if form.validate_on_submit():
        member.name = form.name.data
        member.gender = form.gender.data
        member.age = form.age.data

        db.session.commit()

        return redirect("/")
    return render_template("edit.html", form=form, member=member)



@app.route("/members/<int:member_id>/delete", methods=["POST"])
def delete_member(member_id):
    """Delete member."""

    member = Member.query.get_or_404(member_id)

    db.session.delete(member)
    db.session.commit()
    
    return redirect("/")


    

    






