# Installation

NextGenUI Agent mono repository offers a variety of options for you to align the agent to your environment needs. We took an approach where core implementation is agnostic to inference provider, rendering plugins and agentic frameworks. This way you have full flexibility in picking the right pieces and conveniently using it.

If any particular agentic framework or rendering option is not available out of the box, it's easy to implement it and use with any other piece of the stack.

In the diagram below you can see each layer of NextGenUI from which you need to pick the right piece for you. Each component not only mentions the dependency name but also internal python script where that particular functionality is implemented.
![NextGenUI components](./img/ngui_components.png "NextGenUI components")

The repository organises the sources from the perspective of dependencies and usually you should align your choices to those to prevent unnecesary bloating of your dependency tree. However, you're free to choose any component from any row, so it's fine to use Llama-Stack Agent but inference from BeeAI even if it doesn't make too much sense.

Another diagram in a form of lines visualises how you can combine those components into a package to use.
![Combining NextGenUI components](./img/ngui_combining_components.png "Combining NextGenUI components")