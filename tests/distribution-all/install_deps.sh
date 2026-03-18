echo UNINSTALLING all existing packages
pip uninstall -y ../../dist/next_gen_ui_*.whl

echo INSTALLING all packages
pip install pytest
# LangChain/LangGraph (required by next_gen_ui_langgraph and distribution tests)
pip install -r ../../libs/3rdparty/python/langchain-requirements.txt
pip install -r ../../libs/3rdparty/python/langgraph-requirements.txt
pip install ../../dist/next_gen_ui_*.whl -c ../../libs/3rdparty/python/llama-stack-client-constraints.txt
