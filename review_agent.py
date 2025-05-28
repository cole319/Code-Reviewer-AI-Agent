import os
from dotenv import load_dotenv
import requests
from github import Github, GithubException

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
REPO_NAME = os.getenv("GITHUB_REPOSITORY")
GITHUB_REF = os.getenv("GITHUB_REF")

if not all([GITHUB_TOKEN, OPENROUTER_API_KEY, REPO_NAME, GITHUB_REF]):
    raise EnvironmentError("One or more required environment variables are missing.")

try:
    PR_NUMBER = int(GITHUB_REF.split('/')[-1])
except Exception:
    raise ValueError(f"Unable to parse PR number from GITHUB_REF: {GITHUB_REF}")

g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)
pr = repo.get_pull(PR_NUMBER)

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
        "model": "openai/gpt-3.5-turbo",  # Make configurable
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
    # Posting a simple comment on the PR conversation
    pr.create_issue_comment(comment)

def main():
    print("Fetching code diff...")
    code_diff = get_diff_text(pr)
    if not code_diff:
        print("No code changes detected.")
        return

    print("Sending code diff to LLM...")
    review = review_code_with_llm(code_diff)

    print("Posting review comment...")
    post_comment(pr, f"🤖 AI Code Review:\n\n{review}")

    print("Done.")

if __name__ == "__main__":
    try:
        main()
    except GithubException as e:
        print(f"GitHub API error: {e}")
    except requests.RequestException as e:
        print(f"OpenRouter API error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
