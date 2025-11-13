## 0.3.0 (2025-11-07)

### Feat

- **[NGUI-444](https://issues.redhat.com/browse/NGUI-444)**: Added field ID to data_field object, spec schemas updated [24404](https://github.com//RedHat-UX/next-gen-ui-agent/commit/244046472e40af9b2e52d4c7ec40de30c059b915)
- **[NGUI-451](https://issues.redhat.com/browse/NGUI-451)**: LangGraph Agent updated to new core agent API, error handling improved (#214) [1a332](https://github.com//RedHat-UX/next-gen-ui-agent/commit/1a3327d3baf4a7e20ad7c4e92d975bc2f4bdbe38)
- **[NGUI-472](https://issues.redhat.com/browse/NGUI-472)**: Marking MCP server as supported and fastmcp version 2.12.5 [75c03](https://github.com//RedHat-UX/next-gen-ui-agent/commit/75c037c66fab6c7f2e97a5fbdcae4f370981bf2b)
- **[NGUI-453](https://issues.redhat.com/browse/NGUI-453)**: MCP refactoring to use new agent API and improved error handling [4b214](https://github.com//RedHat-UX/next-gen-ui-agent/commit/4b214579604872e4ccfa74c2d3246b146ad9a388)
- **[NGUI-455](https://issues.redhat.com/browse/NGUI-455)**: ACP Agent - deprecated, new core agent API used to improve error handling (#212) [267c5](https://github.com//RedHat-UX/next-gen-ui-agent/commit/267c56d764410e95d692ba593c75aaa916e9a79e)
- **[NGUI-452](https://issues.redhat.com/browse/NGUI-452)**: LlamaStack Agent - new core agent API used to improve error handling and parallel processing with immediate result return [9d12b](https://github.com//RedHat-UX/next-gen-ui-agent/commit/9d12b7a330f01b16c7befa27cd91a4b1e2c58b7d)
- **[NGUI-450](https://issues.redhat.com/browse/NGUI-450)**: core agent API refactoring for better error handling  (#205) [dddc0](https://github.com//RedHat-UX/next-gen-ui-agent/commit/dddc00f583dc40fbbbd27c22a0cdfeac0866614b)
- **[NGUI-425](https://issues.redhat.com/browse/NGUI-425)**: data refresh - support in the core agent (#204) [4f3a6](https://github.com//RedHat-UX/next-gen-ui-agent/commit/4f3a655bd6ea460331e2cdfebe982b0c3086ac94)
- **[NGUI-426](https://issues.redhat.com/browse/NGUI-426)**: Return component configuration in MCP tools [7d5ed](https://github.com//RedHat-UX/next-gen-ui-agent/commit/7d5edb36586d72c92149c3dcbcf495c64a876d14)
- **[NGUI-432](https://issues.redhat.com/browse/NGUI-432)**: Support structured data and LLM handled data in MCP [9638a](https://github.com//RedHat-UX/next-gen-ui-agent/commit/9638aad3acada0b984adc6250384f539a16ae07a)
- **[NGUI-398](https://issues.redhat.com/browse/NGUI-398)**: Structured result and summary in MCP, documentation (#195) [057ac](https://github.com//RedHat-UX/next-gen-ui-agent/commit/057ac9735a8cd5722fad5c0309b931a4d8efca51)
- **[NGUI-356](https://issues.redhat.com/browse/NGUI-356)**: Fixed Width Columns Table input data transformer (#194) [5f7e4](https://github.com//RedHat-UX/next-gen-ui-agent/commit/5f7e4ef4129102fd43ac3d8b646f39c8881e629e)
- **[NGUI-407](https://issues.redhat.com/browse/NGUI-407)**: `noop` input datat transformer (#193) [8c603](https://github.com//RedHat-UX/next-gen-ui-agent/commit/8c603b7db5012aaa0b968b78bc631360b3033ce5)
- **[NGUI-405](https://issues.redhat.com/browse/NGUI-405)**: added ability to configure default input data transformer (#192) [521bf](https://github.com//RedHat-UX/next-gen-ui-agent/commit/521bf6235568faa9fe8686dda6b82a26ac28df08)
- **[NGUI-391](https://issues.redhat.com/browse/NGUI-391)**: csv input data transformers (#191) [9abba](https://github.com//RedHat-UX/next-gen-ui-agent/commit/9abbaf12f275eeabc3c945fe18b69bcdd45a86be)
- **[NGUI-397](https://issues.redhat.com/browse/NGUI-397)**: excluding input_data in MCP tool call (#189) [0c8bf](https://github.com//RedHat-UX/next-gen-ui-agent/commit/0c8bf741904b2612c0d350993c1c048b367b48d6)
- **[NGUI-394](https://issues.redhat.com/browse/NGUI-394)**: configuration schema improved for "enum" like options (#190) [41211](https://github.com//RedHat-UX/next-gen-ui-agent/commit/412111202f50509effbc5acf34f2fd1596724ee3)
- **[NGUI-396](https://issues.redhat.com/browse/NGUI-396)**: Migrate MCP from MCP SDK to FastMCP to get extra features, tests improved [93409](https://github.com//RedHat-UX/next-gen-ui-agent/commit/93409c9336dcbc2933b5761b11f5faf3f0eac98f)
- **[NGUI-364](https://issues.redhat.com/browse/NGUI-364)**: use dynamic component with pre-defined configuration per data type (#183) [ff693](https://github.com//RedHat-UX/next-gen-ui-agent/commit/ff69353ceadd47341111ca4da32dfa874325d39b)
- **[NGUI-362](https://issues.redhat.com/browse/NGUI-362)**: MCP YAML file config support and support for multiple YAML files [b2cb3](https://github.com//RedHat-UX/next-gen-ui-agent/commit/b2cb3f6159ad9d99f44da3bc194d50870d832002)
- **[NGUI-377](https://issues.redhat.com/browse/NGUI-377)**: Openshift deployment yaml (#182) [536f3](https://github.com//RedHat-UX/next-gen-ui-agent/commit/536f3fe4bc451ad2d71ef21597df1ea12d7288b4)
- **[NGUI-330](https://issues.redhat.com/browse/NGUI-330)**: Split ngui-e2e architecture and update deployment strategy (#166) [8ab26](https://github.com//RedHat-UX/next-gen-ui-agent/commit/8ab26afb7a45df9f9c9a46dbdad2e1498c3b6b30)
- **[NGUI-355](https://issues.redhat.com/browse/NGUI-355)**: input data transformation framework and yaml transformer [79d98](https://github.com//RedHat-UX/next-gen-ui-agent/commit/79d98ab15c091aee6dc029cdaad606a28150ab3f)
- **[NGUI-374](https://issues.redhat.com/browse/NGUI-374)**: MCP tool description improvements (#180) [09edc](https://github.com//RedHat-UX/next-gen-ui-agent/commit/09edc0a8e1f6f4eb7419e89c0402cfe7ae666d4e)
- **[NGUI-380](https://issues.redhat.com/browse/NGUI-380)**: table and set-of-cards json spec exported and documented [0e138](https://github.com//RedHat-UX/next-gen-ui-agent/commit/0e13839ede3d3cbb1be9c46d86a12397765991d2)
- **[NGUI-354](https://issues.redhat.com/browse/NGUI-354)**: wrapping of the json input data with problematic structure for LLM processing [f33d9](https://github.com//RedHat-UX/next-gen-ui-agent/commit/f33d9edfa345bbee8fb55cf67675acc75dcdc9c1)

### Fix

- **[NGUI-475](https://issues.redhat.com/browse/NGUI-475)**: Improved VERSION number generation script. [edc3d](https://github.com//RedHat-UX/next-gen-ui-agent/commit/edc3de3d7a75d07307fc3233f34cad80e98c1ee2)
- data passing to the data transformation step patched in eval script (#201) [645d7](https://github.com//RedHat-UX/next-gen-ui-agent/commit/645d73ada0101d8b25e987359ad2167b2e3946fa)
- **[NGUI-395](https://issues.redhat.com/browse/NGUI-395)**: Fix wrapping for not HBC components [00256](https://github.com//RedHat-UX/next-gen-ui-agent/commit/00256374ed2024373cf8e221bc7605ec1020edd4)
- **[NGUI-387](https://issues.redhat.com/browse/NGUI-387)**: Raise an exception on error in MCP (#179) [b5486](https://github.com//RedHat-UX/next-gen-ui-agent/commit/b5486cbf655466afda10cf4e3df53c90725039e3)
- **[NGUI-386](https://issues.redhat.com/browse/NGUI-386)**: Improve pytest configuration to fail on unknown marker and fix missing deps (#178) [5fc8f](https://github.com//RedHat-UX/next-gen-ui-agent/commit/5fc8f20a6d9d48e07a96acb84f496b02a1ea0dd4)

### Refactor

- **[NGUI-428](https://issues.redhat.com/browse/NGUI-428)**: spec schema separated from tests [88a1d](https://github.com//RedHat-UX/next-gen-ui-agent/commit/88a1d4318eaff958655e61876bf67ec4fbc081ab)

## 0.2.2 (2025-09-30)

### Feat

- **[NGUI-376](https://issues.redhat.com/browse/NGUI-376)**: MCP readiness and liveness health checks (#173) [02285](https://github.com//RedHat-UX/next-gen-ui-agent/commit/022859a80038b63180de8068d22ffd18597b0b1c)
- **[NGUI-370](https://issues.redhat.com/browse/NGUI-370)**: MCP Container, documentation, image build in pipeline (#172) [86607](https://github.com//RedHat-UX/next-gen-ui-agent/commit/866071427e847d8d42811d501e235c70d3f8276f)
- LLM output sanitization when </think> is present, Qwen3 14B evaluation results [53f75](https://github.com//RedHat-UX/next-gen-ui-agent/commit/53f7578f81044642f55ec36dad22da5d6c36cbab)

## 0.2.1 (2025-09-26)

### Feat

- add metadata file for backstage (#168) [df7a2](https://github.com//RedHat-UX/next-gen-ui-agent/commit/df7a27a26264df9d0cf35fe975debbd9b32fc117)

### Fix

- core package links fixed [c3307](https://github.com//RedHat-UX/next-gen-ui-agent/commit/c3307593552f4c979721f6273fdfc1ffc06be248)

## 0.2.0 (2025-09-25)

### Feat

- **[NGUI-361](https://issues.redhat.com/browse/NGUI-361)**: Agent YAML file configuration (#169) [4d2eb](https://github.com//RedHat-UX/next-gen-ui-agent/commit/4d2ebb0f8ed84831b1a6188e5887db59ed451cd0)
- **[NGUI-220](https://issues.redhat.com/browse/NGUI-220)**: MCP integration and standalone MCP server (#136) [76229](https://github.com//RedHat-UX/next-gen-ui-agent/commit/76229736617c4ba2bee15e37113329c4f0d29466)
- **[NGUI-344](https://issues.redhat.com/browse/NGUI-344)**: LlamaStack version 0.2.20 and dropping Python 3.11 support (#162) [4a29f](https://github.com//RedHat-UX/next-gen-ui-agent/commit/4a29fe75de47a34b1b185bf43d424d80c54a9afc)
- use Apache; copy root LICENSE in prepack script [d6a4c](https://github.com//RedHat-UX/next-gen-ui-agent/commit/d6a4cb51cfaa0a86aff5fe009da5e402e9a35d46)
- add MIT license [df3d1](https://github.com//RedHat-UX/next-gen-ui-agent/commit/df3d1644ef28ffab365eb2e4712814794605ff35)
- next_gen_ui_llama_stack_embedded module added [374c4](https://github.com//RedHat-UX/next-gen-ui-agent/commit/374c42b66e8a9b00b62828a6dfdd33547fe021a8)
- **[NGUI-320](https://issues.redhat.com/browse/NGUI-320)**: add GH action to run next_gen_ui_react tests (#158) [c7bf4](https://github.com//RedHat-UX/next-gen-ui-agent/commit/c7bf4e2dfac3025082d9c1a23fa8bf7bdc85e931)
- HBC - changed representation passed to renderer to accomodate other types of pluggable components in the future [7a925](https://github.com//RedHat-UX/next-gen-ui-agent/commit/7a92580e31d7ab7a9857852fd553fbf71129bf54)
- **[NGUI-274](https://issues.redhat.com/browse/NGUI-274)**: patternfly end-to-end app (#147) [bb37d](https://github.com//RedHat-UX/next-gen-ui-agent/commit/bb37d3b5a316b12a010d95b87d737991b0a4dc46)
- HBC mapped selection in LlamaStack agent based on tool_name [7be74](https://github.com//RedHat-UX/next-gen-ui-agent/commit/7be74a89ae47e19966b6b8de3e354338101c7b00)
- HBC selection based on requested component type [e73bc](https://github.com//RedHat-UX/next-gen-ui-agent/commit/e73bcbca161dc8ff122093e2b7df1d1f684f1130)
- HBC selection implemented in Agent's component_selection method [6a36c](https://github.com//RedHat-UX/next-gen-ui-agent/commit/6a36c9067acd7588e6fd3274ceba4967882212d5)
- HBC data transformation and json renderer [3aef9](https://github.com//RedHat-UX/next-gen-ui-agent/commit/3aef9008962b4408f79b8bd428d0a6f1572b7a70)
- HBC component registration and basic method for its selection in Agent [9679e](https://github.com//RedHat-UX/next-gen-ui-agent/commit/9679e18d5eec98cf605b745e333c775bdebfc176)
- **[NGUI-231](https://issues.redhat.com/browse/NGUI-231)**: Improved dependency management by pants Dependency inference [36d67](https://github.com//RedHat-UX/next-gen-ui-agent/commit/36d67f93e430c4728735af83594f6b98590995ad)
- **[evals](https://issues.redhat.com/browse/evals)**: long model response times from API throttling are omitted from perf stats [59658](https://github.com//RedHat-UX/next-gen-ui-agent/commit/596588d5519afb4bbc22b6bdf04a8db1fac41143)
- evals improved to report not enough data in array component (indicating invalid data_path) [e45f5](https://github.com//RedHat-UX/next-gen-ui-agent/commit/e45f5cb59659e1f8d013447fcf027b07156330ad)
- ComponentData JSON contains sanitized data_path now [80bf1](https://github.com//RedHat-UX/next-gen-ui-agent/commit/80bf1b1e0c9bb01edb41a704c7b8fa490b722644)
- added trimming of characters before and after JSON in LLM inference output [9d02c](https://github.com//RedHat-UX/next-gen-ui-agent/commit/9d02c0d70f346fc551f51981477225398e91f5ff)
- configurable embedded LlamaStack in evals. LlamaStack version upgraded. [4d9b1](https://github.com//RedHat-UX/next-gen-ui-agent/commit/4d9b15cbc53f5e3c216041a76cbf11e97fb81d72)
- **[NGUI-244](https://issues.redhat.com/browse/NGUI-244)**: implemented component selection strategy abstraction in the NextGenUIAgent to make it switchable [84e49](https://github.com//RedHat-UX/next-gen-ui-agent/commit/84e49d2d6b88da8ce6f4f25b76f8d48c31a6a5fa)

### Fix

- updated the wrong gitignore [e13c7](https://github.com//RedHat-UX/next-gen-ui-agent/commit/e13c77102eda27456949dfda4d4bc5790c9b1bfb)
- HBC test compatibility fixed [c586a](https://github.com//RedHat-UX/next-gen-ui-agent/commit/c586a402c92437fdb841c807a2fe6347b8e072be)
- **[NGUI-274](https://issues.redhat.com/browse/NGUI-274)**: Resolve installation issues in ngui-e2e app (#150) [eb257](https://github.com//RedHat-UX/next-gen-ui-agent/commit/eb257aea6c364c1511a8c8596c768e7e24468766)
- improved data_path sanitization for fields referenced by ['field'] [c02eb](https://github.com//RedHat-UX/next-gen-ui-agent/commit/c02ebfc9bbf197cf863f0f778999f9d5876c9209)
- patched value pickup for one kind of paths for "object in array in the root" backend data [01f2f](https://github.com//RedHat-UX/next-gen-ui-agent/commit/01f2fe6a325b9386b5566035ddbdd3992992f3de)
- patched boolean 'false' value pickup from backend data [10fe9](https://github.com//RedHat-UX/next-gen-ui-agent/commit/10fe976fcc3d87474f6cf858a7113376bdf71b69)

### Refactor

- **[NGUI-344](https://issues.redhat.com/browse/NGUI-344)**: Python 3.12 used in GH actions (#165) [10390](https://github.com//RedHat-UX/next-gen-ui-agent/commit/10390667c325f519772d38d8438d32f9c7aae4ed)
- **[NGUI-322](https://issues.redhat.com/browse/NGUI-322)**: remove components not part of NGUI agent spec (#155) [aa042](https://github.com//RedHat-UX/next-gen-ui-agent/commit/aa0424fe03eaef94a879d50455d2a5d161eec2e8)

## 0.1.1 (2025-07-23)

### Feat

- **[NGUI-256](https://issues.redhat.com/browse/NGUI-256)**: Add search plugin to docs [857ac](https://github.com//RedHat-UX/next-gen-ui-agent/commit/857acb0dcba7c817ccf47ab77177487d105d454c)
- **[NGUI-255](https://issues.redhat.com/browse/NGUI-255)**: Add Changelog and spec and llama-stack to docs [62f4e](https://github.com//RedHat-UX/next-gen-ui-agent/commit/62f4ea03d9a17ccff3b9160e4212a4022d6ac1ed)
- **[NGUI-241](https://issues.redhat.com/browse/NGUI-241)**: Publish docs to github pages [a89e7](https://github.com//RedHat-UX/next-gen-ui-agent/commit/a89e7208347863312501d046e0249d713227b82d)

## 0.1.0 (2025-07-22)

### Feat

- **[NGUI-158](https://issues.redhat.com/browse/NGUI-158)**: React JS One card component (#130) [a82b9](https://github.com//RedHat-UX/next-gen-ui-agent/commit/a82b938c63084b2950d692d24c8c73ce4df7a8d6)
- **[NGUI-97](https://issues.redhat.com/browse/NGUI-97)**: Quickstart langgraph movies & ngui agents app (#131) [f3aef](https://github.com//RedHat-UX/next-gen-ui-agent/commit/f3aefc9e8c9dbf2c5c14fc704d9fbb08e4afbff2)
- implemented warn only items in evaluation dataset, which run only when requested, and report problems into WARN item instead of error [fc5d7](https://github.com//RedHat-UX/next-gen-ui-agent/commit/fc5d76fda0b4739e56eca13b7eb394edd1fc2734)
- **[NGUI-227](https://issues.redhat.com/browse/NGUI-227)**: implemented switching of components available in LLM syste prompt (supported only or all), removed unimplemented chart components [1e4e5](https://github.com//RedHat-UX/next-gen-ui-agent/commit/1e4e5f955d66ea328b0e0aa5027abda06119f619)
- **[NGUI-227](https://issues.redhat.com/browse/NGUI-227)**: evaluations run only for implemented/supported UI components by default [5044a](https://github.com//RedHat-UX/next-gen-ui-agent/commit/5044ade1973d2abf4c5b52614d61ebd679d4c13f)
- **[NGUI-229](https://issues.redhat.com/browse/NGUI-229)**: Support python version 3.11, 3.12, 3.13 [384f6](https://github.com//RedHat-UX/next-gen-ui-agent/commit/384f6bf3573011bdea89157263de6de4e95d50b2)
- **[NGUI-218](https://issues.redhat.com/browse/NGUI-218)**: github tests for python versions 3.11, 3.12, 3.13 (#122) [56da8](https://github.com//RedHat-UX/next-gen-ui-agent/commit/56da8ecd4ab8015f95af3a68ec7867226ce64f8b)
- **[NGUI-91](https://issues.redhat.com/browse/NGUI-91)**: Video transformation improvements [098f8](https://github.com//RedHat-UX/next-gen-ui-agent/commit/098f880287db1d2a3ca0ddb08a5d538c419557fc)
- **[NGUI-113](https://issues.redhat.com/browse/NGUI-113)**: data transformation fully updated to use nev componentized system, and covered with tests [60c25](https://github.com//RedHat-UX/next-gen-ui-agent/commit/60c253afd996915c77d4256352936063f002dbf9)
- **[NGUI-170](https://issues.redhat.com/browse/NGUI-170)**: ACP Agent PoC, BeeAI inference [71468](https://github.com//RedHat-UX/next-gen-ui-agent/commit/71468960092bfc12254a5fd9a398e737f364e3f5)
- **[NGUI-150](https://issues.redhat.com/browse/NGUI-150)**: Patternfly v6 migration (#117) [2c952](https://github.com//RedHat-UX/next-gen-ui-agent/commit/2c9529084dd36cfbfd927395d92fb5a04efd48c7)
- **[NGUI-166](https://issues.redhat.com/browse/NGUI-166)**: Video component JSON Schema spec CustomGenerateJsonSchema moved to separate file import transformers improved [424b4](https://github.com//RedHat-UX/next-gen-ui-agent/commit/424b42e7972522b0586db01875852834d0484d97)
- **[NGUI-165](https://issues.redhat.com/browse/NGUI-165)**: RHDS video-player rendering [4dd9d](https://github.com//RedHat-UX/next-gen-ui-agent/commit/4dd9df019a4bebefdbaf3aec59599576683d06a3)
- **[NGUI-113](https://issues.redhat.com/browse/NGUI-113)**: data transformation modularized, relevant code moved here from renderer [9e15c](https://github.com//RedHat-UX/next-gen-ui-agent/commit/9e15cb24899577bf4b99da46524e724b508c41c7)
- **[NGUI-113](https://issues.redhat.com/browse/NGUI-113)**: NextGenUIAgent.design_system_handler method returns specific object [e7a00](https://github.com//RedHat-UX/next-gen-ui-agent/commit/e7a00f0767dc3e8d4bd1f3e1a8d2cad6723e3cc0)
- **[NGUI-154](https://issues.redhat.com/browse/NGUI-154)**: component name in rendering context as literals [97381](https://github.com//RedHat-UX/next-gen-ui-agent/commit/9738161a1be011ed38aaaf7b4b956857ecef4977)
- **[NGUI-104](https://issues.redhat.com/browse/NGUI-104)**: LLM response JSON validation [5cd5a](https://github.com//RedHat-UX/next-gen-ui-agent/commit/5cd5aa8a3d07574ab5a22bf976adfffc584e2a0d)
- **[NGUI-105](https://issues.redhat.com/browse/NGUI-105)**: llama stack integration changed, now uses inference API [0d00c](https://github.com//RedHat-UX/next-gen-ui-agent/commit/0d00cd5c16dd9914b169c57ef8bfba879e4ef047)
- **[NGUI-86](https://issues.redhat.com/browse/NGUI-86)**: image handling improvements [3330c](https://github.com//RedHat-UX/next-gen-ui-agent/commit/3330c53da347a0709c8c4b1e9ca2571cc177db92)
- **[NGUI-148](https://issues.redhat.com/browse/NGUI-148)**: Image component JSON Schema, added RenderContextBaseTitle [ce26f](https://github.com//RedHat-UX/next-gen-ui-agent/commit/ce26fb87c49a39a195572129380430a410f521d2)
- **[NGUI-143](https://issues.redhat.com/browse/NGUI-143)**: Image component RHDS rendering [47472](https://github.com//RedHat-UX/next-gen-ui-agent/commit/47472417d7540771da8748f26be089e52747a0b6)
- **[NGUI-136](https://issues.redhat.com/browse/NGUI-136)**: streamlit gui improvements - show input and llm mocked data [4791c](https://github.com//RedHat-UX/next-gen-ui-agent/commit/4791ca6b225254042525085044f24382a12f4b59)
- **[NGUI-139](https://issues.redhat.com/browse/NGUI-139)**: Apply new RHDS design pattern guideline to one-card [e6240](https://github.com//RedHat-UX/next-gen-ui-agent/commit/e62408c44593d115aadf08119f3daf0a011c3332)
- **[NGUI-126](https://issues.redhat.com/browse/NGUI-126)**: NextGen UI NPM React Package (#93) [888d0](https://github.com//RedHat-UX/next-gen-ui-agent/commit/888d0f170fc1882dbdfe8a5e27823ef9f65bf5b7)
- **[NGUI-129](https://issues.redhat.com/browse/NGUI-129)**: data transformation for array and objects [dc4ae](https://github.com//RedHat-UX/next-gen-ui-agent/commit/dc4aea152ac923fe35063153cc0b7eb53e2d5aaa)
- **[NGUI-133](https://issues.redhat.com/browse/NGUI-133)**: JSON Schema for one-card component [b807e](https://github.com//RedHat-UX/next-gen-ui-agent/commit/b807eb315aa63063ffa95431ee787578c2a82e2a)
- **[NGUI-137](https://issues.redhat.com/browse/NGUI-137)**: added Architecture chapter of the User Guide [80290](https://github.com//RedHat-UX/next-gen-ui-agent/commit/802906dcfa5b963f892ba1f351fdf7ba26a0da5b)
- **[NGUI-137](https://issues.redhat.com/browse/NGUI-137)**: added Input Data chapter of the User Guide [3b65a](https://github.com//RedHat-UX/next-gen-ui-agent/commit/3b65af054eb6f904c9c9d480b37546d0eac54058)
- **[NGUI-113](https://issues.redhat.com/browse/NGUI-113)**: data transformation patch for occassional LLM error [03eb6](https://github.com//RedHat-UX/next-gen-ui-agent/commit/03eb6e209b0ab60acdd7517ba04e4fe1c510805f)
- **[NGUI-136](https://issues.redhat.com/browse/NGUI-136)**: Streamlit demo app with one-card and dev console [677b8](https://github.com//RedHat-UX/next-gen-ui-agent/commit/677b89f09dda91ea8fb1fad26857d42fc36c75c1)
- **[NGUI-120](https://issues.redhat.com/browse/NGUI-120)**: Improved gui streamlit app to be Developer Console [196e6](https://github.com//RedHat-UX/next-gen-ui-agent/commit/196e64f57c2d9902a470b86bac7f31c8f2a02d30)
- **[NGUI-118](https://issues.redhat.com/browse/NGUI-118)**: RHDS One Card component with support of image [e0ffe](https://github.com//RedHat-UX/next-gen-ui-agent/commit/e0ffeea257ea2c8a11bea25cf695323ce0f1a56e)
- Streamlit test GUI supports editing mocked data [78547](https://github.com//RedHat-UX/next-gen-ui-agent/commit/785472847685b168195b0857507cabeeb8dab558)
- **[NGUI-130](https://issues.redhat.com/browse/NGUI-130)**: Improved Streamlit GUI to correctly render RHDS [ea08c](https://github.com//RedHat-UX/next-gen-ui-agent/commit/ea08c74a94d3e30cd4a917fa4afdad5ab5f7f0f3)
- **[NGUI-15](https://issues.redhat.com/browse/NGUI-15)**: first set of evals implemented [c03d6](https://github.com//RedHat-UX/next-gen-ui-agent/commit/c03d690e5b9b0195c05e907cea7bb959a71c17f5)
- **[NGUI-52](https://issues.redhat.com/browse/NGUI-52)**: Pluggable tests (#79) [05e05](https://github.com//RedHat-UX/next-gen-ui-agent/commit/05e059cde666a6ab661cef5981c429552ab7dee2)
- **[NGUI-120](https://issues.redhat.com/browse/NGUI-120)**: Streamlit GUI app for agent testing [4cf81](https://github.com//RedHat-UX/next-gen-ui-agent/commit/4cf8161ac33f24f773f8e953bf8b34e5f02ff25e)
- **[NGUI-109](https://issues.redhat.com/browse/NGUI-109)**: evaluation dataset generation implemented [4966e](https://github.com//RedHat-UX/next-gen-ui-agent/commit/4966e96ff67e38d8269393f3322eb379bae900e5)
- **[NGUI-81](https://issues.redhat.com/browse/NGUI-81)**: One Card test coverage, RenderStrategyBase improvements [95713](https://github.com//RedHat-UX/next-gen-ui-agent/commit/95713e0e8f15aa5bf6962d21d01a0cf0c57cee1d)
- **[NGUI-14](https://issues.redhat.com/browse/NGUI-14)**: Added base for the evaluation of the AI component selection functionality [fe473](https://github.com//RedHat-UX/next-gen-ui-agent/commit/fe473d0bc9fe2b769607b6c45155f72942d2f533)
- **[NGUI-114](https://issues.redhat.com/browse/NGUI-114)**: VS Code settings improvements for auto complet, default interepreter [4a4cd](https://github.com//RedHat-UX/next-gen-ui-agent/commit/4a4cd5b9846c719e5c47380e9b20e4e382508971)
- **[NGUI-112](https://issues.redhat.com/browse/NGUI-112)**: Support Py Test in VS Code [327a6](https://github.com//RedHat-UX/next-gen-ui-agent/commit/327a626b23be9747942e8f9929fc52b6f27fe903)
- **[NGUI-26](https://issues.redhat.com/browse/NGUI-26)**: Agent Config improvements [f972c](https://github.com//RedHat-UX/next-gen-ui-agent/commit/f972c029bd646269833f7f6ea3ccc6f949ffe66a)
- **[NGUI-68](https://issues.redhat.com/browse/NGUI-68)**: publishing next_gen_ui_testing package [00fa6](https://github.com//RedHat-UX/next-gen-ui-agent/commit/00fa6e61ffb73892f41e527ae1d46683cbef4260)
- **[NGUI-67](https://issues.redhat.com/browse/NGUI-67)**: AsyncLlamaStackClient support, rendering event [15b22](https://github.com//RedHat-UX/next-gen-ui-agent/commit/15b2262f564f41435735458d919731ad3e6a3165)
- **[NGUI-66](https://issues.redhat.com/browse/NGUI-66)**: better pip deps caching in pipeline (#61) [28da2](https://github.com//RedHat-UX/next-gen-ui-agent/commit/28da2b3b0420f3a1dd0886e4179b93dac3925f6a)
- **[NGUI-38](https://issues.redhat.com/browse/NGUI-38)**: Pipeline version bump & publish to (test) repository (#60) [f9c55](https://github.com//RedHat-UX/next-gen-ui-agent/commit/f9c551129e4dbdfa58488a92da289c2b75defdd8)
- **[NGUI-25](https://issues.redhat.com/browse/NGUI-25)**: Apache 2.0 License [b47a0](https://github.com//RedHat-UX/next-gen-ui-agent/commit/b47a07ab7b28e7b64309e20dde1c6a9724c7097a)

### Fix

- patched eval script to correctly handle -w argument [3ad4a](https://github.com//RedHat-UX/next-gen-ui-agent/commit/3ad4abd2c223e5db220ac887fb10eaa1e75ce21a)
- **[NGUI-153](https://issues.redhat.com/browse/NGUI-153)**: python interpreter version 3.11 [aa091](https://github.com//RedHat-UX/next-gen-ui-agent/commit/aa091348db0ae835afa382c64815f14ee3e4df4a)
- **[NGUI-117](https://issues.redhat.com/browse/NGUI-117)**: adding range to llama-stack-client to llama-stack-client>=0.1.9,<=0.2.7 [d4b2f](https://github.com//RedHat-UX/next-gen-ui-agent/commit/d4b2f90ef44b76eb7d80740dbc9f56bba78fa0ce)
- **[NGUI-117](https://issues.redhat.com/browse/NGUI-117)**: llama-stack-client constraint for distribution tests [e42b7](https://github.com//RedHat-UX/next-gen-ui-agent/commit/e42b7765afc247261e83bd72892204118b9a7379)
- **[NGUI-117](https://issues.redhat.com/browse/NGUI-117)**: Relaxed dependency on  llama-stack-client to >=0.1.9 but pinned version to 0.1.9 in lock file [0ab36](https://github.com//RedHat-UX/next-gen-ui-agent/commit/0ab36568080a9d1c2243f5d339a0ada46da61094)
- **[NGUI-117](https://issues.redhat.com/browse/NGUI-117)**: correct tests exclusion from the sources [ae4de](https://github.com//RedHat-UX/next-gen-ui-agent/commit/ae4de87ce3f2194eb2842e16b1a87ffe47f25bce)
- **[NGUI-162](https://issues.redhat.com/browse/NGUI-162)**: Fixing commitizen version to 4.6.3 this ensures compatibility with cz_github_jira_conventional [45cde](https://github.com//RedHat-UX/next-gen-ui-agent/commit/45cdee07b2d8c0908ee72a01b7fb24cfb3e61abc)
- **[NGUI-157](https://issues.redhat.com/browse/NGUI-157)**: workaround auto-height feature test gui-streamlit app in firefox [97bb3](https://github.com//RedHat-UX/next-gen-ui-agent/commit/97bb3c6132ee029587a822c7623c81f5961a09e4)
- **[NGUI-123](https://issues.redhat.com/browse/NGUI-123)**: ai_eval_components module patched for Pydantic and tests improved [92d16](https://github.com//RedHat-UX/next-gen-ui-agent/commit/92d16e18038cfb81ce959277068e1fb9d682be41)
- correct handling of datetime type [e21d3](https://github.com//RedHat-UX/next-gen-ui-agent/commit/e21d3671dec8293fa8e2c014819843c857291175)
- exception handling in eval.py [03b40](https://github.com//RedHat-UX/next-gen-ui-agent/commit/03b40242e07fe640aeb9d33e8d918fe505447405)
- docs improved, eval updated to granite3.2:2b default model [d97d4](https://github.com//RedHat-UX/next-gen-ui-agent/commit/d97d47d3d25418048d81687638d8487bc1438752)
- **[NGUI-122](https://issues.redhat.com/browse/NGUI-122)**: Do not run same github actions in pipeline [9e721](https://github.com//RedHat-UX/next-gen-ui-agent/commit/9e721b9315640c83afc23880caff4821a566eeff)
- **[NGUI-56](https://issues.redhat.com/browse/NGUI-56)**: removing pprint and using logger.debug in langgraph [22f86](https://github.com//RedHat-UX/next-gen-ui-agent/commit/22f86fcb9829c733a0c9c520933c49311eb977ea)
- updates for llama-stack development [ef207](https://github.com//RedHat-UX/next-gen-ui-agent/commit/ef207665e5c334ea2c5712999dcd2e9364231eb2)

### Refactor

- **[NGUI-107](https://issues.redhat.com/browse/NGUI-107)**: Repository cleanup [47724](https://github.com//RedHat-UX/next-gen-ui-agent/commit/477246856e05fc5d85c6de40031ef143436b3017)
- refactor to use dl instad of ul in one-card [0e347](https://github.com//RedHat-UX/next-gen-ui-agent/commit/0e34705ee107f6d0d7b7d2ee33127a01380cb769)
- improved eval tests ty be covered by MyPy [da334](https://github.com//RedHat-UX/next-gen-ui-agent/commit/da3344070484bf900ee9b58dc5288e224b03c87f)
- **[NGUI-123](https://issues.redhat.com/browse/NGUI-123)**: Use Pydantic to support json schema [49c34](https://github.com//RedHat-UX/next-gen-ui-agent/commit/49c349a3b4c6847ef87d05ef474e1578eeaf7364)
- **[NGUI-115](https://issues.redhat.com/browse/NGUI-115)**: Move each component strategy to separate file [d6c41](https://github.com//RedHat-UX/next-gen-ui-agent/commit/d6c4156a44f40d7c7e48edb567f199d23e0ab58e)
- **[NGUI-102](https://issues.redhat.com/browse/NGUI-102)**: base renderer refactoring - TypeDict [8021c](https://github.com//RedHat-UX/next-gen-ui-agent/commit/8021cd46ac2262372165bf052c9485d6a7674798)
- **[NGUI-108](https://issues.redhat.com/browse/NGUI-108)**: pants-fmt disabled from pre-commit [1f37e](https://github.com//RedHat-UX/next-gen-ui-agent/commit/1f37e2a24f20d28191a2b23a80dc809cff75f269)
- added method is_next_gen_ui_message in LangGraph [fb756](https://github.com//RedHat-UX/next-gen-ui-agent/commit/fb756d8752d624dab8ce58717eb6fc5d15b1652a)
- **[NGUI-63](https://issues.redhat.com/browse/NGUI-63)**: Details from pyproject.toml migrated to BUILD [2e563](https://github.com//RedHat-UX/next-gen-ui-agent/commit/2e563e819e9f3baf4fa41ce8b50f5213a5be2f26)
- **[NGUI-48](https://issues.redhat.com/browse/NGUI-48)**: pants pre-commit [f04db](https://github.com//RedHat-UX/next-gen-ui-agent/commit/f04db7b160fb65a284fd2b9c665273911f030f1a)
- **[NGUI-51](https://issues.redhat.com/browse/NGUI-51)**: added commitizen, pre-commit hook [0c9d7](https://github.com//RedHat-UX/next-gen-ui-agent/commit/0c9d7dae040e3a4c89643790d1a6251b17ac2e91)
