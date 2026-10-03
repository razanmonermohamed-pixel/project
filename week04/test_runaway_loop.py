from agent import ReActAgent


class RunawayModelClient:

    def generate(self, prompt):
        return "Continue working. Do not finish."


def test_runaway_loop_stops_at_turn_cap():

    client = RunawayModelClient()

    agent = ReActAgent(
        model_client=client,
        max_turns=3
    )

    trace = agent.run(
        "Run a task that never reaches FINAL."
    )

    assert len(trace) <= 4