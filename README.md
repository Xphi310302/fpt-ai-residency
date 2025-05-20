# FPT AI Residency Project
# Ranking Results
- Rank 21 in Public Set and Rank 22 in Private Set. The results can be found in this [link](https://www.kaggle.com/competitions/fpt-ai-residency-batch-6-entry-test/leaderboard?tab=public) 
- Note: You can find me as "Phi Nguyễn Xuân" in the team name
## Overview
This repository contains code for a multiple-choice question (CodeMMLU benchmark) answering system for software development topics. The project includes inference scripts for various language models (GPT, Qwen), finetuning notebooks, and data preprocessing utilities.

## Project Structure
```
├── data/                  # Dataset directory
│   ├── b6_test_data.csv   # Test dataset
│   ├── b6_train_data.csv  # Training dataset
│   ├── finetuning_data.csv # Data for model finetuning
│   └── sample_submission.csv # Sample submission format
├── lora_model_3ksample/   # LoRA model weights directory
├── models/                # Model weights directory
├── notebooks/             # Jupyter notebooks
│   ├── ensemble.ipynb     # Ensemble methods for combining model predictions
│   ├── inference.ipynb    # Inference notebook
│   ├── kaggle-qwen-2-5-coder-14b-conversational.ipynb # Qwen model finetuning
│   ├── preprocessing.ipynb # Data preprocessing
│   └── test.ipynb         # Testing notebook
├── output/                # Output directory for predictions
├── .env                   # Environment variables (API keys)
├── .gitignore             # Git ignore file
├── inference_gpt.py       # GPT model inference script
├── inference_gpt_poe.py   # GPT with Product of Experts (PoE) inference
├── inference_llama.py     # Llama model inference script
├── inference_qwen-32b.py  # Qwen 32B model inference script
├── inference_qwen.py      # Qwen model inference script
├── prompt_template.py     # Prompt templates for different models
└── pyproject.toml         # Project dependencies
```

## Inference Scripts

### inference_gpt.py
This script uses OpenAI's GPT models to answer multiple-choice questions. It includes:
- Data loading and preprocessing
- Answer generation using GPT models
- Format correction for answers in incorrect formats
- Submission file generation

Usage:
```bash
python inference_gpt.py
```

### inference_gpt_poe.py
This script implements the Product of Experts (PoE) with Iterative Deletion (ID²) approach using GPT models:
- Calculates probabilities for each option
- Eliminates the two least likely options
- Recalculates probabilities with remaining options
- Selects the highest probability option

Usage:
```bash
python inference_gpt_poe.py
```

### inference_qwen.py
This script uses Qwen models for inference through a local API:
- Connects to a local server via localtunnel
- Supports checkpoint saving
- Includes format correction

Usage:
```bash
python inference_qwen.py
```

### inference_qwen-32b.py
Similar to inference_qwen.py but specifically configured for the 32B parameter version of Qwen.

## Prompt Templates (prompt_template.py)
Contains various prompt templates used by the inference scripts:
- `SYSTEM_MESSAGE`: System prompt for the models
- `ZERO_SHOT_TEMPLATE`: Template for zero-shot learning
- `FEW_SHOT_TEMPLATE`: Template with examples for few-shot learning
- `CORRECT_FORMAT_PROMPT`: Template for correcting answer formats

## Finetuning Notebooks

### kaggle-qwen-2-5-coder-14b-conversational.ipynb
This notebook demonstrates finetuning the Qwen 2.5 Coder 14B model:
- Uses Unsloth for efficient finetuning
- Implements LoRA (Low-Rank Adaptation) for parameter-efficient training
- Configures training hyperparameters
- Evaluates model performance

### preprocessing.ipynb
This notebook handles data preprocessing:
- Loads and cleans the training data
- Formats multiple-choice questions and answers
- Prepares data for model finetuning
- Samples data for testing

### inference.ipynb
Interactive notebook for testing inference with different models and parameters.

### ensemble.ipynb
Implements ensemble methods to combine predictions from multiple models for improved accuracy.

## Setup and Usage

### Prerequisites
- Python 3.8+
- Required API keys (OpenAI, Groq) in .env file

### Environment Setup
1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -e .
```

3. Create a .env file with your API keys:
```
OPENAI_API_KEY=your_openai_key
GROQ_API_KEY=your_groq_key
```

### Running Inference
Choose the appropriate inference script based on the model you want to use:
```bash
python inference_gpt.py  # For GPT models
python inference_qwen.py  # For Qwen models
```

### Output
Inference results are saved to the `output/` directory as CSV files.

## License
[MIT](https://choosealicense.com/licenses/mit/)
