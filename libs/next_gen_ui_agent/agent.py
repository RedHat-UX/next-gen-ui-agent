class NextGenUIAgent:
    """Next Gen UI Agent."""

    async def say_hello_async(self) -> str:
        return "next_gen_ui_agent_async"

    def say_hello(self) -> str:
        print("Hallo from main next_gen_ui_agent.NextGenUIAgent")
        return "next_gen_ui_agent"


if __name__ == "__main__":
    agent = NextGenUIAgent()
    agent.say_hello()
