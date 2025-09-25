from a2a.types import AgentCapabilities, AgentCard, AgentSkill

skill = AgentSkill(
    id="generate_ui_components",
    name="Generates UI component",
    description="Returns generated UI component",
    tags=["ui"],
    examples=[
        "First message TextPart should be user prompt. backend data could be passed as 'data' field in metadata or following DataParts"
    ],
)

# This will be the public-facing agent card
card = AgentCard(
    name="Next Gen UI Agent",
    description="Generates UI component based on structured input data and user prompt",
    url="http://localhost:9999/",
    version="1.0.0",
    default_input_modes=["text"],
    default_output_modes=["text"],
    capabilities=AgentCapabilities(streaming=True),
    skills=[skill],
    supports_authenticated_extended_card=False,
)
