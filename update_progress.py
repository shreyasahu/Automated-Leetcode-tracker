import time
from datetime import datetime

import requests

# Replace with your LeetCode username
LEETCODE_USERNAME = "Shreya1015"

# LeetCode GraphQL API URL
LEETCODE_API_URL = "https://leetcode.com/graphql"

# GraphQL Query for recent accepted submissions
QUERY = """
query recentAcSubmissions($username: String!, $limit: Int!) {
    recentAcSubmissionList(username: $username, limit: $limit) {
        id    
        title    
        titleSlug    
        timestamp  
    }
}
"""

HEADERS = {
    "Content-Type": "application/json",
    "Referer": f"https://leetcode.com/{LEETCODE_USERNAME}/",
}


def fetch_leetcode_data():
    """Fetch user's recent accepted submissions from LeetCode API with error handling."""
    session = requests.Session()
    payload = {
        "query": QUERY,
        "variables": {
            "username": LEETCODE_USERNAME,
            "limit": 10  # Fetch last 10 solved problems
        }
    }

    for attempt in range(3):  # Retry mechanism
        try:
            response = session.post(LEETCODE_API_URL, json=payload, headers=HEADERS, timeout=10)
            response.raise_for_status()
            data = response.json()

            if "errors" in data or not data.get("data"):
                print(f"⚠️ Error in API response (Attempt {attempt + 1}/3). Retrying...")
                time.sleep(2)  # Wait before retrying
                continue

            return data["data"]

        except requests.exceptions.RequestException as e:
            print(f"⚠️ Network error: {e} (Attempt {attempt + 1}/3). Retrying...")
            time.sleep(2)

    print("❌ Failed to fetch data after 3 attempts.")
    return None


# Fetch data
data = fetch_leetcode_data()
if not data:
    exit("❌ Could not fetch data. Check API availability or username.")

# Extract recent accepted submissions
recent_problems = data["recentAcSubmissionList"]

# Get today's date in UTC
today_date = datetime.utcnow().strftime("%Y-%m-%d")

# Filtering problems solved today
daily_problems = [
    {
        "date": datetime.utcfromtimestamp(int(p["timestamp"])).strftime("%Y-%m-%d"),
        "title": p["title"],
        "slug": p["titleSlug"],
        "solution_link": f"./solutions/{p['titleSlug']}.py"
    }
    for p in recent_problems if datetime.utcfromtimestamp(int(p["timestamp"])).strftime("%Y-%m-%d") == today_date
]

daily_solved_count = len(daily_problems)  # Number of problems solved today

# Formatting daily problem log
daily_problem_log = """
| Date       | Problem | Solution |
|------------|---------|----------|
"""

for problem in daily_problems:
    daily_problem_log += f"| {problem['date']} | [{problem['title']}](https://leetcode.com/problems/{problem['slug']}/) | [Solution]({problem['solution_link']}) |\n"

# Generate progress.md content
progress_md = f"""# LeetCode Progress Tracker 📈

This file dynamically tracks my solved problems.

## 📅 Daily Log
{daily_problem_log}

---

## 📊 Summary
- ✅ **Problems Solved Today:** {daily_solved_count}
- 📌 **Total Recent Submissions Tracked:** {len(recent_problems)}
- 🏆 Keep grinding! 🚀

"""

# Save to progress.md
with open("progress.md", "w") as f:
    f.write(progress_md)

print(f"✅ Progress updated! {daily_solved_count} problems solved today.")
