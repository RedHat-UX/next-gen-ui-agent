from next_gen_ui_agent.agent import NextGenUIAgent
from next_gen_ui_agent.renderer.base_renderer import StrategyFactory
from next_gen_ui_agent.renderer.table_shareable_tests import BaseTableRendererTests
from next_gen_ui_rhds_renderer import RhdsStrategyFactory
from next_gen_ui_testing.agent_testing import extension_manager_rhds
from next_gen_ui_testing.data_after_transformation import get_transformed_component

component_system = "rhds"


# Test class for RHDS renderer using shared test cases
class TestTableRHDSRendererWithShareableTests(BaseTableRendererTests):
    def get_strategy_factory(self) -> StrategyFactory:
        return RhdsStrategyFactory()


def test_renderer_table() -> None:
    agent = NextGenUIAgent()
    agent._extension_manager = extension_manager_rhds()
    component = get_transformed_component("table")
    rendition = agent.design_system_handler([component], component_system)[0].content
    print(rendition)
    assert (
        rendition
        == """
<rh-table>
  <table>
        <caption>Movies</caption>
        <colgroup>
            <col>
            <col>
          </colgroup>
    <thead>
      <tr>
                <th scope="col">Titles<rh-sort-button></rh-sort-button>
                <th scope="col">Years<rh-sort-button></rh-sort-button>
                </th>
      </tr>
    </thead>
    <tbody>
            <tr>
                              <td>Toy Story</td>
                                      <td>1995</td>
                    </tr>
            <tr>
                              <td>Toy Story 2</td>
                                      <td>1999</td>
                    </tr>
          </tbody>
  </table>
</rh-table>

<link rel="stylesheet" href="../rh-table-lightdom.css">

<script type="module">
  import '@rhds/elements/rh-table/rh-table.js';
</script>"""
    )
