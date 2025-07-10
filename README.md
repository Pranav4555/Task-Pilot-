TaskPilot – Role-Based Task Management API
A production-ready backend system built with FastAPI and PostgreSQL that supports secure task management, user collaboration with access roles, and productivity analytics.

Live API Docs: https://task-pilot-i2ej.onrender.com/docs

Tech Stack
Backend: FastAPI

Database: PostgreSQL, SQLAlchemy ORM

Authentication: JWT-based OAuth2

Authorization: Role-Based Access Control (RBAC)

Tools: Uvicorn, Docker, Pydantic, pgAdmin, Postman

Key Features
Authentication & Authorization
Secure user registration and login

JWT-based token authentication for protected routes

Role-based access control:

Owner – Full control

Editor – Can update but not delete

Viewer – Read-only

Task Operations
Create, read, update, delete tasks

Share tasks with other users by assigning roles

All task endpoints enforce permission checks

Collaboration API
POST /tasks/{id}/share – Share a task and assign a role

POST /tasks/{id}/unshare – Revoke access from a user

GET /shared-tasks – View all tasks shared with the current user

Analytics
Personal productivity insights

GET /analytics/me/overview – Overview of total/completed/pending tasks

GET /analytics/tasks/{id} – Task-specific activity logs

Setup Instructions
Clone the Repository

git clone https://github.com/Pranav4555/taskpilot-backend.git
cd taskpilot-backend
Install Dependencies

pip install -r requirements.txt
Configure Environment
Create a .env file in the root directory:

DATABASE_URL=postgresql://username:password@localhost/taskpilot
SECRET_KEY=your-secret-key
Run the Application

uvicorn main:app --reload
API Documentation
Visit http://localhost:8000/docs for Swagger UI

Role Matrix
Role	  Read	Update	Delete
Owner   Yes	  Yes	    Yes
Editor  Yes	  Yes   	No
Viewer	Yes	  No	    No

Docker Support
You can containerize the project as follows:

docker build -t taskpilot-app .
docker run -d -p 8000:8000 --env-file .env taskpilot-app
Author
Pranav Baitule
Location: Maharashtra, India
GitHub: github.com/Pranav4555
Email: pranavbaitule27@gmail.com
