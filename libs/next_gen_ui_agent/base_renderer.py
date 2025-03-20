from abc import ABC, ABCMeta, abstractmethod
from .types import UIComponentMetadata
import json

IMAGE_SUFFIXES = ("jpg","png","gif","jpeg","bmp")

class RenderStrategy(ABC):

    _rendering_context: dict

    def __init__(self):
        self._rendering_context = dict()
    
    def preprocess_rendering_context(self, component: UIComponentMetadata):
        if not component:
            return
        fields = component["fields"]
        self._rendering_context["fields"] = fields.copy()
        self._rendering_context["title"] = component["title"]
        self._rendering_context["data_length"] = max(len(field["data"]) for field in fields)
        self._rendering_context["field_names"] = [field["name"] for field in fields]

    def main_processing(self, component: UIComponentMetadata):
        pass

    def generate_output(self, component: UIComponentMetadata):
        return json.dumps(component)
    
    def render(self, component: UIComponentMetadata):
        self.preprocess_rendering_context(component)
        self.main_processing(component)
        return self.generate_output(component)


class OneCardRenderStrategy(RenderStrategy):

    def main_processing(self, component: UIComponentMetadata):
        # Trying to find field that would contain an image link
        fields = component["fields"]
        
        field_with_image_suffix = next( (field for field in fields for d in field["data"] if type(d) is str and d.endswith(IMAGE_SUFFIXES)), None)
        if field_with_image_suffix: 
            image = next((data for data in field_with_image_suffix["data"] if type(data) is str and data.endswith(IMAGE_SUFFIXES)), None)
            self._rendering_context["image"] = image
            self._rendering_context["fields"].remove(field_with_image_suffix)

class TableRenderStrategy(RenderStrategy):
    pass

# TODO: Not yet implemented
class PieChartRenderStrategy(RenderStrategy):
    pass

# TODO: Not yet implemented
class LineChartRenderStrategy(RenderStrategy):
    pass

class SetOfCardsRenderStrategy(RenderStrategy):

    def main_processing(self, component: UIComponentMetadata):
        subtitle_field = next( (field for field in component["fields"] if field["name"].lower() in ["title","name","header"]), None)
        if subtitle_field :
            self._rendering_context["subtitle_field"] = subtitle_field
            self._rendering_context["fields"].remove(subtitle_field)

        image_field = next( (field for field in component["fields"] for d in field["data"] if type(d) is str and d.endswith(IMAGE_SUFFIXES) ), None)
        if image_field :
            self._rendering_context["image_field"] = image_field
            self._rendering_context["fields"].remove(image_field)

class ImageRenderStrategy(RenderStrategy):

    def main_processing(self, component: UIComponentMetadata):
        # Trying to find field that would contain an image link
        fields = component["fields"]
        
        field_with_image_suffix = next( (field for field in fields for d in field["data"] if type(d) is str and d.endswith(IMAGE_SUFFIXES)), None)
        if field_with_image_suffix: 
            image = next((data for data in field_with_image_suffix["data"] if type(data) is str and data.endswith(IMAGE_SUFFIXES)), None)
            self._rendering_context["image"] = image
            self._rendering_context["fields"].remove(field_with_image_suffix)

class VideoRenderStrategy(RenderStrategy):

    def main_processing(self, component: UIComponentMetadata):
        fields = component["fields"]

        field_with_video_suffix = next( (field for field in fields for d in field["data"] if type(d) is str and "youtube.com" in d), None)
        if field_with_video_suffix:
            video = next((data for data in field_with_video_suffix["data"] if type(data) is str and "youtube.com" in data), None)
            video_img = "https://fakeimg.pl/900x499/282828/eae0d0"
            if video.startswith('https://www.youtube.com/watch?v='):
                video_id = video.replace('https://www.youtube.com/watch?v=', '')
                video = f"https://www.youtube.com/embed/{video_id}"
                # https://img.youtube.com/vi/v-PjgYDrg70/maxresdefault.jpg
                video_img = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
            self._rendering_context["video"] = video
            self._rendering_context["video_img"] = video_img
            self._rendering_context["fields"].remove(field_with_video_suffix)
        if not video:
            # We cannot render video without the link
            raise ValueError("Cannot render video without the link")

class AudioPlayerRenderStrategy(RenderStrategy):

    def main_processing(self, component: UIComponentMetadata):
        fields = component["fields"]

        field_with_image_suffix = next( (field for field in fields for d in field["data"] if type(d) is str and d.endswith(IMAGE_SUFFIXES)), None)
        if field_with_image_suffix:
            image = next((data for data in field_with_image_suffix["data"] if type(data) is str and data.endswith(IMAGE_SUFFIXES)), None)
            self._rendering_context["image"] = image
            self._rendering_context["fields"].remove(field_with_image_suffix)

        field_with_audio_suffix = next( (field for field in fields for d in field["data"] if type(d) is str and d.endswith(".mp3")), None)
        if field_with_audio_suffix:
            audio = next((data for data in field_with_audio_suffix["data"] if type(data) is str and data.endswith(".mp3")), None)
            self._rendering_context["audio"] = audio
            self._rendering_context["fields"].remove(audio)

        if not audio:
            # We cannot render video without the link
            raise ValueError("Cannot render video without the link")

class RendererContext:
    render_strategy: RenderStrategy

    def __init__(self, strategy: RenderStrategy):
        self.render_strategy = strategy
            
    def render(self, component: UIComponentMetadata):
        return self.render_strategy.render(component)

# This will be our Stevedore plugin driver entry point
# Default implementation will return preprocessed DTOs that can be JSON'ified for default output
class StrategyFactory(metaclass=ABCMeta):
    
    @abstractmethod
    def get_render_strategy(self, component : UIComponentMetadata):
        match component["component"]:
            case "one-card":
                return OneCardRenderStrategy()
            case "table":
                return TableRenderStrategy()
            case "set-of-cards":
                return SetOfCardsRenderStrategy()
            case "image":
                return ImageRenderStrategy()
            case "video-player":
                return VideoRenderStrategy()
            case "audio-player":
                return AudioPlayerRenderStrategy()
            # TODO: Not yet implemented chart types
            # case "chart-line":
            #     return LineChartRenderStrategy()
            # case "chart-pie":
            #     return PieChartRenderStrategy()
            case _:
                raise ValueError(f"This component: {component['component']} is not supported by rendering plugin.")
            
class JsonStrategyFactory(StrategyFactory):
    def get_render_strategy(self, component : UIComponentMetadata):
        return super().get_render_strategy(component)