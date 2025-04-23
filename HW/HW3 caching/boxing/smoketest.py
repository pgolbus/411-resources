import requests
import time

def run_smoketest():
    base_url = "http://localhost:5000/api"
    username = "test"
    password = "test"

    test_muhammad_ali = {
        "name": "Muhammad Ali",
        "weight": 210,
        "height": 191,
        "reach": 78,
        "age": 32
    }

    test_joe_frazier = {
        "name": "Joe Frazier",
        "weight": 205,
        "height": 182,
        "reach": 73,
        "age": 30
    }

    # Ensure server is up
    for _ in range(10):
        try:
            r = requests.get(f"{base_url}/health")
            if r.status_code == 200:
                break
        except Exception:
            time.sleep(0.5)
    else:
        raise RuntimeError("Flask app did not start in time")

    health_response = requests.get(f"{base_url}/health")
    print("Health check:", health_response.status_code)
    assert health_response.status_code == 200
    assert health_response.json()["status"] == "success"
    print("Healthcheck passed")

    for endpoint, label in [("reset-users", "users"), ("reset-boxers", "boxers")]:
        resp = requests.delete(f"{base_url}/{endpoint}")
        assert resp.status_code == 200
        assert resp.json()["status"] == "success"
        print(f"Reset {label} successful")

    resp = requests.put(f"{base_url}/create-user", json={"username": username, "password": password})
    assert resp.status_code == 201
    print("User creation successful")

    session = requests.Session()

    resp = session.post(f"{base_url}/login", json={"username": username, "password": password})
    assert resp.status_code == 200
    print("Login successful")

    resp = session.post(f"{base_url}/add-boxer", json=test_muhammad_ali)
    assert resp.status_code == 201
    print("Boxer creation (Ali) successful")

    resp = session.post(f"{base_url}/change-password", json={"new_password": "new_password"})
    assert resp.status_code == 200
    print("Password change successful")

    resp = session.post(f"{base_url}/login", json={"username": username, "password": "new_password"})
    assert resp.status_code == 200
    print("Login with new password successful")

    resp = session.post(f"{base_url}/add-boxer", json=test_joe_frazier)
    assert resp.status_code == 201
    print("Boxer creation (Frazier) successful")

    resp = session.post(f"{base_url}/logout")
    assert resp.status_code == 200
    print("Logout successful")

    resp = session.post(f"{base_url}/add-boxer", json=test_muhammad_ali)
    assert resp.status_code == 401
    assert resp.json()["status"] == "error"
    print("Boxer creation blocked as expected (logged out)")

if __name__ == "__main__":
    run_smoketest()
