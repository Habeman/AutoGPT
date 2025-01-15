from backend.blocks.linear._api import LinearAPIException, LinearClient
from backend.blocks.linear._auth import (
    TEST_CREDENTIALS_INPUT_OAUTH,
    TEST_CREDENTIALS_OAUTH,
    LinearCredentials,
    LinearCredentialsField,
    LinearCredentialsInput,
    LinearScope,
)
from backend.blocks.linear.models import CreateIssueResponse
from backend.data.block import Block, BlockCategory, BlockOutput, BlockSchema
from backend.data.model import SchemaField


class LinearCreateIssueBlock(Block):
    """Block for creating issues on Linear"""

    class Input(BlockSchema):
        credentials: LinearCredentialsInput = LinearCredentialsField(
            scopes=[LinearScope.ISSUES_CREATE],
        )
        title: str = SchemaField(description="Title of the issue")
        description: str | None = SchemaField(description="Description of the issue")
        team_name: str = SchemaField(
            description="Name of the team to create the issue on"
        )
        priority: int | None = SchemaField(
            description="Priority of the issue",
            default=None,
            minimum=0,
            maximum=4,
        )

    class Output(BlockSchema):
        issue_id: str = SchemaField(description="ID of the created issue")
        issue_title: str = SchemaField(description="Title of the created issue")
        error: str = SchemaField(description="Error message if issue creation failed")

    def __init__(self):
        super().__init__(
            id="f9c68f55-dcca-40a8-8771-abf9601680aa",
            description="Creates a new issue on Linear",
            input_schema=self.Input,
            output_schema=self.Output,
            categories={BlockCategory.PRODUCTIVITY, BlockCategory.ISSUE_TRACKING},
            test_input={
                "title": "Test issue",
                "description": "Test description",
                "team_name": "Test team",
                "credentials": TEST_CREDENTIALS_INPUT_OAUTH,
            },
            test_credentials=TEST_CREDENTIALS_OAUTH,
            test_output=[("issue_id", "abc123"), ("issue_title", "Test issue")],
            test_mock={
                "create_issue": lambda *args, **kwargs: (
                    "abc123",
                    "Test issue",
                )
            },
        )

    @staticmethod
    def create_issue(
        credentials: LinearCredentials,
        team_name: str,
        title: str,
        description: str | None = None,
        priority: int | None = None,
    ) -> tuple[str, str]:
        client = LinearClient(credentials=credentials)
        team_id = client.try_get_team_by_name(team_name=team_name)
        response: CreateIssueResponse = client.try_create_issue(
            team_id=team_id,
            title=title,
            description=description,
            priority=priority,
        )
        return response.issue.identifier, response.issue.title

    def run(
        self, input_data: Input, *, credentials: LinearCredentials, **kwargs
    ) -> BlockOutput:
        """Execute the issue creation"""
        try:
            issue_id, issue_title = self.create_issue(
                credentials=credentials,
                team_name=input_data.team_name,
                title=input_data.title,
                description=input_data.description,
                priority=input_data.priority,
            )

            yield "issue_id", issue_id
            yield "issue_title", issue_title

        except LinearAPIException as e:
            yield "error", str(e)
        except Exception as e:
            yield "error", f"Unexpected error: {str(e)}"
