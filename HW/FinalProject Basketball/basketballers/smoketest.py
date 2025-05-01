import requests

def run_smoketest():
    base_url = "http://localhost:5001/api"
    username = "test"
    password = "test"

    test_player_1 = {
        "full_name": "LeBron James",
        "position": "F",
        "team": "Los Angeles Lakers",
        "height_feet": 6,
        "height_inches": 9,
        "weight_pounds": 250
    }

    test_player_2 = {
        "full_name": "Stephen Curry",
        "position": "G",
        "team": "Golden State Warriors",
        "height_feet": 6,
        "height_inches": 2,
        "weight_pounds": 185
    }

    health_response = requests.get(f"{base_url}/health")
    assert health_response.status_code == 200
    assert health_response.json()["status"] == "success"

    delete_user_response = requests.delete(f"{base_url}/delete-users")
    assert delete_user_response.status_code == 200
    assert delete_user_response.json()["status"] == "success"
    print("Delete users successful")

    delete_player_response = requests.delete(f"{base_url}/delete-players")
    assert delete_player_response.status_code == 200
    assert delete_player_response.json()["status"] == "success"
    print("Delete players successful")

    create_user_response = requests.put(f"{base_url}/create-user", json={
        "username": username,
        "password": password
    })
    assert create_user_response.status_code == 201
    assert create_user_response.json()["status"] == "success"
    print("User creation successful")

    session = requests.Session()

    # Log in
    login_resp = session.post(f"{base_url}/login", json={
        "username": username,
        "password": password
    })
    assert login_resp.status_code == 200
    assert login_resp.json()["status"] == "success"
    print("Login successful")


     # Add player 1
    add_player_resp = session.post(f"{base_url}/add-player", json=test_player_1)
    assert add_player_resp.status_code == 201
    assert add_player_resp.json()["status"] == "success"
    print("Player 1 creation successful")
    
  
    # Change password
    change_password_resp = session.post(f"{base_url}/change-password", json={
        "new_password": "new_password"
    })
    assert change_password_resp.status_code == 200
    assert change_password_resp.json()["status"] == "success"
    print("Password change successful")

    # Log in with new password
    login_resp = session.post(f"{base_url}/login", json={
        "username": username,
        "password": "new_password"
    })
    assert login_resp.status_code == 200
    assert login_resp.json()["status"] == "success"
    print("Login with new password successful")

   # Add player 2
   
    add_player_resp = session.post(f"{base_url}/add-player", json=test_player_2)
    assert add_player_resp.status_code == 201
    assert add_player_resp.json()["status"] == "success"
    print("Player 2 creation successful")


    # Log out
    logout_resp = session.post(f"{base_url}/logout")
    assert logout_resp.status_code == 200
    assert logout_resp.json()["status"] == "success"
    print("Logout successful")

    add_player_logged_out_resp = session.post(f"{base_url}/add-player", json=test_player_1)
    # This should fail because we are logged out
    assert add_player_logged_out_resp.status_code == 401
    assert add_player_logged_out_resp.json()["status"] == "error"
    print("Player creation failed as expected")

if __name__ == "__main__":
    run_smoketest()
