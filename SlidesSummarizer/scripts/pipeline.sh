#!/bin/bash

# PaperSummarizer Pipeline Script
# This script runs the complete pipeline: extract_paper -> retrieve_content -> predict

# Check if paper_name is provided
if [ $# -lt 1 ]; then
    echo "Usage: $0 <paper_name> [data_dir]"
    echo "  paper_name: Name of the paper to process"
    echo "  data_dir: Optional data directory (default: data)"
    exit 1
fi

PAPER_NAME=$1
DATA_DIR=${2:-"data"}  # Default to "data" if not provided

echo "===================================================="
echo "Starting processing pipeline for paper: $PAPER_NAME"
echo "Using data directory: $DATA_DIR"
echo "===================================================="

# 1. Extract paper (PDF to text and images)
echo "Step 1: Extracting paper content..."
python scripts/extract_paper.py --paper_name "$PAPER_NAME"
if [ $? -ne 0 ]; then
    echo "Error: Paper extraction failed!"
    exit 1
fi
echo "Paper extraction completed."

# 2. Retrieve content (find model structure and experiment results pages)
echo "Step 2: Retrieving specialized content..."
python scripts/retrieve_content.py --paper_name "$PAPER_NAME" 
if [ $? -ne 0 ]; then
    echo "Error: Content retrieval failed!"
    exit 1
fi
echo "Content retrieval completed."

# 3. Generate summary
echo "Step 3: Generating paper summary..."
python -m scripts.predict paper_name="$PAPER_NAME"
if [ $? -ne 0 ]; then
    echo "Error: Summary generation failed!"
    exit 1
fi
echo "Summary generation completed."

echo "===================================================="
echo "Pipeline completed successfully for paper: $PAPER_NAME"
echo "Results available in $DATA_DIR/$PAPER_NAME/"
echo "====================================================" 