GXO Logistics Metrics Tracker 📊
A web application designed to track and manage metrics, records, and team contributions effectively. Built using React, Django REST Framework, and PostgreSQL.

I have invited the collaborator: uyko76@yahoo.com
GitHub Repo (Python – Django backend):  https://github.com/robkinson94/gxologistics
GitHub Repo (React – Typescript frontend): https://github.com/robkinson94/gxologisticsfrontend

Login Instructions:

frontend url: https://gxologisticsfrontend.onrender.com/

backend url: https://gxologistics-metrics-tracker.onrender.com/admin/

Admin user (Can perform CRUD) username: admin@gxo.com password: GXOAdmin2024
Non-Admin user (Can perform READ ONLY) username: non-admin@gxo.com password: GXONonAdmin2024

When registering a new user, please use actual email as email verification is needed to activate account.

In production this will be limited to email address's with domain @gxo.com only.

For security all environment variables are stored securely in render and not in a .env file.

Features
User Authentication: Secure login and registration with token-based authentication.
Dashboard: Visualize key metrics and records with charts (bar, line, pie, area).
Metrics Management: Add, edit, and delete metrics.
Team Management: Manage teams and their details.
Records Management: Add, edit, and track records.
Data Visualization: Beautiful and responsive charts powered by recharts.
Loading Indicators: Seamless user experience with loading spinners for data-heavy components.
Tech Stack
Frontend:

React (TypeScript)
Tailwind CSS
Axios
React Router
Backend:

Django REST Framework (DRF)
PostgreSQL
Django Simple JWT
Deployment:

Render (Backend & Database)
render (Frontend)
Getting Started
Prerequisites
Ensure you have the following installed on your machine:

Node.js (v14+)
Python (v3.9+)
PostgreSQL
Installation
Clone the repository:

bash
Copy code
git clone https://github.com/robkinson94/gxologistics.git
cd gxologistics
Backend Setup:

bash
Copy code
cd gxologistics
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser  # Follow prompts to create an admin user
Frontend Setup:

bash
Copy code
cd frontend
npm install
npm start

Backend: python manage.py runserver
Frontend: npm start
Usage
Login/Register:

Navigate to /login or /register to access the application.
Explore Features:

Dashboard: View charts and key metrics.
Manage Metrics: Add, edit, and delete metrics.
Manage Teams: Organize team data.
Manage Records: Track contributions and values.
API Endpoints
Here is a summary of key API endpoints:

Authentication:

POST /api/token/: Obtain access and refresh tokens.
POST /api/token/refresh/: Refresh access token.
Metrics:

GET /api/metrics/: Fetch all metrics.
POST /api/metrics/: Create a new metric.
PUT /api/metrics/<id>/: Update an existing metric.
DELETE /api/metrics/<id>/: Delete a metric.
Teams:

GET /api/teams/: Fetch all teams.
POST /api/teams/: Add a new team.
Records:

GET /api/records/: Fetch all records.
POST /api/records/: Add a new record.
Refer to the API documentation for full details.
