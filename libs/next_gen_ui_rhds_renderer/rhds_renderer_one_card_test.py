from next_gen_ui_agent.agent import NextGenUIAgent
from next_gen_ui_agent.renderer.base_renderer import StrategyFactory
from next_gen_ui_agent.renderer.one_card_shareable_tests import BaseOneCardRendererTests
from next_gen_ui_rhds_renderer import RhdsStrategyFactory
from next_gen_ui_testing.agent_testing import extension_manager_rhds
from next_gen_ui_testing.data_after_transformation import (
    get_transformed_component,
    get_transformed_component_testing_data,
)

component_system = "rhds"


# Test class for RHDS renderer using shared test cases
class TestOneCardRHDSRendererWithShareableTests(BaseOneCardRendererTests):
    def get_strategy_factory(self) -> StrategyFactory:
        return RhdsStrategyFactory()


def test_renderer_one_card_full() -> None:
    agent = NextGenUIAgent()
    agent._extension_manager = extension_manager_rhds()
    component = get_transformed_component()
    rendition = agent.design_system_handler([component], component_system)[0].content
    print(rendition)
    assert (
        rendition
        == """
<rh-card class="ngui-one-card">
  <h2 slot="header">Toy Story Details</h2>

  <dl>

      <dt>Title</dt>
      <dd>Toy Story</dd>

      <dt>Year</dt>
      <dd>1995</dd>

      <dt>IMDB Rating</dt>
      <dd>8.3</dd>

      <dt>Release Date</dt>
      <dd>1995-11-22</dd>

      <dt>Actors</dt>
      <dd>Jim Varney, Tim Allen, Tom Hanks, Don Rickles</dd>
  </dl>
</rh-card>

<style>
  .ngui-one-card {
    /* Definition list itself */
    & dl {
      display: flex;
      flex-flow: column;
      gap: var(--rh-space-md, 8px);
      margin: 0;
      padding: 0;

      & dt {
        font-weight: var(--rh-font-weight-heading-medium, 500);
      }

      & dd {
        margin: 0;
        padding-block-end: var(--rh-space-md, 8px);
        border-block-end: var(--rh-border-width-sm, 1px) solid var(--rh-color-border-subtle);

        &:last-child {
          padding-block-end: 0;
          border-block-end: none;
        }
      }
    }
</style>

<script type="module">
  import '@rhds/elements/rh-cta/rh-cta.js';
  import '@rhds/elements/rh-card/rh-card.js';
</script>"""
    )


def test_renderer_one_card_array_boolean() -> None:
    agent = NextGenUIAgent()
    agent._extension_manager = extension_manager_rhds()
    component = get_transformed_component_testing_data()

    rendition = agent.design_system_handler([component], component_system)[0].content
    assert rendition
    assert "True, False" in rendition


def test_renderer_one_card_array_numbers() -> None:
    agent = NextGenUIAgent()
    agent._extension_manager = extension_manager_rhds()
    component = get_transformed_component_testing_data()
    rendition = agent.design_system_handler([component], component_system)[0].content
    assert rendition
    assert "1, 2, 3" in rendition


def test_renderer_one_card_image() -> None:
    agent = NextGenUIAgent()
    agent._extension_manager = extension_manager_rhds()
    component = get_transformed_component_testing_data()

    rendition = agent.design_system_handler([component], component_system)[0].content
    assert rendition
    assert (
        '<img src="https://image.tmdb.org/t/p/w440_and_h660_face/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg" slot="image" aria-label="Toy Story Details">'
        in rendition
    )
    assert "&::part(image) {" in rendition
