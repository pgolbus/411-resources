Basketball Management API
1. Project Title
    Basketball Management API

2. Project Description
    The Basketball Management API is a web application designed to manage basketball players and their details, alongside user authentication for creating and managing accounts. The API allows users to:

    Create an account, log in, and log out.

    View and add basketball players with relevant details (e.g., name, position, team, height, weight).

    Modify user information, including password updates.

    Perform CRUD operations (Create, Read, Update, Delete) on basketball player data.

    Play a simulated basketball game between two teams of players and track the results.

    Core Features
    User Account Management: Create, login, and delete user accounts with password hashing and authentication.

    Basketball Player Management: Add new players, retrieve player details, and delete players from the database.

    Game Simulation: Simulate a game between two teams of players, calculating skill levels and randomly determining the winner.

    Health Check: Verify the status of the application using a health check endpoint.

    Secure Routes: Protect certain routes so that only logged-in users can access them.

3. Technologies Used
    Flask (backend framework)

    SQLAlchemy (ORM/database management)

    Flask-Login (session and user auth)

    SQLite (database)

    Python 3.x

4. Installation Instructions
    Clone the Repository
    
    
    git clone https://github.com/yourusername/basketball-management-api.git
    cd basketball-management-api
    Set up the Virtual Environment
    For Linux/macOS:
        
        
        python3 -m venv venv
        source venv/bin/activate
    For Windows:
        
        
        python -m venv venv
        venv\Scripts\activate
        Install Dependencies
        
        
        pip install -r requirements.txt
5. Set up Environment Variables
    Create a .env file in the project root directory:

    ini
    
    FLASK_ENV=development
    SECRET_KEY=your_secret_key_here
    DATABASE_URL=sqlite:///basketballers.db

6. Initialize the Database
    Run the following in Python shell:

    python
    
    from basketballers.app import app, db
    app.app_context().push()
    db.create_all()

7. Usage
    Run the Flask App
    Activate your virtual environment and run:

    
    
    flask run
    This starts the server at http://127.0.0.1:5000.

    Example API Routes
        Route 1: Create Account
            Path: /api/create-account

            Method: POST

            Request:
            
            
            {
            "username": "newuser",
            "password": "password123"
            }
            Response:
            
            
            {
            "message": "User created successfully!"
            }
            cURL:
            
            
            curl -X POST -H "Content-Type: application/json" -d '{"username": "newuser", "password": "password123"}' http://127.0.0.1:5000/api/create-account
        Route 2: Login
            Path: /api/login

            Method: POST

            Request:
            
            
            {
            "username": "newuser",
            "password": "password123"
            }
            Response:
            
            
            {
            "message": "Login successful!"
            }
            cURL:
            
            
            curl -X POST -H "Content-Type: application/json" -d '{"username": "newuser", "password": "password123"}' http://127.0.0.1:5000/api/login
        Route 3: Logout
            Path: /api/logout

            Method: POST

            Response:
            
            
            {
            "message": "Logged out successfully!"
            }
            cURL:
            
            
            curl -X POST -H "Authorization: Bearer <TOKEN>" http://127.0.0.1:5000/api/logout
        Route 4: Add Player
            Path: /api/add-player

            Method: POST

            Request:
            
            
            {
            "full_name": "LeBron James",
            "position": "F",
            "team": "Los Angeles Lakers",
            "height_feet": 6,
            "height_inches": 9,
            "weight_pounds": 250
            }
            Response:
            
            
            {
            "status": "success",
            "message": "Player 'LeBron James' added successfully"
            }
            cURL:
            
            
            curl -X POST -H "Content-Type: application/json" -d '{"full_name": "LeBron James", "position": "F", "team": "Los Angeles Lakers", "height_feet": 6, "height_inches": 9, "weight_pounds": 250}' http://127.0.0.1:5000/api/add-player 

