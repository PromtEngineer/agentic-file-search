from google.genai.types import (
    HttpOptions,
    Content,
    GenerateContentResponse,
    Candidate,
    Part,
)
from fs_explorer.models import StopAction, Action


class MockModels:
    async def generate_content(self, *args, **kwargs) -> GenerateContentResponse:
        return GenerateContentResponse(
            candidates=[
                Candidate(
                    content=Content(
                        role="assistant",
                        parts=[
                            Part.from_text(
                                text=Action(
                                    action=StopAction(
                                        final_result="this is a final result"
                                    ),
                                    reason="I am done",
                                ).model_dump_json()
                            )
                        ],
                    )
                )
            ]
        )


class MockAio:
    @property
    def models(self):
        return MockModels()


class MockGenAIClient:
    def __init__(self, api_key: str, http_options: HttpOptions) -> None:
        return None

    @property
    def aio(self) -> MockAio:
        return MockAio()
