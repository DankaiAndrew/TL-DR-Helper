#!/bin/bash

# PaperSummarizer Installation Script

# Upgrade pip
pip install --upgrade pip

# Install PyTorch
pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128

# Install Hugging Face Transformers (specific commit)
pip install git+https://github.com/huggingface/transformers@51ed61e2f05176f81fa7c9decba10cc28e138f61

# Install accelerate for faster inference
pip install accelerate

# Install utilities and dependencies
pip install qwen_vl_utils argparse matplotlib pymupdf ipywidgets
pip install pandas seaborn openai scikit-learn
pip install hydra-core

# Install Colpali
pip install colpali_engine==0.1.1
pip install mteb

# Install git-lfs
conda install git-lfs -y

# Install additional dependencies
pip install fastapi
pip install python-pptx
pip install markdown
pip install Levenshtein
pip install python-multipart
pip install uvicorn 