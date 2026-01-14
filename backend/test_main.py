"""Basic tests for the blog post API"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app

client = TestClient(app)


@pytest.fixture
def mock_qdrant():
    with patch('main.qdrant') as mock:
        yield mock


@pytest.fixture
def mock_embedding():
    with patch('main.get_embedding') as mock:
        mock.return_value = [0.1] * 768
        yield mock


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_all_posts(mock_qdrant):
    mock_point = MagicMock()
    mock_point.id = "test-id"
    mock_point.payload = {
        "title": "Test Title",
        "content": "Test Content",
        "topic": "test"
    }
    mock_qdrant.scroll.return_value = ([mock_point], None)

    response = client.get("/api/posts")
    assert response.status_code == 200
    posts = response.json()
    assert len(posts) == 1
    assert posts[0]["title"] == "Test Title"


def test_get_single_post(mock_qdrant):
    mock_point = MagicMock()
    mock_point.id = "test-id"
    mock_point.payload = {
        "title": "Test Title",
        "content": "Test Content",
        "topic": "test"
    }
    mock_qdrant.retrieve.return_value = [mock_point]

    response = client.get("/api/posts/test-id")
    assert response.status_code == 200
    post = response.json()
    assert post["title"] == "Test Title"


def test_get_nonexistent_post(mock_qdrant):
    mock_qdrant.retrieve.return_value = []

    response = client.get("/api/posts/nonexistent-id")
    assert response.status_code == 200
    assert response.json() == {"error": "Post not found"}


def test_create_post(mock_qdrant, mock_embedding):
    response = client.post("/api/posts", json={
        "title": "New Post",
        "content": "New Content",
        "topic": "test"
    })
    assert response.status_code == 200
    assert response.json()["status"] == "created"
    assert "id" in response.json()


def test_update_post(mock_qdrant, mock_embedding):
    response = client.post("/api/posts/update", json={
        "id": "test-id",
        "title": "Updated Post",
        "content": "Updated Content",
        "topic": "test"
    })
    assert response.status_code == 200
    assert response.json()["status"] == "updated"


def test_update_post_without_id():
    response = client.post("/api/posts/update", json={
        "title": "Updated Post",
        "content": "Updated Content",
        "topic": "test"
    })
    assert response.status_code == 200
    assert response.json() == {"error": "Post ID required"}


def test_delete_post(mock_qdrant):
    response = client.get("/api/posts/delete/test-id")
    assert response.status_code == 200
    assert response.json()["status"] == "deleted"


def test_search_posts(mock_qdrant, mock_embedding):
    mock_point = MagicMock()
    mock_point.id = "test-id"
    mock_point.payload = {
        "title": "Test Title",
        "content": "Test Content",
        "topic": "test"
    }
    mock_point.score = 0.95
    mock_response = MagicMock()
    mock_response.points = [mock_point]
    mock_qdrant.query_points.return_value = mock_response

    response = client.get("/api/posts/search/test query")
    assert response.status_code == 200
    posts = response.json()
    assert len(posts) == 1
    assert posts[0]["score"] == 0.95
