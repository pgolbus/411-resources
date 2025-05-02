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
    print("Delete user failed with:", delete_user_response.status_code, delete_user_response.text)
    assert delete_user_response.status_code == 200
    assert delete_user_response.json()["status"] == "success"
    print("Delete users successful")

    delete_player_response = requests.delete(f"{base_url}/delete-players")
    assert delete_player_response.status_code == 200
    assert delete_player_response.json()["status"] == "success"
    print("Delete players successful")
    
    session = requests.Session()

    create_user_response = session.post(f"{base_url}/create-account", json={
    "username": username,
    "password": password
    })
    assert create_user_response.status_code in [200, 201]
    assert "User created successfully" in create_user_response.json().get("message", "")
    print("User creation successful")


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
    assert "Logged out successfully" in logout_resp.json().get("message", "")
    print("Logout successful")


    add_player_logged_out_resp = session.post(f"{base_url}/add-player", json=test_player_1)
    # This should fail because we are logged out
    assert add_player_logged_out_resp.status_code in [401, 302] 
    try:
        data = add_player_logged_out_resp.json()
        assert data["status"] == "error"
        print("Player creation failed as expected")
    except requests.exceptions.JSONDecodeError:
        print("Player creation failed as expected (non-JSON redirect)")


if __name__ == "__main__":
    run_smoketest()
