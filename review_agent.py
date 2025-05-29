import os
from dotenv import load_dotenv
import requests
from github import Github

load_dotenv()

# === For Local Test ===
# USE_MOCK = True

# if USE_MOCK:
    # from mock_github_api import MockGithub as Github


# === Secure Token Selection ===
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN") or os.getenv("MY_GITHUB_PAT")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not GITHUB_TOKEN:
    raise ValueError("❌ GitHub token not found. Set GITHUB_TOKEN (for CI) or MY_GITHUB_PAT (for local dev)")
if not OPENROUTER_API_KEY:
    raise ValueError("❌ OpenRouter API key not found.")

# === GitHub Environment Setup ===
REPO_NAME = os.getenv("GITHUB_REPOSITORY")
PR_NUMBER = os.getenv("PR_NUMBER")

if not REPO_NAME or not PR_NUMBER or not PR_NUMBER.isdigit():
    raise ValueError("❌ GITHUB_REPOSITORY or PR_NUMBER is invalid/missing.")

# === GitHub Setup ===
g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)
print(f"Repo: {REPO_NAME}, PR Number: {PR_NUMBER}")
print(type(PR_NUMBER))
pr = repo.get_pull(int(PR_NUMBER))

# === Get Diff ===
def get_diff_text(pr):
    changes = []
    for f in pr.get_files():
        if f.patch:
            changes.append(f"File: {f.filename}\n{f.patch}")
    return "\n\n".join(changes)

# === Review via LLM ===
def review_code_with_llm(code_diff):
    default_prompt = (
        "You are a senior software engineer reviewing a pull request. "
        "Your job is to provide clear, constructive, and concise feedback on the code changes. "
        "Point out bugs, design flaws, code smells, and areas for improvement. Be respectful and precise."
    )

    try:
        with open("prompt.txt", "r") as prompt_file:
            base_prompt = prompt_file.read().strip()
            if not base_prompt:
                raise ValueError("prompt.txt is empty. Using default prompt.")
    except (FileNotFoundError, ValueError):
        base_prompt = default_prompt

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": base_prompt},
            {"role": "user", "content": f"Review the following code changes:\n\n{code_diff}"}
        ],
        "temperature": 0.4
    }
    res = requests.post(url, headers=headers, json=data, timeout=30)
    res.raise_for_status()
    return res.json()["choices"][0]["message"]["content"]

# === Post Back to PR ===
def post_comment(pr, comment):
    pr.create_issue_comment(f"🤖 **AI Code Review**:\n\n{comment}")

# === Main ===
def main():
    print("📦 Fetching PR code diff...")
    code_diff = get_diff_text(pr)
    if not code_diff:
        print("✅ No code changes to review.")
        return

    print("🧠 Sending code to LLM...")
    review = review_code_with_llm(code_diff)

    if os.getenv("DRY_RUN") == "1":
        print("🧪 Dry run mode. Review not posted.")
        print("\n🔍 Review Output:\n")
        print(review)
    else:
        print("📝 Posting comment on PR...")
        post_comment(pr, review)
        print("🎉 Done.")

if __name__ == "__main__":
    main()