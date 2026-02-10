# Calling LLM

[*UI Agent* core library](../ai_apps_binding/pythonlib.md) abstracts LLM inference over `InferenceBase` interface. 
Multiple implementations are provided in the core and different [AI Framework and protocols](../ai_apps_binding/index.md) bindings modules, 
including OpenAI compatible API, LlamaStack remote and embedded server, Anthropic/Claude models from proxied Google Vertex AI API etc.

Our MCP and A2A server default container images provide a configuration to use the most common providers over configuration, and 
also technology specific ways like MCP Sampling.

Additional providers can be easily implemented and used with the agent if necessary.

BTW, to get repeatable results from the UI agent, you should always use `temperature=0` when calling the LLM behind this interface!

