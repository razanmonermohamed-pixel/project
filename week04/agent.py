from model_client import ModelClient


class ReActAgent:
    def __init__(self, model_client, max_turns=5):
        self.model_client = model_client
        self.max_turns = max_turns
        self.max_cost = 3
        self.current_cost = 0

        self.tools = {
            "check_website": self.check_website
        }

    def check_website(self, url):
        return f"Website checked: {url}"

    def execute_tool(self, tool_name, tool_input):
        if tool_name not in self.tools:
            return f"Error: Unknown tool '{tool_name}'"

        return self.tools[tool_name](tool_input)

    def run(self, task):
        trace = []

        for turn in range(1, self.max_turns + 1):

            prompt = f"""
You are a ReAct agent.

Task:
{task}

Turn:
{turn}

Decide what action should be taken next.
Return a short response describing the next action.
"""

            response = self.model_client.generate(prompt)

            self.current_cost += 1

            trace.append({
                "turn": turn,
                "cost": self.current_cost,
                "response": response
            })

            if self.current_cost >= self.max_cost:
                trace.append({
                    "turn": turn,
                    "cost": self.current_cost,
                    "response": "Stopped: Cost budget exceeded"
                })
                break

            if "FINAL" in response.upper():
                trace.append({
                    "turn": turn,
                    "cost": self.current_cost,
                    "response": "Stopped: FINAL detected"
                })
                break

        return trace


if __name__ == "__main__":
    client = ModelClient()

    agent = ReActAgent(
        model_client=client,
        max_turns=5
    )

    trace = agent.run(
        "Check a university website and determine whether an important change has occurred."
    )

    print("\n===== INSTRUMENTED TRACE =====")

    for item in trace:
        print(f"Turn      : {item['turn']}")
        print(f"Cost      : {item['cost']}")
        print(f"Response  : {item['response']}")
        print("-" * 50)