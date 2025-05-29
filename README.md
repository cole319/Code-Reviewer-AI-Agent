# AI Code Reviewer GitHub Action

[![GitHub Workflow](https://github.com/cole319/Code-Reviewer-AI-Agent/actions/workflows/code-review.yml/badge.svg)](https://github.com/cole319/Code-Reviewer-AI-Agent/actions/workflows/code-review.yml)

## Overview

This repository contains a GitHub Action and Python agent that automatically reviews pull requests using OpenRouter’s GPT-3.5-turbo language model. Upon opening or updating a pull request, the action fetches the code diff, sends it to the LLM for a detailed code review, and posts the review as a comment on the PR.

It helps teams maintain code quality by providing quick, AI-powered feedback directly inside GitHub, reducing manual review load and catching common issues early.

---

## Features

- Automatically triggers on PR opened, reopened, or updated (synchronize)
- Fetches diff of changed files and sends to LLM for review
- Customizable review prompt with fallback default
- Posts constructive, respectful, and concise review comments on the PR
- Dry-run mode for local testing without posting comments
- Uses secure GitHub Secrets for tokens and API keys
- Supports local development with dotenv and mock GitHub API

---

## Getting Started

### Prerequisites

- Python 3.11+
- GitHub Personal Access Token (PAT) with `repo` and `pull-requests` permissions
- OpenRouter API key (https://openrouter.ai)
- Repository admin rights to add GitHub Actions workflows and secrets

### Setup

1.  **Clone the repository**

    ```bash
    git clone https://github.com/cole319/Code-Reviewer-AI-Agent.git
    cd Code-Reviewer-AI-Agent
    ```

2.  **Create .env for local development (optional)**

    ```env
    MY_GITHUB_PAT=your_personal_access_token
    OPENROUTER_API_KEY=your_openrouter_api_key
    GITHUB_REPOSITORY=owner/repo
    PR_NUMBER=123
    DRY_RUN=1
    ```

3.  **Install dependencies**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure GitHub Secrets**

    - In your repository, add these secrets:

    - `MY_GITHUB_PAT` (your GitHub PAT)

    - `OPENROUTER_API_KEY` (OpenRouter API key)

5.  **Push the workflow**

    The code-review.yml GitHub Actions workflow is already included. It triggers on pull request events.

---

### Usage

- Open or update a pull request in the repository.

- The GitHub Action will automatically:

- Fetch the PR diff

- Send code changes to OpenRouter LLM for review

- Post the AI-generated review comment on the PR

---

### Configuration

- Dry Run Mode: Set environment variable `DRY_RUN=1` to print review output locally or in GitHub logs without posting comments.

- Prompt Customization: Modify or create prompt.txt to provide a custom review prompt.

- Token Environment Variables:

- `GITHUB_TOKEN` or `MY_GITHUB_PAT` — your GitHub access token

- `OPENROUTER_API_KEY` — your OpenRouter API key

---

### File Structure

```css
.
├── code-review.yml    /* GitHub Actions workflow */
├── review_agent.py    /* Main Python script for PR review logic */
├── requirements.txt    /* Python dependencies */
├── mock_github_api.py    /* Mock script to run local tests */
├── prompt.txt    /* Optional custom prompt for LLM */
└── README.md

```

---

### Development & Testing

Use DRY_RUN=1 in .env or workflow to avoid posting comments during tests.

For local testing, run:

```bash
python review_agent.py
```

Use mocked GitHub API in mock_github_api.py (optional, for offline/dev).

License
MIT License © 2025 cole319