API Routes
    1. Create Account
        Path: /api/create-account

        Method: POST

        Purpose: Creates a new user account with a unique username and password.

    Request Body (JSON):
    
    
        {
        "username": "newuser",
        "password": "password123"
        }

    Success Response:
    
    
        {
        "message": "User created successfully!"
        }
        Error Response (Username exists):
    
    
        {
        "message": "Username already exists!"
        }
    Example cURL:
    
    
        curl -X POST -H "Content-Type: application/json" -d '{"username": "newuser", "password": "password123"}' http://127.0.0.1:5000/api/create-account
    2. Login
        Path: /api/login

        Method: POST

        Purpose: Logs in a user with valid credentials.

    Request Body (JSON):
    
    
        {
        "username": "newuser",
        "password": "password123"
        }
    Success Response:
    
    
        {
        "message": "Login successful!"
        }
    Error Response (Invalid credentials):
    
        {
        "message": "Invalid credentials!"
        }
    Example cURL:
    
    
        curl -X POST -H "Content-Type: application/json" -d '{"username": "newuser", "password": "password123"}' http://127.0.0.1:5000/api/login

    3. Logout
        Path: /api/logout

        Method: POST

        Purpose: Logs out the currently logged-in user and clears their session.

    Response:
    
        {
        "message": "Logged out successfully!"
        }
    Example cURL:
        
        
        curl -X POST http://127.0.0.1:5000/api/logout

    4. Protected Route
        Path: /api/protected

        Method: GET

        Purpose: Returns a welcome message if the user is logged in.

    Response:
    
    
        {
        "message": "Hello, newuser! Welcome to the protected route."
        }
    Example cURL:
    
    
        curl -X GET http://127.0.0.1:5000/api/protected

    5. Health Check
        Path: /api/health

        Method: GET

        Purpose: Confirms that the service is running.

    Response:
    
    
    {
    "status": "success",
    "message": "Service is running"
    }

    Example cURL:
    
        curl -X GET http://127.0.0.1:5000/api/health

    6. Delete Users
        Path: /api/delete-users

        Method: DELETE

        Purpose: Deletes all users (for resetting user data).

    Success Response:
    
    
    {
    "status": "success",
    "message": "Users table recreated successfully"
    }
    Error Response:
    
    
    {
    "status": "error",
    "message": "An internal error occurred while deleting users",
    "details": "Detailed error message"
    }
    Example cURL:
    
    
    curl -X DELETE http://127.0.0.1:5000/api/delete-users
    7. Add Player
        Path: /api/add-player

        Method: POST

        Purpose: Adds a basketball player to the database.

    Request Body:
    
    
        {
        "full_name": "LeBron James",
        "position": "F",
        "team": "Los Angeles Lakers",
        "height_feet": 6,
        "height_inches": 9,
        "weight_pounds": 250
        }
        Success Response:
        
        
        {
        "status": "success",
        "message": "Player 'LeBron James' added successfully"
        }
        Error Response:
        
        
        {
        "status": "error",
        "message": "Invalid input types"
        }
    Example cURL:
    
    
    curl -X POST -H "Content-Type: application/json" -d '{"full_name": "LeBron James", "position": "F", "team": "Los Angeles Lakers", "height_feet": 6, "height_inches": 9, "weight_pounds": 250}' http://127.0.0.1:5000/api/add-player

    8. Delete Player
        Path: /api/delete-player/<int:player_id>

        Method: DELETE

        Purpose: Deletes a player by ID.

    Success Response:
    
    
        {
        "status": "success",
        "message": "Player with ID 1 deleted successfully"
        }
        Error Response:
        
        
        {
        "status": "error",
        "message": "Player with ID 1 not found"
        }
        Example cURL:
        
        
        curl -X DELETE http://127.0.0.1:5000/api/delete-player/1
    9. Get Player by Name
        Path: /api/get-player-by-name/<string:player_name>

        Method: GET

        Purpose: Retrieves a player by full name.

        Success Response:
        
        
        {
        "status": "success",
        "player": {
            "id": 1,
            "full_name": "LeBron James",
            "position": "F",
            "team": "Los Angeles Lakers",
            "height_feet": 6,
            "height_inches": 9,
            "weight_pounds": 250
        }
        }
        Error Response:
        
        
        {
        "status": "error",
        "message": "Player 'LeBron James' not found"
        }
        Example cURL:
        
        
        curl -X GET http://127.0.0.1:5000/api/get-player-by-name/LeBron%20James

 6. Testing

This project includes unit tests to ensure the functionality of different features and API routes. The tests are written using `pytest` and can be easily run from the terminal.

### Running Tests

Install the dependencies if you haven't already:

```bash
pip install -r requirements.txt
```

To run all tests, use the `pytest` command:

```bash
pytest --maxfail=1 --disable-warnings -q
```

- `--maxfail=1`: Stops after the first failure.
- `--disable-warnings`: Disables warnings during the test run.
- `-q`: Run in quiet mode for reduced output.

---

### Test Coverage

The following key components are tested:

#### User Creation & Authentication

- Creating a new user.
- Verifying password correctness.
- Logging in and logging out.
- Handling invalid credentials.
- Updating user passwords.

#### Basketball Player Management

- Adding new players to the database.
- Retrieving player details by name or ID.
- Deleting players.
- Validating player data before insertion.

#### Game Model

- Simulating a game between two teams.
- Adding players to teams.
- Calculating team skill scores.
- Caching player performance data.
- Refreshing cache as needed.

---

### Example Test Files

- `test_user_model.py`:  
  Tests for user creation, login/logout, and password updates.

- `test_basketball_player_model.py`:  
  Tests for CRUD operations on basketball players.

- `test_basketball_general_model.py`:  
  Tests for game logic, skill computation, and team simulation.

- `test_api_utils.py`:  
  Tests for utility functions and mock API calls (e.g., random number generation).

---

7. Summary
The Basketball Flask application is a comprehensive web service designed to manage basketball players and user accounts. It allows users to create accounts, log in, log out, and manage their profiles. The application also supports a range of actions related to basketball players, such as adding, deleting, and retrieving player details.

At its core, the application is built using Flask, a lightweight Python web framework, and utilizes SQLAlchemy for database management, ensuring robust data handling. Flask-Login is integrated for managing user sessions, allowing secure authentication and authorization. The data storage is handled through an SQLite database, which is persistent and structured for storing user and basketball player information.

The API provides several routes that support different operations, including user management (creating accounts, logging in/out) and player management (adding and retrieving basketball players). The application also features a game simulation, where users can organize two-player teams, calculate their skill levels, and simulate a game to determine a winner.

Additionally, the application has built-in health check and error handling mechanisms, ensuring smooth operation even during unexpected scenarios. It also includes logging for tracking activity and troubleshooting issues.

8. Conclusion
The Basketball Flask application offers a functional platform for managing basketball players and users, with API routes for interaction. It is designed to be easily extendable, with various improvements that can be added, such as a scoring system, player statistics, and more detailed game mechanics.

With its test-driven development approach, the application ensures reliability and scalability. The use of pytest allows for continuous testing, making it easier to spot errors and fix them promptly. By leveraging Flask’s simplicity and SQLAlchemy’s robust database features, the application is both efficient and maintainable.

This application serves as an excellent foundation for building more complex sports management systems, with clear API routes for integration with other services, real-time features, or more detailed player analytics. It also demonstrates the application of modern web frameworks and practices like Flask-Login, SQLAlchemy, and pytest for full-stack web development.

