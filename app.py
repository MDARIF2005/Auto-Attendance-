import flask
from flask import Flask, render_template, request, redirect, url_for, flash, session
from functools import wraps
from firebase import auth, db  # your firebase_admin config
import firebase_admin

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # ⚠️ Change in production

# --------------------- LOGIN REQUIRED DECORATOR ---------------------
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

# --------------------- LOGIN ---------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')  # 'admin', 'faculty', 'student'

        try:
            # Fetch all users
            users_ref = db.reference('users')
            all_users = users_ref.get() or {}
            user = None

            for uid, u in all_users.items():
                if u.get('email') == email and u.get('role') == role:
                    user = u
                    break

            if not user:
                flash(f'⚠️ {role.capitalize()} user not found!')
                return redirect(url_for('login'))

            if user.get('password') and user.get('password') != password:
                flash('⚠️ Incorrect password!')
                return redirect(url_for('login'))

            session['user_email'] = email
            session['role'] = role
            session['org_short'] = user.get('org_short', '').strip()

            flash(f'✅ Logged in successfully as {role.capitalize()}!')

            # Lookup organization by org_short
            orgs_ref = db.reference('organizations')
            all_orgs = orgs_ref.get() or {}
            organization = None
            for key, org in all_orgs.items():
                if org.get('short', '').strip() == session['org_short']:
                    organization = org
                    break

            if not organization:
                flash(f'❌ Organization "{session["org_short"]}" Not Found!')
                return redirect(url_for('index'))

            if organization.get('status', 'inactive') != 'active':
                flash(f'❌ Organization "{session["org_short"]}" is not active!')
                return redirect(url_for('index'))

            # Redirect based on role
            if role == 'admin':
                return redirect(url_for('admin_dashboard', org_short=session['org_short']))
            elif role == 'faculty':
                return redirect(url_for('view_faculty', org_short=session['org_short']))
            else:  # student
                return render_template('organisation.html', organization=organization)

        except Exception as e:
            flash(f'⚠️ Login failed: {e}')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout', methods=['POST'])
@login_required
def logout():
    session.pop('user_email', None)
    session.pop('role', None)
    session.pop('org_short', None)
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
        auth.create_user(email=email, password=password)

        # Use org_short as key to simplify lookup
        org_ref = db.reference(f'organizations/{org_short}')
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
        org_ref.set(org_data)  # use set() instead of push()

        # Save admin info
        users_ref = db.reference('users')
        admin_data = {
            'username': email.split('@')[0],
            'email': email,
            'password': password,
            'role': 'admin',
            'admin_contact': admin_contact,
            'organization': org_name,
            'org_short': org_short
        }
        users_ref.push(admin_data)

        flash('✅ Organization and admin registered successfully!')
        return redirect(url_for('login'))

    except Exception as e:
        flash(f'⚠️ Admin registration failed: {e}')
        return redirect(url_for('organization_registration_page'))

# --------------------- ORGANIZATION PAGE ---------------------
 
@app.route('/<org_short>/', methods=['GET'], strict_slashes=False)
def show_organization(org_short):
    org_short = org_short.strip()  # preserve case

    orgs_ref = db.reference('organizations')
    try:
        all_orgs = orgs_ref.get() or {}
        print("🔥 All organizations:", all_orgs)
    except firebase_admin.exceptions.NotFoundError:
        all_orgs = {}
        print("❌ 'organizations' node not found")

    org_data = None
    for key, org in all_orgs.items():
        short_name = org.get('short', '').strip()
        if short_name == org_short:
            org_data = org
            break

    if not org_data:
        return render_template("not_found.html", org_short=org_short), 404

    if org_data.get('status', 'inactive').strip() != 'active':
        return render_template("organizationreg.html", organization=org_data), 403

    return render_template('organisation.html', organization=org_data)

# --------------------- ADMIN DASHBOARD ---------------------
@app.route('/<org_short>/admin')
@login_required
def admin_dashboard(org_short):
    org_short = org_short.strip()  # normalize input
    orgs_ref = db.reference('organizations')
    all_orgs = orgs_ref.get() or {}

    organization = None
    for key, org in all_orgs.items():
        if org.get('short', '').strip() == org_short:
            organization = org
            break

    if not organization:
        return render_template("not_found.html", org_short=org_short), 404

    return render_template('admin/home.html', organization=organization, active_tab='home')

# --------------------- ADMIN PAGES ---------------------
@app.route('/<org_short>/students')
@login_required
def view_students(org_short):
    users_ref = db.reference('users')
    all_users = users_ref.get() or {}
    students = [u for u in all_users.values() if u.get('role') == 'student' and u.get('org_short') == org_short]

    org_ref = db.reference(f'organizations/{org_short}')
    organization = org_ref.get()

    return render_template('students.html', organization=organization, students=students, active_tab='students')

@app.route('/<org_short>/faculty')
@login_required
def view_faculty(org_short):
    users_ref = db.reference('users')
    all_users = users_ref.get() or {}
    faculty_list = [u for u in all_users.values() if u.get('role') == 'faculty' and u.get('org_short') == org_short]

    org_ref = db.reference(f'organizations/{org_short}')
    organization = org_ref.get()

    return render_template('faculty.html', organization=organization, faculty_list=faculty_list, active_tab='faculty')

# --------------------- MAIN ---------------------
if __name__ == '__main__':
    app.run(debug=True)
