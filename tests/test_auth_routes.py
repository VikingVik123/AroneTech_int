import pytest
from app import create_app
from app.databases.db import db
from app.models.users import User
from flask_login import current_user

@pytest.fixture
def app():
    """Create a test app with an in-memory SQLite database."""
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SECRET_KEY': 'test-secret-key',
        'WTF_CSRF_ENABLED': False,
    })

    with app.app_context():
        db.create_all()

    yield app

    with app.app_context():
        db.drop_all()

@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()

def test_index_route(client):
    """Test the index route returns JSON and CORS headers."""
    response = client.get('/')
    assert response.status_code == 200
    assert response.json == {"message": "Welcome to the Basic Flask App!"}
    assert 'Access-Control-Allow-Origin' in response.headers
    assert response.headers['Access-Control-Allow-Origin'] == '*'

def test_register_and_login_flow(client):
    """Test registration and login flow with form validation."""
    # Test GET /register
    response = client.get('/register')
    assert response.status_code == 200
    assert b'Register' in response.data

    # Test POST /register with valid data
    response = client.post('/register', data={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'test123'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Registration successful! Please log in.' in response.data
    assert b'Login' in response.data

    # Verify user in database
    with client.application.app_context():
        user = User.query.filter_by(email='test@example.com').first()
        assert user is not None
        assert user.username == 'testuser'
        assert user.check_password('test123')

    # Test POST /register with missing fields
    response = client.post('/register', data={
        'username': '',  # Will trigger "All fields are required."
        'email': 'test2@example.com',
        'password': 'test123'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'All fields are required.' in response.data

    # Test GET /login
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Login' in response.data

    # Test POST /login with valid credentials
    response = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'test123'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Login successful!' in response.data
    assert b'Welcome, testuser!' in response.data

    # Test POST /login with invalid credentials
    response = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'wrongpass'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Invalid email or password.' in response.data

def test_dashboard_requires_login(client):
    response = client.get('/dashboard')
    assert response.status_code == 302
    assert '/login' in response.location

def test_dashboard_access(client):
    """Test dashboard access for authenticated and unauthenticated users."""
    # Create a user
    with client.application.app_context():
        user = User(username='testuser2', email='test2@example.com')
        user.set_password('test123')
        db.session.add(user)
        db.session.commit()
        user_id = user.id

    # Test POST /login
    response = client.post('/login', data={
        'email': 'test2@example.com',
        'password': 'test123'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Welcome, testuser2!' in response.data

    # Verify authenticated state
    with client:
        with client.session_transaction() as sess:
            print("Session after login:", dict(sess))  # Debug
        response = client.get('/dashboard')
        assert response.status_code == 200
        assert b'Welcome, testuser2!' in response.data
        assert 'Access-Control-Allow-Origin' in response.headers
        assert current_user.is_authenticated

    # Clear entire session to simulate logout properly (without logout route)
    with client.session_transaction() as sess:
        print("Session before clearing session:", dict(sess))  # Debug
        sess.clear()
        print("Session after clearing session:", dict(sess))  # Debug

    # Verify unauthenticated state: access to dashboard should redirect to login
    with client.session_transaction() as sess:
        sess.clear()  # Clear session to simulate logout
        response = client.get('/dashboard')
        print("current_user.is_authenticated after clearing session (in request):", current_user.is_authenticated)
        assert response.status_code == 302
        assert '/login' in response.location
        assert not current_user.is_authenticated