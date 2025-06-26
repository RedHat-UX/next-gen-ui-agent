echo UNINSTALLING all existing packages
pip uninstall -y ../../dist/next_gen_ui_*.whl

echo INSTALLING all packages
pip install pytest
pip install ../../dist/next_gen_ui_*.whl -c ../../libs/3rdparty/python/llama-stack-client-constraints.txt
