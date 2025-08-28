# NGUI: End-to-End Demo

## ✨ Summary

This update introduces a complete end-to-end example of the Next Gen UI (NGUI) system, featuring a new demo, improved configuration, and comprehensive documentation. This makes it easier for new contributors to get started and provides a flexible foundation for development.

---

## 📋 Changes

- **New Demo**: Added a React Vite project with a `OneCard` component demo.
- **Enhanced Documentation**: The `README` now includes complete setup instructions for Ollama, the backend, and the frontend.
- **Configurable Backend**: The `main.py` file has been made more generic to support different AI models like Ollama, OpenAI, and others.
- **Configuration Guide**: A new `MODEL_CONFIGURATION.md` file provides detailed setup examples.
- **Fixed Imports**: Updated the `DynamicComponent` import to work correctly with the npm-linked UI package.

---

## 🧪 How to Test

Follow these steps to test the complete chat, AI, and UI generation flow:

1.  **Install Ollama**:

```bash
ollama pull llama3.2:3b
```

2.  **Start the Backend**:

Set up Python in project root directory.

```bash
pants export
# change `3.11.13` in the path to your python version, or to `latest` for venv symlink created from `CONTRIBUTING.md`!
source dist/export/python/virtualenvs/python-default/3.11.13/bin/activate
export PYTHONPATH=./libs:./tests:$PYTHONPATH
```

Start Assisten API

```bash
python tests/ngui-e2e/main.py
python main.py # if running in VS Code
```
You can check it's running under [http://127.0.0.1:5000/docs](http://127.0.0.1:5000/docs)

3.  **Start the Frontend**:

Navigate to the `NGUI-e2e` folder and run:

```bash
npm install
npm link dynamicui
npm run dev
```

Note: It's expected you already build `dynamicui` package located in [libs_js/next_gen_ui_react](/libs_js/next_gen_ui_react/)

---

## 🚀 Benefits

- **Easy Setup**: New contributors can now get up and running quickly.
- **Flexible Configuration**: The system is more adaptable, allowing for different AI models to be used.
- **Complete Working Example**: Provides a clear, functional reference for the entire NGUI system.
- **Clear Documentation**: The improved documentation simplifies the setup and testing process.
