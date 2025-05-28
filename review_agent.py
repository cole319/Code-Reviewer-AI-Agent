import os
from dotenv import load_dotenv
import requests
from github import Github, GithubException

load_dotenv()

# Load and validate environment variables
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
REPO_NAME = os.getenv("GITHUB_REPOSITORY")
GITHUB_REF = os.getenv("GITHUB_REF")

missing = [var for var in ["GITHUB_TOKEN", "OPENROUTER_API_KEY", "GITHUB_REPOSITORY", "GITHUB_REF"] if not os.getenv(var)]
if missing:
    raise EnvironmentError(f"❌ Missing required environment variables: {', '.join(missing)}")

# Extract PR number
try:
    PR_NUMBER = GITHUB_REF.split('/')[2]
except Exception:
    raise ValueError(f"❌ Unable to parse PR number from GITHUB_REF: {GITHUB_REF}")

# GitHub API setup
g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)
pr = repo.get_pull(int(PR_NUMBER))

def get_diff_text(pr):
    changes = []
    for f in pr.get_files():
        if f.patch:
            changes.append(f"File: {f.filename}\n{f.patch}")
    return "\n\n".join(changes)

def review_code_with_llm(code_diff):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {
                "role": "system",
                "content": "You are a senior software engineer reviewing code. Be clear, constructive, and concise."
            },
            {
                "role": "user",
                "content": f"Review the following code changes:\n\n{code_diff}"
            }
        ],
        "temperature": 0.4
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

def post_comment(pr, comment):
    pr.create_issue_comment(comment)

def main():
    print("📥 Fetching code diff...")
    code_diff = get_diff_text(pr)
    if not code_diff.strip():
        print("✅ No code changes to review.")
        return

    print("🤖 Sending diff to OpenRouter...")
    review = review_code_with_llm(code_diff)
    print("🧾 LLM Review:\n", review[:500], "..." if len(review) > 500 else "")

    print("📤 Posting review comment...")
    post_comment(pr, f"🤖 **AI Code Review**:\n\n{review}")
    print("✅ Done.")

if __name__ == "__main__":
    try:
        main()
    except GithubException as e:
        print(f"❌ GitHub API error: {e}")
    except requests.RequestException as e:
        print(f"❌ OpenRouter API error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
