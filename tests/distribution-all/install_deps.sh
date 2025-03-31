pip install pytest
pip install pytest-asyncio

echo Uninstalling all existing packages
pip uninstall -y ../../dist/next_gen_ui_agent-0.0.1-py3-none-any.whl
pip uninstall -y ../../dist/next_gen_ui_langgraph-0.0.1-py3-none-any.whl
pip uninstall -y ../../dist/next_gen_ui_llama_stack-0.0.1-py3-none-any.whl
pip uninstall -y ../../dist/next_gen_ui_rhds_renderer-0.0.1-py3-none-any.whl
pip uninstall -y ../../dist/next_gen_ui_patternfly_renderer-0.0.1-py3-none-any.whl

echo Installing all packages
pip install ../../dist/next_gen_ui_agent-0.0.1-py3-none-any.whl
pip install ../../dist/next_gen_ui_langgraph-0.0.1-py3-none-any.whl
pip install ../../dist/next_gen_ui_llama_stack-0.0.1-py3-none-any.whl
pip install ../../dist/next_gen_ui_rhds_renderer-0.0.1-py3-none-any.whl
pip install ../../dist/next_gen_ui_patternfly_renderer-0.0.1-py3-none-any.whl
