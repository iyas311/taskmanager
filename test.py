import requests
import json

BASE = "http://127.0.0.1:8000"

# -------------------------------
# Utilities
# -------------------------------
def login(username, password):
    r = requests.post(f"{BASE}/api/login/", json={"username": username, "password": password})
    r.raise_for_status()
    return r.json()


def auth_put(endpoint, token, data):
    r = requests.put(f"{BASE}{endpoint}", json=data, headers={"Authorization": f"Bearer {token}"})
    print(f"\nPUT {endpoint} → Status: {r.status_code}")
    try:
        print("Response JSON:", json.dumps(r.json(), indent=2))
    except:
        print("Response content:", r.text)
    return r


def auth_get(endpoint, token):
    r = requests.get(f"{BASE}{endpoint}", headers={"Authorization": f"Bearer {token}"})
    print(f"\nGET {endpoint} → Status: {r.status_code}")
    try:
        print("Response JSON:", json.dumps(r.json(), indent=2))
    except:
        print("Response content:", r.text)
    return r


# -------------------------------
# Test Flow for Pending Task
# -------------------------------

def test_user_sets_task_pending(task_id):
    print("=== USER SETS TASK TO PENDING ===")
    tokens = login("user7", "Iy@s2458")
    access = tokens["access"]

    # Mark task as pending (no report or worked_hours)
    resp = auth_put(f"/api/tasks/{task_id}/", access, {
        "status": "pending",
        "completion_report": None,
        "worked_hours": None
    })
    return task_id


def test_admin_access_pending(task_id):
    print("\n=== ADMIN TRIES TO ACCESS PENDING TASK REPORT ===")
    tokens = login("admintest", "Iy@s2458")
    access = tokens["access"]

    resp = auth_get(f"/api/tasks/{task_id}/report/", access)


def test_superadmin_access_pending(task_id):
    print("\n=== SUPERADMIN TRIES TO ACCESS PENDING TASK REPORT ===")
    tokens = login("iyas", "123")
    access = tokens["access"]

    resp = auth_get(f"/api/tasks/{task_id}/report/", access)


if __name__ == "__main__":
    TASK_ID = 8  # Pending task
    test_user_sets_task_pending(TASK_ID)
    test_admin_access_pending(TASK_ID)
    test_superadmin_access_pending(TASK_ID)
