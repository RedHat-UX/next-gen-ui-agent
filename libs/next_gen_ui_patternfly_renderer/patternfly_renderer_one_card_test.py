from next_gen_ui_agent.agent import NextGenUIAgent
from next_gen_ui_agent.renderer.renderer_base import PLUGGABLE_RENDERERS_NAMESPACE
from next_gen_ui_patternfly_renderer import PatternflyStrategyFactory
from next_gen_ui_testing.data_after_transformation import get_transformed_component
from stevedore.extension import Extension, ExtensionManager


def test_renderer_one_card() -> None:
    agent = NextGenUIAgent()
    extension = Extension(
        name="patternfly",
        entry_point=None,
        plugin=None,
        obj=PatternflyStrategyFactory(),
    )
    em = ExtensionManager(PLUGGABLE_RENDERERS_NAMESPACE).make_test_instance(
        extensions=[extension], namespace=PLUGGABLE_RENDERERS_NAMESPACE
    )
    agent._extension_manager = em
    component = get_transformed_component()
    rendition = agent.design_system_handler([component], "patternfly")[0]["rendition"]
    assert (
        rendition
        == """import React from 'react';
import { Card, CardHeader, CardBody, Button } from '@patternfly/react-core';

function OneCard() {
// Counter state
const [count, setCount] = React.useState(0);

return (
<Card>
    <CardHeader>Toy Story Details</CardHeader>
    <CardBody>
                        <div>
                        <h4>Title</h4>
            <p>Toy Story</p>
                        <h4>Year</h4>
            <p>1995</p>
                        <h4>IMDB Rating</h4>
            <p>8.3</p>
                        <h4>Release Date</h4>
            <p>1995-11-22</p>
                        <h4>Actors</h4>
            <p>['Jim Varney', 'Tim Allen', 'Tom Hanks', 'Don Rickles']</p>
                    </div>
                <div style={ { marginTop: "16px" } }>
            <strong>Counter:</strong> {count}
            <div style={ { marginTop: "8px" , display: "flex" , gap: "8px" } }>
                <Button variant="primary" onClick={()=> setCount(count + 1)}>
                    Increment
                </Button>
                <Button variant="secondary" onClick={()=> setCount(count - 1)}>
                    Decrement
                </Button>
            </div>
        </div>
    </CardBody>
</Card>
);
}

export default OneCard;"""
    )
