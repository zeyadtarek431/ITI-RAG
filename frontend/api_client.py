import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Read API_BASE_URL from environment — never hardcode it!
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000").rstrip("/")

class APIClient:
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url

    def check_health(self) -> dict:
        """Calls GET /health to check backend connectivity."""
        url = f"{self.base_url}/health"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            return {"success": False, "error": f"Backend returned status {response.status_code}"}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"Failed to connect to backend at {self.base_url}: {str(e)}"}

    def query(self, question: str, top_k: int = 3) -> dict:
        """Calls POST /query with question payload."""
        url = f"{self.base_url}/query"
        payload = {"question": question, "top_k": top_k}
        try:
            response = requests.post(url, json=payload, timeout=120)
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            elif response.status_code == 422:
                return {"success": False, "error": "Validation Error: Question string cannot be empty."}
            else:
                return {"success": False, "error": f"API Error ({response.status_code}): {response.text}"}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"Could not reach backend API at {url}. Ensure backend server is running."}

api_client = APIClient()
