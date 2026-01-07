# Next Gen UI Agent LLM Fine-tuning with Unsloth and LoRA

This project provides a complete Google Colab notebook for fine-tuning Large Language Models (2B-3B parameters) for the UI Agent 
using LoRA (Low-Rank Adaptation) and exporting them for use with Ollama.

The included example training data teaches a model to recommend appropriate UI components (tables, cards, charts, image/video players) based on data structure and user intent. 

Final training dataset must be constructed still, it should contain examples for areas like:

* Understanding JSON data structures - array of objects vs. array of simple values vs. simple object, detecting the array size from UI Agent optimization, …
* Generation of the valid JSONPaths for different data structures
* Detecting field value types - image and video URLs, dates, numbers, …
* UI component type selection for data structures and prompts
* Visualized fields selection for data structures and prompts
* UI component specific field rules, mainly for charts, image and video player. Rules not to visualize `id` fileds etc.

## Files

- **`finetune_model.ipynb`** - Google Colab notebook with complete fine-tuning pipeline
- **`training_data.json`** - Example training dataset with 30 Q&A pairs about UI component selection
- **`README.md`** - This file

## Features

✅ **Efficient Fine-tuning**: Uses Unsloth for 2x faster training and reduced memory usage  
✅ **LoRA Adapters**: Parameter-efficient fine-tuning (only ~1-2% of parameters trained)  
✅ **Flexible Models**: Supports Qwen2.5-3B, Llama-3.2-3B, Phi-3.5-mini, and similar models  
✅ **Model-Agnostic**: Uses tokenizer's chat template - works with any chat model automatically  
✅ **Simple Data Format**: Easy-to-use question/answer JSON format  
✅ **Ollama Export**: Automatic conversion to GGUF format for Ollama with multiple quantization options (q4_k_m, q5_k_m, q8_0, f16)

## Quick Start

### 1. Upload to Google Colab and Enable GPU

