# Recipe Web App

A Flask-based web application that allows users to list available ingredients and find possible recipes.

## Features
- Add ingredients via a modal form
- View all stored ingredients on a separate page
- Remove ingredients using a dropdown selection modal
- PostgreSQL as the database (setup separately)
- Bootstrap for styling
- Configuration managed via `config.py`
- `.gitignore` included to prevent unnecessary files from being tracked

---

## 📌 Prerequisites

Ensure you have the following installed:
- Python 3.x
- PostgreSQL (Database setup in a separate repository)
- Virtual environment (`venv`)
- Docker (if using PostgreSQL in a container)
- Git (for version control)

---

## ⚙️ Setup Instructions

1. **Clone the Repository**
   ```sh
   git clone https://github.com/yourusername/your-flask-repo.git
   cd your-flask-repo

2. **Create a Virtual Environment**
    ```sh
    python -m venv .venv
    source .venv/bin/activate  # macOS/Linux
    # or
    .venv\Scripts\activate     # Windows

3. **Install Dependencies**
   ```sh
   pip install -r requirements.txt

4. **Configure the Database**
   ```sh
    The database setup is in a separate repository. Follow its README for setting up PostgreSQL.    
    Create a .env file (if needed) or update config.py with your database credentials:
    
    DATABASE_URL=postgresql://username:password@localhost:5432/yourdbname
