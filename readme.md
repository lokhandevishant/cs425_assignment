

# Role-Based Access Control (RBAC) System

This is a lightweight web application demonstrating a Role-Based Access Control (RBAC) system. It authenticates users and dynamically provides access to specific activities based on the role assigned to them in the database.

## Technology Stack

* **Backend:** Python with Flask

* **Database:** PostgreSQL (accessed via `psycopg` v3)

* **Frontend:** Vanilla HTML, CSS, and JavaScript

* **Authentication:** JSON Web Tokens (JWT)

## Prerequisites

* Python 3.11 or higher

* PostgreSQL installed and running locally

## Database Setup

1. Open your PostgreSQL command line tool (e.g., `psql`) or a database GUI (like pgAdmin or DBeaver).

2. Create a new database for this project.

3. Run the following SQL script to create the schema and insert the dummy data:

```
CREATE TABLE Role (
    RoleId SERIAL PRIMARY KEY,
    RoleName VARCHAR(50) NOT NULL
);

CREATE TABLE Activity (
    ActivityId SERIAL PRIMARY KEY,
    ActivityName VARCHAR(100) NOT NULL,
    ParentActivityId INT,
    AccessDetail VARCHAR(255)
);

CREATE TABLE Responsibility (
    RoleId INT REFERENCES Role(RoleId),
    ActivityId INT REFERENCES Activity(ActivityId),
    PRIMARY KEY(RoleId, ActivityId)
);

CREATE TABLE Users (
    UserId SERIAL PRIMARY KEY,
    UserName VARCHAR(100) NOT NULL,
    LoginId VARCHAR(50) UNIQUE NOT NULL,
    Pwd VARCHAR(255) NOT NULL,
    RoleId INT REFERENCES Role(RoleId)
);

-- Insert Roles
INSERT INTO Role (RoleName) VALUES ('Admin'), ('Employee');

-- Insert Activities
INSERT INTO Activity (ActivityName, AccessDetail) VALUES 
('Manage Users', 'Can add/remove users'), 
('View Reports', 'Can view monthly reports'), 
('Submit Timesheet', 'Can log hours');

-- Map Roles to Activities (Admin gets all, Employee gets limited)
INSERT INTO Responsibility (RoleId, ActivityId) VALUES 
(1, 1), (1, 2), (1, 3), 
(2, 2), (2, 3);

-- Insert Test Users
INSERT INTO Users (UserName, LoginId, Pwd, RoleId) VALUES 
('Alice Admin', 'alice_admin', 'password123', 1),
('Bob Employee', 'bob_emp', 'password123', 2);

```

4. Update the `DB_URL` variable in `app.py` to match your local PostgreSQL credentials (username, password, and database name).
   *(Example: `postgresql://postgres:yourpassword@localhost:5432/yourdatabase`)*

## Installation & Running the App

1. **Open a terminal** and navigate to the project folder.

2. **Create a virtual environment:**

   ```
   python -m venv venv
   
   ```

3. **Activate the virtual environment:**

   * On Mac/Linux: `source venv/bin/activate`

   * On Windows: `venv\Scripts\activate`

4. **Install dependencies:**

   ```
   pip install -r requirements.txt
   
   ```

5. **Start the Flask server:**

   ```
   python app.py
   
   ```

6. **Access the application:** Open your web browser and go to `http://127.0.0.1:5000/`.

## Sample Credentials for Testing

You can use the following pre-configured accounts to test the RBAC functionality.

**Admin User** (Has access to 3 activities)

* **Login ID:** `alice_admin`

* **Password:** `password123`

**Employee User** (Has access to only 2 activities)

* **Login ID:** `bob_emp`

* **Password:** `password123`

## How It Works

1. When a user logs in, the backend verifies their credentials against the PostgreSQL database.

2. If successful, a JWT (JSON Web Token) is generated, embedding the user's `role_id`, and returned to the frontend.

3. The frontend stores this token and redirects the user to the dashboard.

4. The dashboard makes an authenticated request (passing the JWT) to fetch the user's allowed activities.

5. The backend joins the `Activity` and `Responsibility` tables using the user's `role_id` to ensure they only see what they are authorized to access.