1. Go to [Google Colab](https://colab.research.google.com/)
2. Upload `finetune_model.ipynb`
3. **Enable GPU (REQUIRED):**
   - Click `Runtime` → `Change runtime type`
   - Under "Hardware accelerator", select **T4 GPU** (or better)
   - Click `Save`
4. The notebook will verify GPU is available in Step 1

### 2. Prepare Your Training Data

Your training data should be in JSON format with the following structure:

```json
[
  {
    "question": "Your question here",
    "answer": "Expected response"
  }
]
```

**Option 1: Multiple JSON files (Recommended)**
- Create a folder (e.g., `training_data/`) on your computer
- Place multiple JSON files in it (e.g., `ui_components.json`, `json_path_generation.json`, etc.)
- Each file should contain an array of Q&A pairs
- The notebook will automatically combine and shuffle all files

**Option 2: Single JSON file**
- Use a single `training_data.json` file with all your Q&A pairs

You can use the provided `training_data.json` as an example (contains 30 Q&A pairs about UI component selection) or create your own.

### 3. Upload Your Training Data

**Manual Upload to Colab:**
1. Click the **folder icon** (📁) in the left sidebar of Colab
2. Create a folder called `training_data` 
3. Upload your JSON files into this folder
4. The notebook will load and combine all JSON files automatically

**Alternative:** Upload a single `training_data.json` file to the root directory

### 4. Run the Notebook

1. Run all cells in order
2. The notebook will:
   - Verify GPU availability
   - Install required packages
   - Load the model
   - Configure LoRA adapters
   - Load and shuffle your training data from multiple files
   - Train the model on your data
   - Export to GGUF format for Ollama

### 5. Download and Use with Ollama

After training completes, the notebook will:
1. Download the GGUF model file, eg. `NGUI-llama-3.2-3b.q4_k_m.gguf` finetuned from Llama 3.2 3B base model.
2. Download a `Modelfile` for Ollama configuration

On your local machine:

```bash
# Create the Ollama model
ollama create ngui-finetuned-model -f Modelfile

# Run the model
ollama run ngui-finetuned-model

# Test with a prompt
>>> What is machine learning?
```

## Training Data Format

The training data should be in simple JSON format:

```json
[
  {
    "question": "I have an array of product objects with name, price, and stock. What UI component should I use?",
    "answer": "For an array of product objects with multiple fields, use a table component. Tables are ideal for displaying structured data..."
  },
  {
    "question": "My data contains a YouTube video URL. How should this be displayed?",
    "answer": "Use a video player component. For video URLs, a video player provides playback controls..."
  }
]
```

**Format:**
- **`question`** (required): Your question or prompt
- **`answer`** (required): The expected response

That's it! Simple and clean.

**Data Shuffling:**
When loading multiple JSON files, the notebook automatically:
- Combines all examples from all files
- Shuffles them randomly (with a fixed seed for reproducibility)
- This ensures examples from different files are mixed together during training

## Configuration Options

You can customize various parameters in the notebook:

### Model Configuration
- `model_name`: Choose from supported models
- `max_seq_length`: Maximum sequence length (default: 2048)
- `load_in_4bit`: Use 4-bit quantization for training (default: True)

### LoRA Configuration
- `lora_r`: LoRA rank (default: 16)
- `lora_alpha`: LoRA scaling factor (default: 16)
- `lora_dropout`: Dropout for LoRA layers (default: 0)

### Training Configuration
- `num_train_epochs`: Number of training epochs (default: 3)
- `per_device_train_batch_size`: Batch size per device (default: 2)
- `gradient_accumulation_steps`: Gradient accumulation (default: 4)
- `learning_rate`: Learning rate (default: 2e-4)

## Supported Models

The notebook works with various 2B-3B parameter models:

- **Llama-3.2-3B-Instruct** (3B, default)
- **Qwen2.5-3B-Instruct** (3B)
- **Phi-3.5-mini-instruct** (3.8B)
- Other compatible models from Unsloth

### Model-Agnostic Design

The notebook uses the tokenizer's built-in `apply_chat_template()` method to prepare training data, which means:
- ✅ No hardcoded chat format tags
- ✅ Automatically adapts to any model's expected format
- ✅ Works with ChatML, Llama format, Alpaca format, and others
- ✅ Easy to switch between different models without code changes

Simply change the `model_name` and the notebook handles the rest!

## Requirements

- Google Colab account (free tier works!)
- **GPU runtime (REQUIRED)**: T4 or better
  - ⚠️ The notebook will NOT work without GPU
  - ⚠️ TPU is NOT supported (requires NVIDIA CUDA GPUs)
  - Free Colab provides T4 GPU access
- Training data in JSON format (`question`/`answer`)
- ~10-20GB of GPU memory (with 4-bit quantization)

## Tips for Best Results

1. **Quality over Quantity**: 50-100 high-quality examples often work better than 1000s of poor examples
2. **Diverse Examples**: Include varied examples that cover different aspects of your task
3. **Clear Questions**: Make questions clear and unambiguous
4. **Comprehensive Answers**: Provide detailed, informative answers
5. **Balance**: Avoid having one type of question dominate your dataset
6. **Validation**: Test your model on questions not in the training set

## Quantization Options

The notebook exports models in multiple quantization formats:

- **q4_k_m** (recommended): Good balance of size and quality (~2GB for 3B model)
- **q5_k_m**: Better quality, slightly larger (~2.5GB for 3B model)
- **q8_0**: High quality, larger size (~3GB for 3B model)
- **f16**: Full precision, largest size (~6GB for 3B model)

## Troubleshooting

### No GPU Error / "Unsloth cannot find any torch accelerator"
**Solution:**
1. Click `Runtime` → `Change runtime type` in Colab
2. Select `T4 GPU` under Hardware accelerator
3. Click `Save`
4. Re-run all cells from the beginning

The notebook includes automatic GPU detection and will show clear error messages if GPU is not available.

### xformers Installation Error / "Failed to build installable wheels"
**Solution:**
The main installation cell has been updated to use pre-built xformers wheels. If you still get errors:

1. Run the **Alternative Installation** cell (Step 1) which skips xformers
2. Xformers is optional - it provides a small speed boost but isn't required
3. The notebook works perfectly fine without it

The updated installation command uses `--no-build-isolation` to avoid building from source.

### Out of Memory Errors
- Reduce `per_device_train_batch_size`
- Reduce `max_seq_length`
- Enable 4-bit quantization
- Use a smaller model

### Slow Training
- Increase `per_device_train_batch_size` if you have memory
- Reduce `num_train_epochs`
- Use a smaller dataset for testing

### Poor Model Performance
- Increase training epochs
- Add more diverse training examples
- Check data quality and format
- Try a larger model or different learning rate

## Resources

- [Unsloth GitHub](https://github.com/unslothai/unsloth)
- [Ollama Documentation](https://github.com/ollama/ollama)
- [LoRA Paper](https://arxiv.org/abs/2106.09685)
- [GGUF Format](https://github.com/ggerganov/llama.cpp/blob/master/gguf-py/README.md)

