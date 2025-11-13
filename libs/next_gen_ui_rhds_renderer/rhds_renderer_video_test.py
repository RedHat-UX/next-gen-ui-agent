from next_gen_ui_agent.agent import NextGenUIAgent
from next_gen_ui_agent.data_transform.types import ComponentDataVideo
from next_gen_ui_agent.renderer.base_renderer import StrategyFactory
from next_gen_ui_agent.renderer.video_shareable_tests import BaseVideoRendererTests
from next_gen_ui_rhds_renderer import RhdsStrategyFactory
from next_gen_ui_testing.agent_testing import extension_manager_for_testing
from next_gen_ui_testing.data_after_transformation import get_transformed_component

component_system = "rhds"


class TestVideoRHDSRendererWithShareableTests(BaseVideoRendererTests):
    """Test class for RHDS renderer using shared test cases for video component."""

    def get_strategy_factory(self) -> StrategyFactory:
        return RhdsStrategyFactory()


def test_renderer_video_full() -> None:
    agent = NextGenUIAgent()
    agent._extension_manager = extension_manager_for_testing(
        "rhds", RhdsStrategyFactory()
    )
    component = get_transformed_component("video-player")
    rendition = agent.generate_rendering(component, component_system).content
    print(rendition)
    assert (
        rendition
        == """<rh-video-embed class="ngui-video-player">
  <img slot="thumbnail" src="https://img.youtube.com/vi/v-PjgYDrg70/maxresdefault.jpg" alt="Toy Story Trailer"/>
  <template>
    <iframe title="Toy Story Trailer" width="900" height="499" src="https://www.youtube.com/embed/v-PjgYDrg70" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
  </template>
  <p slot="caption">Toy Story Trailer</p>
</rh-video-embed>

<script type="module">
  import '@rhds/elements/rh-video-embed/rh-video-embed.js';
</script>

<style>
  .ngui-video-player {
    &::part(caption) {
      font-family: var(--rh-font-family-heading);
      text-align: center;
    }
</style>
"""
    )


def test_renderer_video_bad_url() -> None:
    agent = NextGenUIAgent()
    agent._extension_manager = extension_manager_for_testing(
        "rhds", RhdsStrategyFactory()
    )
    component: ComponentDataVideo = get_transformed_component("video-player")
    delattr(component, "video")
    rendition = agent.generate_rendering(component, component_system).content
    print(rendition)
    assert (
        rendition
        == """<rh-card class="ngui-one-card">
  <h2 slot="header">Toy Story Trailer</h2>
  <p>No video to play.</p>
</rh-card>

<script type="module">
  import '@rhds/elements/rh-card/rh-card.js';
</script>
"""
    )
