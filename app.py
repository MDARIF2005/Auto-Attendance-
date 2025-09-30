import flask
from flask import Flask, render_template, request, redirect, url_for, flash, session
from firebase import db, firebase

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # ⚠️ Change this in production

# --------------------- LOGIN REQUIRED DECORATOR ---------------------
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_email' not in session:
            flash('⚠️ Please login first!')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --------------------- ROUTES ---------------------

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/organizationreg', methods=['GET'])
def organization_registration_page():
    return render_template('organizationreg.html')


# --------------------- LOGIN/LOGOUT ---------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            user = firebase.auth().sign_in_with_email_and_password(email, password)
            session['user_email'] = email
            flash('✅ Logged in successfully!')
            # Redirect based on role
            user_data = db.child('users').order_by_child('email').equal_to(email).get()
            role = None
            org_short = None
            if user_data.each():
                for u in user_data.each():
                    role = u.val().get('role')
                    org_short = u.val().get('org_short')
                    break
            if role == 'admin':
                return redirect(url_for('admin_dashboard', org_short=org_short))
            else:
                flash('⚠️ Only admin access for now.')
                return redirect(url_for('index'))
        except Exception as e:
            flash(f'⚠️ Login failed: {e}')
            return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    session.pop('user_email', None)
    flash('✅ Logged out successfully!')
    return redirect(url_for('index'))

# --------------------- ADMIN REGISTRATION ---------------------
@app.route('/register_admin', methods=['POST'])
def register_admin():
    org_name = request.form.get('organization')
    org_short = request.form.get('org_short').strip()
    org_code = request.form.get('org_code')
    org_area = request.form.get('org_area')
    org_areapin = request.form.get('org_areapin')
    org_country = request.form.get('org_country')
    org_contact = request.form.get('org_contact')
    admin_contact = request.form.get('admin_contact')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    status = request.form.get('status', 'inactive')

    if password != confirm_password:
        flash('❌ Passwords do not match!')
        return redirect(url_for('organization_registration_page'))

    try:
        firebase.auth().create_user_with_email_and_password(email, password)

        # Save organization info
        org_data = {
            'name': org_name,
            'short': org_short,
            'code': org_code,
            'area': org_area,
            'areapin': org_areapin,
            'country': org_country,
            'contact': org_contact,
            'admin_email': email,
            'status': status
        }
        db.child('organizations').push(org_data)

        # Save admin info
        admin_data = {
            'username': email.split('@')[0],
            'email': email,
            'role': 'admin',
            'admin_contact': admin_contact,
            'organization': org_name,
            'org_short': org_short
        }
        db.child('users').push(admin_data)

        flash('✅ Organization and admin registered successfully!')
        return redirect(url_for('login'))

    except Exception as e:
        flash(f'⚠️ Admin registration failed: {e}')
        return redirect(url_for('organization_registration_page'))

# --------------------- ORGANIZATION PAGE ---------------------
# --------------------- ORGANIZATION PAGE ---------------------
@app.route('/<org_short>', methods=['GET'])
@login_required
def show_organization(org_short):
    org_short = org_short.strip()
    orgs = db.child('organizations').order_by_child('short').equal_to(org_short).get()

    org_data = None
    if orgs.each():
        for org in orgs.each():
            org_data = org.val()
            break

    # If organization not found
    if not org_data:
        return render_template("not_found.html", org_short=org_short), 404

    # If organization exists but inactive
    if org_data.get('status') != 'active':
        return render_template("inactive.html", organization=org_data), 403

    # If organization exists and active
    return render_template('organisation.html', organization=org_data)


# --------------------- ADMIN DASHBOARD ---------------------
@app.route('/<org_short>/admin')
@login_required
def admin_dashboard(org_short):
    org_short = org_short.strip()
    orgs = db.child('organizations').order_by_child('short').equal_to(org_short).get()
    organization = None
    if orgs.each():
        for org in orgs.each():
            organization = org.val()
            break
    if not organization:
        return render_template("not_found.html", org_short=org_short), 404

    return render_template('admin/home.html', organization=organization)


# --------------------- ADMIN PAGES ---------------------
@app.route('/<org_short>/students')
@login_required
def view_students(org_short):
    orgs = db.child('organizations').order_by_child('short').equal_to(org_short).get()
    organization = orgs.each()[0].val() if orgs.each() else None
    students = [u.val() for u in db.child('users').order_by_child('org_short').equal_to(org_short).get().each() if u.val().get('role')=='student']
    return render_template('students.html', organization=organization, students=students, active_tab='students')


@app.route('/<org_short>/faculty')
@login_required
def view_faculty(org_short):
    orgs = db.child('organizations').order_by_child('short').equal_to(org_short).get()
    organization = orgs.each()[0].val() if orgs.each() else None
    faculty_list = [u.val() for u in db.child('users').order_by_child('org_short').equal_to(org_short).get().each() if u.val().get('role')=='faculty']
    return render_template('faculty.html', organization=organization, faculty_list=faculty_list, active_tab='faculty')


# --------------------- MAIN ---------------------
if __name__ == '__main__':
    app.run(debug=True)
