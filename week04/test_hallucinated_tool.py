from model_client import ModelClient
from agent import ReActAgent


def test_hallucinated_tool_is_rejected():
    client = ModelClient()

    agent = ReActAgent(
        model_client=client,
        max_turns=3
    )

    result = agent.execute_tool(
        "fake_tool",
        "test input"
    )

    assert "Unknown tool" in result