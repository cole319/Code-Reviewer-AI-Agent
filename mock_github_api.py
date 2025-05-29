import os

class MockPullRequest:
    def __init__(self):
        self.number = 123
        self.title = "Mock PR for Testing"
        self.body = "This is a mock pull request."
        self.base = type("Base", (), {"ref": "main"})
        self.head = type("Head", (), {"ref": "feature/test-branch"})
        self.user = type("User", (), {"login": "mockuser"})

    def get_files(self):
        return [
            type("File", (), {"filename": "mock_file.py", "patch": "print('Hello world')", "status": "modified"})
        ]

    def create_review(self, body, event, comments=None):
        print(f"[MOCK REVIEW] Event: {event}\n{body}\nComments: {comments}")

class MockRepo:
    def get_pull(self, number):
        if number != 123:
            raise Exception(f"Pull request #{number} not found.")
        return MockPullRequest()

class MockGithub:
    def __init__(self, token):
        self.token = token

    def get_repo(self, full_name):
        return MockRepo()
