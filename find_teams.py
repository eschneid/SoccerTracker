import requests

# Replace with your actual API key from football-data.org
API_KEY = "ed316788f094478388d2751b180b027e"
COMPETITION = "PL"  # Premier League

url = f"https://api.football-data.org/v4/competitions/{COMPETITION}/teams"

headers = {
    "X-Auth-Token": API_KEY
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()
    teams = data.get("teams", [])
    
    brentford_team = next((team for team in teams if team["name"] == "Brentford FC"), None)
    
    if brentford_team:
        print(f"Brentford FC team ID is: {brentford_team['id']}")
    else:
        print("Brentford FC not found in this competition.")
else:
    print(f"Error: {response.status_code}, {response.text}")

