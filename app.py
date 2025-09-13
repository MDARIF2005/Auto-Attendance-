
import flask
from flask import Flask, render_template, request, redirect, url_for, flash
from firebase import db, firebase

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flash messages


@app.route('/', methods=['GET'])
def get_data():
    return render_template('index.html')

# Route for organization registration page
@app.route('/ograisationreg', methods=['GET'])
def organisation_registration_page():
    return render_template('ograisationreg.html')




# Admin registration route (with organization)
@app.route('/register_admin', methods=['POST'])
def register_admin():
    org_name = request.form.get('organization')
    org_code = request.form.get('org_code')
    org_area = request.form.get('org_area')
    org_areapin = request.form.get('org_areapin')
    org_country = request.form.get('org_country')
    org_contact = request.form.get('org_contact')
    admin_contact = request.form.get('admin_contact')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    if password != confirm_password:
        flash('Passwords do not match!')
        return redirect(url_for('get_data'))
    try:
        user = firebase.auth().create_user_with_email_and_password(email, password)
        # Save organization info
        org_data = {
            'name': org_name,
            'code': org_code,
            'area': org_area,
            'areapin': org_areapin,
            'country': org_country,
            'contact': org_contact,
            'admin_email': email
        }
        db.child('organizations').push(org_data)
        # Save admin info
        admin_data = {
            'username': email.split('@')[0],
            'email': email,
            'role': 'admin',
            'admin_contact': admin_contact,
            'organization': org_name
        }
        db.child('users').push(admin_data)
        flash('Organization and admin registered successfully!')
        # Redirect to /org_name/admin
        return redirect(url_for('org_role_page', org_name=org_name, role='admin'))
    except Exception as e:
        flash('Admin registration failed: ' + str(e))
        return redirect(url_for('get_data'))

# Login route for admin/faculty/student
@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    try:
        user = firebase.auth().sign_in_with_email_and_password(email, password)
        # Fetch user info from Realtime Database
        users = db.child('users').order_by_child('email').equal_to(email).get()
        user_data = None
        for u in users.each():
            user_data = u.val()
            break
        if not user_data:
            flash('User record not found in database!')
            return redirect(url_for('get_data'))
        role = user_data.get('role', 'Unknown')
        org_name = user_data.get('organization', 'Unknown')
        flash(f'Login successful! Role: {role}, Organization: {org_name}')
        return redirect(url_for('get_data'))
    except Exception as e:
        flash('Login failed: ' + str(e))
        return redirect(url_for('get_data'))


# Route to show organization details by type and name
@app.route('/<org_short>', methods=['GET'])
def show_organization(org_type, org_name):
    # Find organization by type and name
    orgs = db.child('organizations').order_by_child('type').equal_to(org_type).get()
    org_data = None
    for org in orgs.each():
        if org.val().get('name') == org_name:
            org_data = org.val()
            break
    if org_data:
        return render_template('student_base.html', organization=org_data)
    else:
        return f"No organization found for {org_type} named {org_name}", 404



# Admin dashboard route
@app.route('/<org_short>/admin', methods=['GET'])
def admin_dashboard(org_name):
    # Get organization info
    orgs = db.child('organizations').order_by_child('name').equal_to(org_name).get()
    organization = None
    for org in orgs.each():
        organization = org.val()
        break
    # Get filters from query params
    academic_year = flask.request.args.get('academic_year', '')
    branch = flask.request.args.get('branch', '')
    section = flask.request.args.get('section', '')
    department = flask.request.args.get('department', '')
    # Get students
    students = []
    users = db.child('users').order_by_child('organization').equal_to(org_name).get()
    for u in users.each():
        user = u.val()
        if user.get('role') == 'student':
            if (not academic_year or user.get('academic_year', '') == academic_year) and \
               (not branch or user.get('branch', '') == branch) and \
               (not section or user.get('section', '') == section):
                students.append(user)
    # Get faculty
    faculty_list = []
    for u in users.each():
        user = u.val()
        if user.get('role') == 'faculty':
            if not department or user.get('department', '') == department:
                faculty_list.append(user)
    # Get attendance
    attendance = []
    att_records = db.child('attendance').order_by_child('organization').equal_to(org_name).get()
    for att in att_records.each() if att_records.each() else []:
        record = att.val()
        if (not academic_year or record.get('academic_year', '') == academic_year) and \
           (not branch or record.get('branch', '') == branch) and \
           (not section or record.get('section', '') == section):
            attendance.append(record)
    # Get timetable
    timetable = []
    tt_records = db.child('timetable').order_by_child('organization').equal_to(org_name).get()
    for tt in tt_records.each() if tt_records.each() else []:
        record = tt.val()
        if (not academic_year or record.get('academic_year', '') == academic_year) and \
           (not branch or record.get('branch', '') == branch) and \
           (not section or record.get('section', '') == section):
            timetable.append(record)
    return flask.render_template('admin.html', organization=organization, students=students, faculty_list=faculty_list, attendance=attendance, timetable=timetable)

if __name__ == '__main__':
    app.run(debug=True)
