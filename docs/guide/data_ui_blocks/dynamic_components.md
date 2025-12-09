# Dynamic Components

These fully AI/LLM selected and configured dynamic *Data UI Blocks* are now supported by *UI Agent*. UI Agent selects UI 
component which matches best the current user prompt and [input data structure](../input_data/structure.md).

Optionally, this components can be [mapped per `InputData.type` and pre-configured in this mapping](../configuration.md#components-listagentconfigcomponent-optional),
LLM is not used/necessary in this case.

See details about [component selection and configuration process](index.md#selection-and-configuration-process).

## Components for [one `Object` input data](../input_data/structure.md#one-object-input-data)

### Card

Component identification: [`one-card`](../../spec/component.md#one-card)

Card is UI block that displays:

  * Title
  * Facts list
  * Image (if [image url is present in the input data](../input_data/structure.md#image-url) and selected to be shown)

Facts are name-value pairs, where the `name` is AI generated and the `value` is gathered from agent's input data.
Value can be simple text or number etc. List (array) of values is supported as well.

Example rendering by Red Hat Design System for user prompt `Tell me details about Toy Story`:

![Card Data UI Block rendering by Red Hat Design System](../../img/data_ui_block_card.png "Card Data UI Block rendering by Red Hat Design System")

### Image

Component identification: [`image`](../../spec/component.md#image)

Image is UI block to display a single image with a title, based on [image url present in the input data](../input_data/structure.md#image-url).

Example rendering by Red Hat Design System for a prompt `Show me poster of Toy Story movie`:

![Image Data UI Block rendering by Red Hat Design System](../../img/data_ui_block_image.png "Image Data UI Block rendering by Red Hat Design System")

Image is found by agent from backend-data either by field value or by field name. See the [spec/component/image.schema.json](https://github.com/RedHat-UX/next-gen-ui-agent/blob/main/spec/component/image.schema.json) for more details.

### Video Player

Component identification: [`video-player`](../../spec/component.md#video-player)

Video player is UI block to play a single video from [video URL provided in the input data](../input_data/structure.md#video-url).

Title is also generated, and link pointing to the video cover image for YouTube videos is provided.

!!!warning
    Ability to play videos from video service url's (YouTube, Vimeo) or support for video file 
    formats (`avi`, `mpeg`, `mov`, ...) can vary in individual [UI renderers](../renderer/index.md)!

Example rendering by Red Hat Design System for a prompt `Play trailer of Toy Story movie`:

![Video Player Data UI Block rendering by Red Hat Design System](../../img/data_ui_block_video.jpg "Video Player Data UI Block rendering by Red Hat Design System")

## Components for [`Array of objects` input data](../input_data/structure.md#array-of-objects-input-data)

### Set Of Cards

Component identification: [`set-of-cards`](../../spec/component.md#set-of-cards)

Set of Card is UI block that displays:

  * Title
  * Set of multiple Card components, each showing the same list of facts

Facts are name-value pairs, where the `name` is AI generated and the `value` is gathered from agent's input data.
Value can be simple text or number etc. List (array) of values is supported as well.

Layout for this set of cards has to be provided by frontend application.

If enabled in the *UI Agent* configuration, [agent's output can contain list of all fields available in the input data](../../spec/output.md), so you can 
provide user with the ability to manually select what is shown after this UI component is generated.

### Table

Component identification: [`table`](../../spec/component.md#table)

Table is UI block that displays:

  * Title
  * Table with AI selected Columns with AI generated names, and rows of values gathered from agent's input data.

Individual cell value can be simple text or number etc. List (array) of values is supported as well.

If enabled in the *UI Agent* configuration, [agent's output can contain list of all fields available in the input data](../../spec/output.md), so you can 
provide user with the ability to manually select which columns are shown after this UI component is generated.
