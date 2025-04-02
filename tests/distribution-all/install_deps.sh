pip install pytest
pip install pytest-asyncio

echo UNINSTALLING all existing packages
pip uninstall -y next_gen_ui_agent
pip uninstall -y next_gen_ui_langgraph
pip uninstall -y next_gen_ui_llama_stack
pip uninstall -y next_gen_ui_rhds_renderer
pip uninstall -y next_gen_ui_patternfly_renderer
pip uninstall -y next_gen_ui_testing

echo INSTALLING all packages
pip install ../../dist/next_gen_ui_*.whl
