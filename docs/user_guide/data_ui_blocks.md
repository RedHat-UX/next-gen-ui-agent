# Data UI Blocks

Next Gen UI Agent generates output and visualize them in Data UI Blocks.
This chapter list all available data blocks that the agent can generate and render.

## Card

Card is UI block that displays:

  * Title
  * Facts list
  * Image (if present)

Facts are name-value pairs, where the `name` is AI generated and the `value` is gathered from agent's input data.
Value can be simple text or number. List (array) of values is supported as well.

Example rendering by Red Hat Design System for user prompt `Tell me details about Toy Story`:

![Card Data UI Block rendering by Red Hat Design System](../img/data_ui_block_card.png "Card Data UI Block rendering by Red Hat Design System")

## Image

Image is UI block to display a single image with a title.

Example rendering by Red Hat Design System for a prompt `Show me poster of Toy Story movie`:

![Image Data UI Block rendering by Red Hat Design System](../img/data_ui_block_image.png "Image Data UI Block rendering by Red Hat Design System")
