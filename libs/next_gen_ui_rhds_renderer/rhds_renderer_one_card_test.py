from next_gen_ui_agent.agent import NextGenUIAgent
from next_gen_ui_agent.renderer.base_renderer import (
    PLUGGABLE_RENDERERS_NAMESPACE,
    StrategyFactory,
)
from next_gen_ui_agent.renderer.one_card_shareable_tests import BaseOneCardRendererTests
from next_gen_ui_rhds_renderer import RhdsStrategyFactory
from next_gen_ui_testing.data_after_transformation import get_transformed_component
from stevedore.extension import Extension, ExtensionManager


class TestRHDSRenderer(BaseOneCardRendererTests):
    def get_strategy_factory(self) -> StrategyFactory:
        return RhdsStrategyFactory()


def test_renderer_one_card() -> None:
    agent = NextGenUIAgent()
    extension = Extension(
        name="rhds", entry_point=None, plugin=None, obj=RhdsStrategyFactory()
    )
    em = ExtensionManager(PLUGGABLE_RENDERERS_NAMESPACE).make_test_instance(
        extensions=[extension], namespace=PLUGGABLE_RENDERERS_NAMESPACE
    )
    agent._extension_manager = em
    component = get_transformed_component()
    rendition = agent.design_system_handler([component], "rhds")[0]["rendition"]
    assert (
        rendition
        == """
<rh-card class="example-fast-facts-card">
  <h2 slot="header">Toy Story Details</h2>
  <div id="one-card-image-text">
        <div>
                <h4>Title</h4>
          <p>Toy Story</p>
        </li>
                <h4>Year</h4>
          <p>1995</p>
        </li>
                <h4>IMDB Rating</h4>
          <p>8.3</p>
        </li>
                <h4>Release Date</h4>
          <p>1995-11-22</p>
        </li>
                <h4>Actors</h4>
          <p>[\'Jim Varney\', \'Tim Allen\', \'Tom Hanks\', \'Don Rickles\']</p>
        </li>
          </div>
      </div>
</rh-card>

<style>
  rh-card {
    & h2 {
      font-size: initial;
    }
  }
  #one-card-image-text {
    display: flex;
    gap: 1rem;
  }
  #one-card-image-text .img {
    width: 50%;
  }
</style>

<script type="module">
  import \'@rhds/elements/rh-cta/rh-cta.js\';
  import \'@rhds/elements/rh-card/rh-card.js\';
</script>"""
    )
