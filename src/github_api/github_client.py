from github import Github  # ty:ignore[unresolved-import]


class GitHubClient:

    def __init__(
        self,
        token_path: str,
        repository_name: str,
        bot_username: str
    ):
        with open(token_path, "r") as f:
            token = f.read().strip()

        self.github = Github(token)

        self.repo = self.github.get_repo(
            repository_name
        )

        self.bot_username = bot_username

    #
    # Issues
    #

    def get_assigned_issues(self):

        issues = self.repo.get_issues(
            state="open"
        )

        assigned = []

        for issue in issues:

            if issue.pull_request:
                continue

            assignees = [
                a.login
                for a in issue.assignees
            ]

            if self.bot_username in assignees:
                assigned.append(issue)

        return sorted(
            assigned,
            key=lambda i: i.number
        )

    def get_issue_comments(
        self,
        issue_number: int
    ):

        issue = self.repo.get_issue(
            issue_number
        )

        comments = []

        for comment in issue.get_comments():

            comments.append(
                {
                    "id": comment.id,
                    "user": comment.user.login,
                    "body": comment.body,
                    "created_at": comment.created_at
                }
            )

        return comments

    #
    # Pull Requests
    #

    def create_pull_request(
        self,
        title: str,
        body: str,
        branch_name: str,
        base_branch: str = "main"
    ):

        return self.repo.create_pull(
            title=title,
            body=body,
            head=branch_name,
            base=base_branch
        )

    def get_open_pull_requests(self):

        return self.repo.get_pulls(
            state="open"
        )

    def get_pull_request(
        self,
        pr_number: int
    ):

        return self.repo.get_pull(
            pr_number
        )

    def get_pull_request_comments(
        self,
        pr_number: int
    ):

        pr = self.repo.get_pull(
            pr_number
        )

        comments = []

        for comment in pr.get_issue_comments():

            comments.append(
                {
                    "id": comment.id,
                    "user": comment.user.login,
                    "body": comment.body
                }
            )

        return comments

    #
    # Comments
    #

    def post_comment(
        self,
        issue_number: int,
        message: str
    ):

        issue = self.repo.get_issue(
            issue_number
        )

        issue.create_comment(
            message
        )

    def post_pr_comment(
        self,
        pr_number: int,
        message: str
    ):

        pr = self.repo.get_pull(
            pr_number
        )

        pr.create_issue_comment(
            message
        )

    #
    # Merge Tracking
    #

    def get_merged_pull_requests(self):

        merged = []

        pulls = self.repo.get_pulls(
            state="closed"
        )

        for pr in pulls:

            if pr.merged:
                merged.append(pr)

        return merged

    #
    # Helper
    #

    def get_issue(
        self,
        issue_number: int
    ):

        return self.repo.get_issue(
            issue_number
        )