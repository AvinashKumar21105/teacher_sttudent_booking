📚 Student-Teacher Booking & Chat Application
This project is a Flask-based web application integrated with Firebase Realtime Database that enables students to book appointments with teachers and have real-time chat communication.
🚀 Features
👩‍🏫 Teacher Features
- Teacher registration and login
- Manage availability for student appointments
- View and reply to student chat messages
- Track booking history
🎓 Student Features
- Student registration and login
- Search and book appointments with teachers
- Real-time chat with teachers
- View appointment and booking status
💬 Chat System
- Real-time student-teacher chat
- Teachers can send replies directly in the chat
- Timestamped messages for better tracking
🛠 Tech Stack
- Backend: Python Flask
- Frontend: HTML, CSS, JavaScript
- Database: Firebase Realtime Database
- Authentication: Firebase Admin SDK
- Session Management: Flask sessions
📂 Project Structure

📦 student-teacher-booking-app
├── app.py                # Main Flask application
├── templates/            # HTML templates
│   ├── login.html
│   ├── register.html
│   ├── student_dashboard.html
│   ├── teacher_dashboard.html
│   ├── chat.html
│   └── bookings.html
├── static/               # CSS, JS, images
├── serviceAccountKey.json # Firebase credentials
└── README.md

🔧 Setup Instructions
1️⃣ Clone the Repository:
git clone https://github.com/yourusername/student-teacher-booking.git
cd student-teacher-booking

2️⃣ Install Dependencies:
pip install flask firebase-admin

3️⃣ Firebase Setup:
- Create a Firebase project
- Enable Realtime Database
- Download serviceAccountKey.json and place it in the project root
- Update the databaseURL in app.py:
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://<your-database-name>.firebaseio.com/"
})

4️⃣ Run the Application:
python app.py
Visit http://localhost:5000 in your browser.
🗄 Firebase Database Structure

admins/
appointments/
bookings/
chats/
students/
teachers/
users/

✅ Future Enhancements
- Add push notifications for appointment updates
- Implement role-based dashboards with analytics
- Add AI-powered teacher suggestion system
- Real-time WebSocket chat instead of page refresh
🤝 Contributing
Contributions are welcome! Please fork the repository and create a pull request for any feature or bug fix.