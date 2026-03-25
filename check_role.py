import requests

BASE_URL = "http://localhost:8001/api"

# 登录
response = requests.post(
    f"{BASE_URL}/auth/login",
    data={"username": "admin", "password": "admin123"}
)
print(f"登录状态: {response.status_code}")
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 获取当前用户信息
response = requests.get(f"{BASE_URL}/users/1", headers=headers)
print(f"用户信息: {response.json()}")
print(f"用户角色: '{response.json()['role']}'")
