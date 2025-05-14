from next_gen_ui_agent.agent import NextGenUIAgent
from next_gen_ui_testing.agent_testing import extension_manager_rhds
from next_gen_ui_testing.data_after_transformation import get_transformed_component

component_system = "rhds"


def test_renderer_image_full() -> None:
    agent = NextGenUIAgent()
    agent._extension_manager = extension_manager_rhds()
    component = get_transformed_component("image")
    rendition = agent.design_system_handler([component], component_system)[0].content
    print(rendition)
    assert (
        rendition
        == """
<rh-card class="ngui-image-card">
  <img src="https://image.tmdb.org/t/p/w440_and_h660_face/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg" slot="image" alt="Toy Story Poster">
  <h2 slot="header">Toy Story Poster</h2>
</rh-card>

<style>
  .ngui-image-card {
    &::part(header) {
      order: 0;
    }
    &::part(image) {
      order: 1;
      padding: var(--rh-space-xl, 24px);
    }
    &::part(footer) {
      order: 2;
    }
    @container (min-width: 768px) {
      &::part(image) {
        padding: var(--rh-space-2xl, 32px);
      }
    }
  }
</style>


<script type="module">
  import '@rhds/elements/rh-card/rh-card.js';
</script>"""
    )
