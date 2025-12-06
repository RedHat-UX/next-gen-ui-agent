# Choose your framework

NextGenUI Agent mono repository offers a variety of options for you to align the agent to your environment needs. 
We took an approach where core implementation is agnostic to inference provider, [UI rendering plugin](guide/renderer/index.md) and [AI framework](guide/ai_apps_binding/index.md).
This way you have full flexibility in picking the right pieces and conveniently using it.

If any particular AI framework or UI rendering option is not available out of the box, it's easy to implement it and use with any other piece of the stack.

In the diagram below you can see each layer of NextGen UI Agent from which you need to pick the right piece for you. Each module not only 
mentions the dependency name but also internal python script where that particular functionality is implemented.
![NextGenUI modules](./img/ngui_modules.jpg "NextGenUI modules")

The repository organises the sources from the perspective of dependencies and usually you should align your choices to those to prevent unnecesary bloating 
of your dependency tree. However, you're free to choose any module from any row, so it's fine to use Llama-Stack Agent but inference from BeeAI even 
if it doesn't make too much sense.

Another diagram in a form of lines visualises how you can combine those modules into a package to use.
![Combining NextGenUI modules](./img/ngui_combining_modules.jpg "Combining NextGenUI modules")

A special oferring is our support for [Agent2Agent (A2A) Protocol](https://a2a-protocol.org/latest/) and [Model Context Protocol (MCP)](https://modelcontextprotocol.io). You can learn more about NextGenUI's A2A and MCP implementation specifics from their respective modules readmes [next_gen_ui_a2a](https://github.com/RedHat-UX/next-gen-ui-agent/tree/main/libs/next_gen_ui_a2a) and [next_gen_ui_mcp](https://github.com/RedHat-UX/next-gen-ui-agent/tree/main/libs/next_gen_ui_mcp). Here however, we'll concentrate on presenting the integration of the whole stack to run NextGenUI with support for those protocols.
![A2A and MCP support in NextGenUI](./img/ngui_mcp_a2a.jpg "A2A and MCP support in NextGenUI")
Looking from the top we have our AI protocols support and each of them exposes an endpoint compatible with the standard.
Next we have our set of renderers, by default we ship with JSON and Red Hat Design System renderers but you can easily add others.
Another step is our core logic of the NextGenUI where the main processing is happening.
Then we go into inference section where MCP Sampling is specific only to MCP server implementation but the other two represent the most common LLM inference APIs these days. One aligned with OpenAI format and second oferring Anthropic's VertexAI API that is compatible with Claude models. We intentionaly limited the choice of inference APIs as we wanted to provide a full and easy to use package that supports the most common scenarios. At the same time there is nothing limiting you from extending this implementation in case your case needs customisation.

Lastly, please consult our [Architecture guide](guide/architecture.md) and other guides for more details.