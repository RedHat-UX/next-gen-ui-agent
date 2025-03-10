class NextGenUIAgent:
    """Next Gen UI Agent"""

    def say_hello(self) -> str:
        print("Hallo from main next_gen_ui_agent.NextGenUIAgent")
        return "next_gen_ui_agent"


if __name__ == "__main__":
    agent = NextGenUIAgent()
    agent.say_hello()
