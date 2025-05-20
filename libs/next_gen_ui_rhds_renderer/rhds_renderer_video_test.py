from next_gen_ui_agent.agent import NextGenUIAgent
from next_gen_ui_agent.data_transform.types import ComponentDataVideo
from next_gen_ui_testing.agent_testing import extension_manager_rhds
from next_gen_ui_testing.data_after_transformation import get_transformed_component

component_system = "rhds"


def test_renderer_video_full() -> None:
    agent = NextGenUIAgent()
    agent._extension_manager = extension_manager_rhds()
    component = get_transformed_component("video-player")
    rendition = agent.design_system_handler([component], component_system)[0].content
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
    agent._extension_manager = extension_manager_rhds()
    component: ComponentDataVideo = get_transformed_component("video-player")
    delattr(component, "video")
    rendition = agent.design_system_handler([component], component_system)[0].content
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
