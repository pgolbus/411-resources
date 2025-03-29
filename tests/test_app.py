import pytest
from flask import json
from HW.hw2_docker.flask.app import app, boxers

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        # Clear the boxer list before each test
        boxers.clear()
        yield client

def test_root(client):
    res = client.get('/')
    assert res.status_code == 200
    data = res.get_json()
    assert data['response'] == 'Hello, World!'

def test_create_boxer(client):
    res = client.post('/boxer', json={"name": "Ali"})
    assert res.status_code == 201
    data = res.get_json()
    assert "Ali" in data['boxers']

def test_duplicate_boxer(client):
    client.post('/boxer', json={"name": "Ali"})
    res = client.post('/boxer', json={"name": "Ali"})
    assert res.status_code == 400
    assert res.get_json()['error'] == "Boxer already exists"

def test_boxer_limit(client):
    client.post('/boxer', json={"name": "Ali"})
    client.post('/boxer', json={"name": "Tyson"})
    res = client.post('/boxer', json={"name": "Rocky"})
    assert res.status_code == 400
    assert res.get_json()['error'] == "Cannot add more than 2 boxers"

def test_get_boxers(client):
    client.post('/boxer', json={"name": "Ali"})
    res = client.get('/boxers')
    data = res.get_json()
    assert "Ali" in data['boxers']

def test_delete_boxer(client):
    client.post('/boxer', json={"name": "Ali"})
    res = client.delete('/boxer', json={"name": "Ali"})
    assert res.status_code == 200
    assert "Ali" not in res.get_json()['boxers']

def test_delete_missing_boxer(client):
    res = client.delete('/boxer', json={"name": "Nobody"})
    assert res.status_code == 404
    assert "error" in res.get_json()

def test_fight_success(client, mocker):
    client.post('/boxer', json={"name": "Ali"})
    client.post('/boxer', json={"name": "Tyson"})

    mocker.patch('HW.hw2_docker.flask.app.random.choice', return_value="Ali")
    res = client.post('/fight')
    assert res.status_code == 200
    data = res.get_json()
    assert data['winner'] == "Ali"
    assert data['loser'] == "Tyson"

def test_fight_too_few_boxers(client):
    client.post('/boxer', json={"name": "Ali"})
    res = client.post('/fight')
    assert res.status_code == 400
    assert "Need two boxers" in res.get_json()['error']
