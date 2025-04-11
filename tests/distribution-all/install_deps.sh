echo UNINSTALLING all existing packages
pip uninstall -y ../../dist/next_gen_ui_*.whl

echo INSTALLING all packages
pip install ../../dist/next_gen_ui_*.whl
