import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# ==========================================
# CONFIGURACIÓN DE TESTS
# ==========================================

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
test_engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)

# ==========================================
# TESTS
# ==========================================

def test_register_user():
    """Test: Registrar un nuevo usuario"""
    response = client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "password123",
            "nombre": "Test User"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "password" not in data
    assert "password_hash" not in data


def test_register_duplicate_email():
    """Test: Intentar registrar email duplicado debe fallar"""
    client.post(
        "/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "password123",
            "nombre": "User 1"
        }
    )
    
    response = client.post(
        "/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "password456",
            "nombre": "User 2"
        }
    )
    
    assert response.status_code == 400
    assert "ya está registrado" in response.json()["detail"].lower()


def test_login_success():
    """Test: Login con credenciales correctas"""
    client.post(
        "/auth/register",
        json={
            "email": "login@example.com",
            "password": "password123",
            "nombre": "Login User"
        }
    )
    
    response = client.post(
        "/auth/login",
        json={
            "email": "login@example.com",
            "password": "password123"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "login@example.com"


def test_login_wrong_password():
    """Test: Login con password incorrecta debe fallar"""
    client.post(
        "/auth/register",
        json={
            "email": "user@example.com",
            "password": "correctpassword",
            "nombre": "User"
        }
    )
    
    response = client.post(
        "/auth/login",
        json={
            "email": "user@example.com",
            "password": "wrongpassword"
        }
    )
    
    assert response.status_code == 401
    assert "incorrectos" in response.json()["detail"].lower()


def test_get_me_with_token():
    """Test: Acceder a /auth/me con token válido"""
    client.post(
        "/auth/register",
        json={
            "email": "me@example.com",
            "password": "password123",
            "nombre": "Me User"
        }
    )
    
    login_response = client.post(
        "/auth/login",
        json={
            "email": "me@example.com",
            "password": "password123"
        }
    )
    
    token = login_response.json()["access_token"]
    
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "me@example.com"


def test_get_me_without_token():
    """Test: Acceder a /auth/me sin token debe fallar"""
    response = client.get("/auth/me")
    assert response.status_code == 401