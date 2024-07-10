import requests
from func.error.error import raise_custom_error

# GitHub 사용자 정보를 가져오는 함수
def fetch_github_data(token: str, owner: str, name: str, data_type: str):
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    api_base_url = "https://api.github.com/repos"
    url = f"{api_base_url}/{owner}/{name}/{data_type}"

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise_custom_error(500, 600)
        