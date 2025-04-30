from next_gen_ui_agent.agent import NextGenUIAgent
from next_gen_ui_agent.renderer.base_renderer import StrategyFactory
from next_gen_ui_agent.renderer.one_card_shareable_tests import BaseOneCardRendererTests
from next_gen_ui_rhds_renderer import RhdsStrategyFactory
from next_gen_ui_testing.agent_testing import extension_manager_rhds
from next_gen_ui_testing.data_after_transformation import (
    get_transformed_component,
    get_transformed_component_testing_data,
)


class TestRHDSRenderer(BaseOneCardRendererTests):
    def get_strategy_factory(self) -> StrategyFactory:
        return RhdsStrategyFactory()


component_system = "rhds"


def test_renderer_one_card_full() -> None:
    agent = NextGenUIAgent()
    agent._extension_manager = extension_manager_rhds()
    component = get_transformed_component()
    rendition = agent.design_system_handler([component], component_system)[0].rendition
    print(rendition)
    assert (
        rendition
        == """
<rh-card class="ngui-one-card reverse" >
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
rh-card[variant="promo"] {
  container-name: promo;
  container-type: inline-size;
}

@container promo (min-width: 768px) {
  .reverse::part(container) {
    grid-template-columns: 1fr 2fr;
  }

  .reverse::part(image) {
    justify-self: start;
    order: -10;
  }
}


.ngui-one-card {
  & dl {
    display: flex;
    flex-flow: column;
    gap: var(--rh-space-md);
    margin: 0;
    padding: 0;
    list-style-type: none;
    & dd {
      margin-block: 0;
      margin-inline-start: 0;
      padding-block-end: var(--rh-space-md);
      border-block-end: 1px solid var(--rh-color-border-subtle);
      &:last-child {
        padding-block-end: 0;
        border-block-end: none;
      }
      & :first-child {
        margin-block-start: 0;
      }
      & :last-child {
        margin-block-end: 0;
      }
    }
    & dt {
      margin-block-end: 0 var(--rh-space-md);
      font-weight: var(--rh-font-weight-heading-regular);
      font-size: var(--rh-font-size-body-text-md);
      font-family: var(--rh-font-family-body-text);
      line-height: var(--rh-line-height-body-text);
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

    rendition = agent.design_system_handler([component], component_system)[0].rendition
    assert rendition
    assert "True, False" in rendition


def test_renderer_one_card_array_numbers() -> None:
    agent = NextGenUIAgent()
    agent._extension_manager = extension_manager_rhds()
    component = get_transformed_component_testing_data()
    rendition = agent.design_system_handler([component], component_system)[0].rendition
    assert rendition
    assert "1, 2, 3" in rendition


def test_renderer_one_card_image() -> None:
    agent = NextGenUIAgent()
    agent._extension_manager = extension_manager_rhds()
    component = get_transformed_component_testing_data()

    rendition = agent.design_system_handler([component], component_system)[0].rendition
    assert rendition
    assert (
        '<img src="https://image.tmdb.org/t/p/w440_and_h660_face/uXDfjJbdP4ijW5hWSBrPrlKpxab.jpg" slot="image" aria-label="Toy Story Details">'
        in rendition
    )
    assert '<rh-card class="ngui-one-card reverse" variant="promo">' in rendition


def test_renderer_one_card_padding() -> None:
    agent = NextGenUIAgent()
    agent._extension_manager = extension_manager_rhds()
    component = get_transformed_component_testing_data()

    rendition = agent.design_system_handler([component], component_system)[0].rendition
    assert rendition
    assert "gap: var(--rh-space-md);" in rendition


def test_renderer_one_card_padding_one_field() -> None:
    agent = NextGenUIAgent()
    agent._extension_manager = extension_manager_rhds()
    component = get_transformed_component_testing_data()
    component.fields = [component.fields[0]]

    rendition = agent.design_system_handler([component], component_system)[0].rendition
    assert rendition
    assert "gap: var(--rh-space-lg);" in rendition
