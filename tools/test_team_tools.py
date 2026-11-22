import unittest

from tools.team_tools import issue_body


class IssueBodyTests(unittest.TestCase):
    def test_issue_body_closes_secondary_skills(self):
        task = {
            "id": "T-TEST",
            "title": "Test task",
            "tier": "Core",
            "size": "M",
            "primary": ["DOC"],
            "secondary": ["GIT"],
            "deps": [],
            "acceptance": "The generated body is readable.",
            "refs": "README.md",
            "ai_tip": "Check the output.",
        }

        body = issue_body(task, "Ali", "Fatma", 1)

        self.assertIn("- Skills: DOC (also: GIT)", body)
