# 📚 PDF Mentor

**Your Personal PDF Learning Platform**

PDF Mentor is a web-based PDF learning and management platform built with Django. It allows administrators to manage users, upload PDF documents, assign documents to approved users, and provide support through an integrated messaging system.

Users can securely access their assigned PDF documents online through their personal dashboard.

🌐 **Live Website:** https://pdf-mentor.onrender.com/

---

## ✨ Features

### 👨‍💼 Admin Panel
- Admin Dashboard with platform statistics.
- User Management.
- Approve or deactivate user accounts.
- Manually set user passwords.
- Upload and manage PDF documents.
- Assign PDFs to individual users.
- Activate, deactivate, edit, and delete documents.
- View user PDF assignment history.

### 👤 User Panel
- User Registration with Full Name and Mobile Number.
- Admin-approved account access.
- Secure Login using Mobile Number and Password.
- Personal Dashboard.
- My PDF Library.
- Online PDF Viewing.
- Support and Help Chat.

### 💬 Support System
- Create support tickets.
- User and Admin messaging.
- Admin reply functionality.
- Close and reopen support tickets.
- Delete complete support conversations.

### 🔐 Security
- Custom Django User Model.
- Password hashing using Django authentication.
- Role-based access control.
- Login-protected pages.
- User-specific PDF access permissions.
- Environment variables for sensitive configuration.
- Private PDF object storage.

---

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend Programming |
| Django | Web Framework |
| PostgreSQL | Database |
| Neon | Cloud PostgreSQL Hosting |
| Tigris | PDF Object Storage |
| HTML5 | Structure |
| CSS3 | Styling |
| JavaScript | Frontend Interactions |
| Bootstrap 5 | Responsive UI |
| Bootstrap Icons | Icons |
| Gunicorn | Production Server |
| WhiteNoise | Static File Serving |
| Render | Deployment |
| Git & GitHub | Version Control |

---

## 🏗️ Project Structure

```text
PDF-Mentor/
│
├── accounts/
│   ├── models.py
│   ├── views.py
│   └── urls.py
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── dashboard/
│   ├── views.py
│   └── urls.py
│
├── documents/
│   ├── models.py
│   ├── views.py
│   └── urls.py
│
├── support/
│   ├── models.py
│   ├── views.py
│   └── urls.py
│
├── static/
│   ├── css/
│   └── pwa/
│
├── templates/
│
├── manage.py
├── requirements.txt
├── .gitignore
└── README.md
```

---

## ⚙️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/RohanJagtap431/PDF-Mentor.git
```

### 2. Open the Project

```bash
cd PDF-Mentor
```

### 3. Create Virtual Environment

```bash
python -m venv venv
```

Activate on Windows:

```powershell
venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a `.env` file in the project root directory.

```env
SECRET_KEY=your-django-secret-key
DEBUG=True

ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=

DATABASE_URL=your-neon-postgresql-connection-string

AWS_ACCESS_KEY_ID=your-tigris-access-key
AWS_SECRET_ACCESS_KEY=your-tigris-secret-key
AWS_ENDPOINT_URL_S3=https://t3.storage.dev
AWS_REGION=auto
TIGRIS_BUCKET_NAME=your-tigris-bucket-name
```

**Important:** Never commit your `.env` file or expose database credentials and storage access keys.

### 6. Apply Database Migrations

```bash
python manage.py migrate
```

### 7. Create Superuser

```bash
python manage.py createsuperuser
```

### 8. Run Development Server

```bash
python manage.py runserver
```

Open in your browser:

```text
http://127.0.0.1:8000/
```

---

## ☁️ Deployment

PDF Mentor is deployed using Render.

- **Backend Hosting:** Render
- **Database:** Neon PostgreSQL
- **PDF Storage:** Tigris Object Storage
- **Source Code:** GitHub

Live Website:

https://pdf-mentor.onrender.com/

---

## 🔒 Privacy & Security

- Database credentials and secret keys are stored in environment variables.
- PDF files are stored in private object storage.
- Access to assigned documents is controlled by the application.
- PDF viewing is provided through time-limited access URLs.

Note: Online viewing does not guarantee complete prevention of copying, screenshots, or downloading.

---

## 🚀 Future Improvements

- Progressive Web App installation support.
- Improved PDF reading experience.
- Enhanced user profile and account settings.
- Additional document management features.
- Improved platform analytics.

---

## 👨‍💻 Developer

**Rohan Jagtap**

Python / Django Backend Developer

- GitHub: https://github.com/RohanJagtap431
- Project Repository: https://github.com/RohanJagtap431/PDF-Mentor
- Live Project: https://pdf-mentor.onrender.com/

---

## 📄 License

This project is currently available as a personal development project. No open-source license has been specified.

---

**PDF Mentor — Learn, Read & Manage PDFs in One Place.**
