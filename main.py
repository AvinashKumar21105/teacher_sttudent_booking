from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import pyrebase
import json
import datetime

app = Flask(__name__)
app.secret_key = "your_secret_key"

# ---------------- Firebase Configuration ---------------- #
firebaseConfig = {
    "apiKey": "AIzaSyCI1d6GKJRgrdZdtldchGpZu-raGZs1nPo",
    "authDomain": "ev-recharge-station-eba17.firebaseapp.com",
    "databaseURL": "https://ev-recharge-station-eba17-default-rtdb.asia-southeast1.firebasedatabase.app",
    "projectId": "ev-recharge-station-eba17",
    "storageBucket": "ev-recharge-station-eba17.appspot.com",
    "messagingSenderId": "778963998102",
    "appId": "1:778963998102:web:aaa79b3509a1705e6e39b7",
    "measurementId": "G-MKD2KWQ2TB"
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
db = firebase.database()

# ---------------- Home ---------------- #
@app.route('/')
def index():
    return render_template("index.html")

# ---------------- Admin Register ---------------- #
@app.route('/register/admin', methods=['GET', 'POST'])
def admin_register():
    if request.method == 'POST':
        name = request.form['name']
        empid = request.form['empid']
        password = request.form['password']
        try:
            admins = db.child("admins").get().val()
            if admins:
                for key, admin in admins.items():
                    if admin.get("empid") == empid:
                        flash("Employee ID already exists!", "danger")
                        return redirect(url_for('admin_register'))

            db.child("admins").push({
                "name": name,
                "empid": empid,
                "password": password
            })
            flash("Admin registered successfully!", "success")
            return redirect(url_for('admin_login'))
        except Exception as e:
            print(f"Error during admin registration: {e}")
            try:
                error_json = json.loads(e.args[1])
                error_message = error_json['error']['message']
            except:
                error_message = str(e)
            flash(f"Registration failed: {error_message}", "danger")
            return redirect(url_for('admin_register'))
    return render_template("admin_registration.html")

# ---------------- Admin Login ---------------- #
@app.route('/login/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        empid = request.form['empid']
        password = request.form['password']
        admins = db.child("admins").get().val()
        if admins:
            for key, admin in admins.items():
                if admin.get("empid") == empid and admin.get("password") == password:
                    session['admin'] = empid
                    flash("Admin login successful", "success")
                    return redirect(url_for('admin_home'))
        flash("Invalid credentials", "danger")
        return redirect(url_for('admin_login'))
    return render_template("admin_login.html")

# ---------------- Admin Home ---------------- #
@app.route('/admin/home', methods=['GET', 'POST'])
def admin_home():
    if 'admin' not in session:
        flash("Login required", "warning")
        return redirect(url_for('admin_login'))

    empid = session['admin']
    search_query = request.args.get("search", "").lower()

    if request.method == 'POST':
        name = request.form['name']
        teacher_empid = request.form['empid']
        department = request.form['department']
        subject = request.form['subject']
        password = request.form['password']

        db.child("teachers").push({
            "name": name,
            "empid": teacher_empid,
            "department": department,
            "subject": subject,
            "password": password,
            "admin_empid": empid
        })
        flash("Teacher added", "success")
        return redirect(url_for('admin_home'))

    teachers_data = db.child("teachers").get().val() or {}
    teacher_list = []
    for key, val in teachers_data.items():
        if val.get("admin_empid") == empid:
            val['id'] = key
            teacher_list.append(val)

    if search_query:
        teacher_list = [t for t in teacher_list if search_query in t['name'].lower()]

    return render_template("admin_home.html", teachers=teacher_list, search_query=search_query)

# ---------------- Update Teacher ---------------- #
@app.route('/admin/update/<id>', methods=['GET', 'POST'])
def update_teacher(id):
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    teacher = db.child("teachers").child(id).get().val()
    if not teacher:
        flash("Teacher not found", "danger")
        return redirect(url_for('admin_home'))

    if request.method == 'POST':
        name = request.form['name']
        empid = request.form['empid']
        department = request.form['department']
        subject = request.form['subject']
        password = request.form['password']

        db.child("teachers").child(id).update({
            "name": name,
            "empid": empid,
            "department": department,
            "subject": subject,
            "password": password
        })
        flash("Teacher updated", "success")
        return redirect(url_for('admin_home'))

    return render_template("update_teacher.html", teacher=teacher, id=id)

# ---------------- Delete Teacher ---------------- #
@app.route('/admin/delete/<id>', methods=['POST'])
def delete_teacher(id):
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    db.child("teachers").child(id).remove()
    flash("Teacher deleted", "info")
    return redirect(url_for('admin_home'))

# ---------------- Student Register ---------------- #
@app.route('/register/student', methods=['GET', 'POST'])
def student_register():
    if request.method == 'POST':
        name = request.form['name']
        roll_number = request.form['roll_number']
        email = request.form['email']
        password = request.form['password']
        try:
            db.child("students").push({
                "name": name,
                "roll_number": roll_number,
                "email": email,
                "password": password
            })
            flash("Student registered successfully!", "success")
            return redirect(url_for('student_login'))
        except Exception as e:
            print(f"Error during student registration: {e}")
            flash("Something went wrong during registration", "danger")
            return redirect(url_for('student_register'))
    return render_template("student_register.html")

# ---------------- Student Login ---------------- #
@app.route('/login/student', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        roll = request.form['roll']
        password = request.form['password']
        try:
            students = db.child("students").get()
            if students.each():
                for student in students.each():
                    student_data = student.val()
                    if student_data.get("roll_number") == roll and student_data.get("password") == password:
                        session['student_roll'] = roll
                        session['student_id'] = student.key()  # Ensure this is set
                        flash("Student login successful!", "success")
                        return redirect(url_for('student_home'))
            flash("Invalid credentials. Try again.", "danger")
        except Exception as e:
            print(f"Error during student login: {e}")
            flash("Login failed. Please try again.", "danger")
    return render_template("student_login.html")


# ---------------- Student Home ---------------- #
@app.route('/student/home', methods=['GET'])
def student_home():
    if 'student_roll' not in session:
        flash("Please login to access your dashboard.", "warning")
        return redirect(url_for('student_login'))

    student_id = session['student_id']  # Get the student ID from the session
    search_query = request.args.get("search", "").lower()
    teachers = []

    try:
        teacher_data = db.child("teachers").get()
        if teacher_data.each():
            for t in teacher_data.each():
                t_data = t.val()
                if search_query in t_data.get("name", "").lower():
                    teachers.append(t_data)
    except Exception as e:
        print("Error loading teachers:", e)

    student_appointments = []
    try:
        all_appointments = db.child("appointments").get()
        if all_appointments.each():
            for a in all_appointments.each():
                a_data = a.val()
                if a_data.get("student_id") == student_id:  # Ensure we are filtering by the correct student ID
                    teacher_id = a_data.get("teacher_id", "")
                    teacher_info = db.child("teachers").order_by_child("empid").equal_to(teacher_id).get().val()
                    teacher_name = "Unknown"
                    if teacher_info:
                        for t in teacher_info.values():
                            teacher_name = t.get("name", "Unknown")
                            break
                    a_data['teacher_name'] = teacher_name
                    student_appointments.append(a_data)
    except Exception as e:
        print("Error loading appointments:", e)

    return render_template("student_home.html",
                           teachers=teachers,
                           appointments=student_appointments,
                           search_query=search_query)

# ---------------- Teacher Login ---------------- #
@app.route('/login/teacher', methods=['GET', 'POST'])
def teacher_login():
    if request.method == 'POST':
        empid = request.form['empid']
        password = request.form['password']
        try:
            teachers = db.child("teachers").get().val()
            if teachers:
                for key, teacher in teachers.items():
                    if teacher.get("empid") == empid and teacher.get("password") == password:
                        session['teacher'] = empid
                        session['teacher_name'] = teacher.get("name")
                        flash("Teacher login successful", "success")
                        return redirect(url_for('teacher_home'))
            flash("Invalid employee ID or password", "danger")
        except Exception as e:
            print(f"Error during teacher login: {e}")
            flash("Something went wrong", "danger")
    return render_template("teacher_login.html")

# ---------------- Teacher Home ---------------- #
# ---------------- Teacher Home ---------------- #
# ---------------- Teacher Home ---------------- #
@app.route('/teacher/home')
def teacher_home():
    if 'teacher' not in session:
        flash("Please login first.", "warning")
        return redirect(url_for('teacher_login'))

    teacher_id = session.get('teacher')  # empid
    teacher_name = session.get('teacher_name', 'Teacher')

    appointments = []
    messages = []

    try:
        # Fetch appointments for this teacher
        all_appointments = db.child("appointments").get()
        if all_appointments.each():
            for a in all_appointments.each():
                a_data = a.val()
                a_data['key'] = a.key()
                if a_data.get('teacher_id') == teacher_id:
                    appointments.append(a_data)

        # Fetch messages for this teacher
        all_chats = db.child("chats").get()
        if all_chats.each():
            for chat in all_chats.each():
                chat_id = chat.key()
                if chat_id.endswith(f"_{teacher_id}"):
                    for msg_key, msg in chat.val().items():
                        messages.append({
                            "message_id": msg_key,
                            "student_name": msg.get("sender", "Unknown"),
                            "content": msg.get("message", ""),
                            "timestamp": msg.get("timestamp", "")
                        })

        # Sort messages by timestamp
        messages.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

    except Exception as e:
        print("Error fetching data:", e)

    return render_template("teacher_home.html",
                           teacher_name=teacher_name,
                           appointments=appointments,
                           messages=messages)

# ---------------- Schedule Appointment ---------------- #
@app.route('/teacher/schedule', methods=['GET', 'POST'])
def schedule_appointment():
    if 'teacher' not in session:
        flash("Please login first", "danger")
        return redirect(url_for('teacher_login'))

    students = db.child("students").get().val()
    student_list = []
    if students:
        for key, val in students.items():
            student_list.append({"id": key, **val})

    if request.method == 'POST':
        student_id = request.form['student']
        date = request.form['date']
        time = request.form['time']
        purpose = request.form['purpose']
        message = request.form['message']

        teacher_id = session.get('teacher')
        teacher_name = session.get('teacher_name', 'Unknown')

        appointment_data = {
            'teacher_id': teacher_id,
            'teacher_name': teacher_name,
            'student_id': student_id,
            'date': date,
            'time': time,
            'purpose': purpose,
            'message': message,
            'status': 'pending'
        }

        db.child("appointments").push(appointment_data)
        flash("Appointment request sent to student!", "success")

        # Redirect to the student appointment page
        return redirect(url_for('student_home'))  # Ensure this route exists

    return render_template('schedule_appointment.html', students=student_list)

# ---------------- Accept/Reject Appointment ---------------- #
@app.route('/teacher/appointment/<key>/accept', methods=['POST'])
def accept_appointment(key):
    try:
        print(f"Accepting appointment with key: {key}")  # Debugging line
        db.child("appointments").child(key).update({"status": "accepted"})
        flash("Appointment accepted!", "success")
    except Exception as e:
        flash("Failed to accept appointment", "danger")
        print(f"Error: {e}")  # More detailed error logging
    return redirect(url_for('teacher_home'))

@app.route('/teacher/appointment/<key>/reject', methods=['POST'])
def reject_appointment(key):
    try:
        print(f"Rejecting appointment with key: {key}")  # Debugging line
        db.child("appointments").child(key).update({"status": "rejected"})
        flash("Appointment rejected!", "warning")
    except Exception as e:
        flash("Failed to reject appointment", "danger")
        print(f"Error: {e}")  # More detailed error logging
    return redirect(url_for('teacher_home'))

# ---------------- Chat Functionality ---------------- #

# ---------------- Open Chat ---------------- #
@app.route('/chat/<teacher_empid>', methods=['GET'])
def open_chat(teacher_empid):
    """Student opens chat with a teacher."""
    if 'student_roll' not in session:
        flash("Please login as a student.", "warning")
        return redirect(url_for('student_login'))

    teacher = db.child("teachers").order_by_child("empid").equal_to(teacher_empid).get().val()
    if teacher:
        teacher = list(teacher.values())[0]
    else:
        flash("Teacher not found.", "danger")
        return redirect(url_for('student_home'))

    return jsonify({"teacher_name": teacher["name"], "empid": teacher_empid})

# ---------------- Fetch Messages ---------------- #
@app.route('/chat/messages/<teacher_empid>', methods=['GET'])
def fetch_messages(teacher_empid):
    """Fetch chat messages for student-teacher."""
    if 'student_roll' not in session:
        return jsonify([])

    student_id = session['student_id']
    chat_id = f"{student_id}_{teacher_empid}"

    messages = db.child("chats").child(chat_id).get().val()
    chat_list = []
    if messages:
        for key, msg in messages.items():
            chat_list.append(msg)

    chat_list.sort(key=lambda x: x.get("timestamp", 0))
    return jsonify(chat_list)

# ---------------- Send Message ---------------- #
@app.route('/chat/send/<teacher_empid>', methods=['POST'])
def send_message(teacher_empid):
    """Send message from student to teacher."""
    if 'student_roll' not in session:
        return jsonify({"status": "error", "message": "Login required"}), 403

    student_id = session['student_id']
    student_name = session['student_roll']
    message = request.form.get('message')

    if not message.strip():
        return jsonify({"status": "error", "message": "Empty message"}), 400

    chat_id = f"{student_id}_{teacher_empid}"
    timestamp = datetime.datetime.now().isoformat()

    db.child("chats").child(chat_id).push({
        "sender": student_name,
        "message": message,
        "timestamp": timestamp
    })

    # Redirect to the chat page after sending the message
    return redirect(url_for('student_open_chat', teacher_empid=teacher_empid))


@app.route('/teacher/messages/reply/<message_id>', methods=['POST'])
def teacher_reply(message_id):
    print(f"Received reply for message_id: {message_id}")  # Debugging line
    try:
        reply_text = request.form.get('reply_text')
        teacher_name = "Teacher Name"  # Fetch the actual teacher's name from the session if needed

        # Path where messages are stored
        message_ref = db.child('chats').child(message_id)  # Assuming message_id is the chat ID

        # Get the original message to know which student sent it
        message_data = message_ref.get().val()
        print(f"Message data: {message_data}")  # Debugging line
        if not message_data:
            flash("Message not found.", "danger")
            return redirect(url_for('teacher_home'))

        student_id = message_data.get('student_id')

        # Store the reply under the same message ID
        reply_ref = message_ref.child('replies').push()  # Create a 'replies' node under the original message
        reply_ref.set({
            'teacher_name': teacher_name,
            'student_id': student_id,
            'reply_text': reply_text,
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        print("Reply saved successfully.")  # Debugging line

        flash("Reply sent successfully!", "success")
    except Exception as e:
        flash(f"Error sending reply: {str(e)}", "danger")
        print(f"Error details: {str(e)}")  # Log the error for debugging

    return redirect(url_for('teacher_home'))


@app.route('/student/message/<teacher_empid>', methods=['GET'])
def student_open_chat(teacher_empid):
    student_id = session.get('student_id')
    student_name = session.get('student_roll')

    if not student_id or not student_name:
        flash("Please log in again to chat.", "danger")
        return redirect(url_for('student_login'))

    chat_id = f"{student_id}_{teacher_empid}"
    messages_ref = db.child('chats').child(chat_id)
    chat_messages = messages_ref.get().val() or {}

    chat_messages_list = []
    for msg_id, msg in chat_messages.items():
        replies = msg.get('replies', {})
        chat_messages_list.append({
            'id': msg_id,
            'content': msg.get('message', ''),
            'timestamp': msg.get('timestamp', ''),
            'from_teacher': msg.get('sender') != student_name,
            'replies': [reply for reply in replies.values()]  # Collect replies
        })

    return render_template('chat.html',
                           teacher_empid=teacher_empid,
                           teacher_name="Teacher",  # Fetch the actual teacher's name if needed
                           student_name=student_name,
                           chat_messages=chat_messages_list)

# ---------------- Book Appointment ---------------- #
@app.route('/student/book/<teacher_empid>', methods=['GET'])
def book_appointment(teacher_empid):
    # Fetch teacher details using the empid
    teacher = db.child("teachers").order_by_child("empid").equal_to(teacher_empid).get().val()
    if teacher:
        teacher = list(teacher.values())[0]
    else:
        flash("Teacher not found.", "danger")
        return redirect(url_for('student_home'))

    return render_template("student_appointment.html", teacher=teacher)
@app.route('/student/submit_appointment', methods=['POST'])
def submit_appointment():
    if 'student_id' not in session:
        flash("Please login to book an appointment.", "danger")
        return redirect(url_for('student_login'))

    student_id = session['student_id']
    teacher_id = request.form['teacher_id']
    date = request.form['date']
    time = request.form['time']
    purpose = request.form['purpose']
    message = request.form['message']

    appointment_data = {
        'student_id': student_id,
        'teacher_id': teacher_id,
        'date': date,
        'time': time,
        'purpose': purpose,
        'message': message,
        'status': 'pending'
    }

    db.child("appointments").push(appointment_data)
    flash("Appointment request submitted successfully!", "success")
    return redirect(url_for('student_home'))

# ---------------- Logout ---------------- #
@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out", "info")
    return redirect(url_for('index'))

# ---------------- Run App ---------------- #
if __name__ == '__main__':
    app.run(debug=True)
