from next_gen_ui_agent.base_renderer.base_renderer import IMAGE_SUFFIXES, RenderStrategyBase
from next_gen_ui_agent.base_renderer.types import RenderContexSetOfCard
from next_gen_ui_agent.types import UIComponentMetadata


class SetOfCardsRenderStrategy(RenderStrategyBase[RenderContexSetOfCard]):
    COMPONENT_NAME = "set-of-cards"

    def main_processing(self, component: UIComponentMetadata):
        # TODO: Use super()._find_field
        subtitle_field = next(
            (
                field
                for field in component["fields"]
                if field["name"].lower() in ["title", "name", "header"]
            ),
            None,
        )
        if subtitle_field:
            self._rendering_context["subtitle_field"] = subtitle_field
            self._rendering_context["fields"].remove(subtitle_field)

        image_field = next(
            (
                field
                for field in component["fields"]
                for d in field["data"]
                if type(d) is str and d.endswith(IMAGE_SUFFIXES)
            ),
            None,
        )
        if image_field:
            self._rendering_context["image_field"] = image_field
            self._rendering_context["fields"].remove(image_field)
