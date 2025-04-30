# TL;DR: A Multi-Agent Framework for Research Paper Summary Slide Generation

For researchers managing extensive literature reviews and paper collections, creating and maintaining presentation slides for each paper is a time-consuming task. To address this challenge, we propose a specialized multi-agent framework that automatically transforms academic papers into concise one page summaries. These summaries can be integrated into comprehensive paper collection presentations, significantly enhancing researchers' ability to organize, present, and share knowledge. 

## Video Demonstration

You can watch the video demonstration of our project here: [Project Video](https://youtu.be/ux1_VWRCBhQ)

## System Requirements

This framework requires approximately 6-7GB of VRAM to run efficiently. Please ensure your system meets these requirements before proceeding with the installation.

## Getting Started

### 1. Clone the Repository

```bash
git clone git@github.com:DankaiAndrew/TL-DR-Helper.git
cd TL-DR-Helper
```

## Node.js Environment Setup

This project requires [Node.js](https://nodejs.org/) (LTS version recommended).

### 1. Check if Node.js is Installed

Open your terminal (Terminal / Command Prompt) and run:

```bash
node -v
npm -v
```

## Conda Environment Setup

### 1. Create and Activate Conda Environment

Create a new Conda environment with Python 3.12:

```bash
conda create -n tldrhelper python=3.12
conda activate tldrhelper
```

### 2. Install Dependencies

Run the installation script:

```bash
bash install.sh
```

## Agent and API Configuration

The framework supports both API-based and local models. Configure the models in the respective YAML files:

### Supported Models

#### API Models
- OpenAI (GPT-4o)
- DeepSeek (DeepSeek-Chat)

#### Local Models
- Llama3.1 (Text Model)
- Qwen2VL (Vision-Language Model)
- Qwen25VL (Vision-Language Model)

### Configuration Files

The configuration files are located in the `SlidesSummarizer/config/` directory:

1. **base.yaml** (`SlidesSummarizer/config/base.yaml`): Configure the agents and their models
   - `image_agent`: Should be configured as a VLM (Vision Language Model)
   - `general_agent`: Should be configured as a VLM
   - `text_agent`: Should be configured as a VLM
   - `sum_agent`: Should be configured as an LLM (Language Model)

2. **deepseek.yaml** (`SlidesSummarizer/config/model/deepseek.yaml`): Configure the DeepSeek API
   - Add your API key
   - Configure other parameters as needed

3. **openai.yaml** (`SlidesSummarizer/config/model/openai.yaml`): Configure the OpenAI API
   - Add your API key
   - Configure other parameters as needed

### Default Configuration

By default, the framework uses:
- OpenAI API for `image_agent`, `general_agent`, and `text_agent`
- DeepSeek API for `sum_agent`

If you don't modify the agent configurations in `base.yaml`, the system will use these default settings.

## Starting the Application

### 1. Start the Frontend

Open a new terminal and run:

```bash
cd frontend_5260
npm install
npm run dev
```

Open the URL displayed in the terminal to access the frontend.

### 2. Start the Backend

Open another terminal and run:

```bash
uvicorn backend_5260.main:app --reload --port 8000
```

Open the URL displayed in the terminal to access the backend.

## System Architecture

![Image](https://github.com/user-attachments/assets/f9498569-8d84-460e-8772-baa635c47d4c)

Our multi-agent system consists of five specialized agents working in concert to analyze and summarize research papers:

### Initial Processing
1. PDF Information Extraction
   - Uses PyMuPDF for comprehensive PDF parsing
   - Extracts text, images, and structural information
   - Prepares content for agent analysis

2. Image Retrieval
   - Employs pretrained ColPali (Visual Retriever based on PaliGemma-3B)
   - Uses ColBERT strategy for efficient image retrieval
   - Focuses on retrieving model structure and experiment results
   - Identifies relevant page images for detailed analysis

### Agent System

#### 1. Image Agent
- Analyzes retrieved top-k visual segments from the PDF (e.g., experiment results, model figures)
- Uses the provided question and critical visual cues from critical_agent
- Processes and interprets visual content with context-aware understanding

#### 2. Text Agent
- Analyzes the PDF with a question and critical textual focus provided by critical_agent
- Focuses on detailed textual reasoning
- Processes both structured and unstructured text content

#### 3. General Agent
- Generates an initial summary based solely on the PDF and question
- Provides a general understanding of the document
- Sets the foundation for more detailed analysis

#### 4. Critical Agent
- Reflects on the general summary to identify missing or unclear information
- Generates critical textual cues for text_agent
- Provides background visual guidance for image_agent
- Ensures comprehensive coverage of important aspects

#### 5. Summary Agent
- Integrates outputs from general agent, text_agent, and image_agent
- Produces the final comprehensive summary
- Ensures coherent and well-structured output

The system's workflow:
1. PDF processing and image retrieval using PyMuPDF and ColPali
2. General agent provides initial understanding of the paper
3. Critical agent analyzes the general summary and identifies gaps
4. Image and text agents work in parallel with guidance from critical agent
5. Summary agent integrates all insights into a final comprehensive summary
6. Output is formatted as a well-structured, one-page summary suitable for presentation slides 

## Citation

This project is based on the multi-agent framework from:

```bibtex
@article{han2025mdocagent,
  title={MDocAgent: A Multi-Modal Multi-Agent Framework for Document Understanding},
  author={Han, Siwei and Xia, Peng and Zhang, Ruiyi and Sun, Tong and Li, Yun and Zhu, Hongtu and Yao, Huaxiu},
  journal={arXiv preprint arXiv:2503.13964},
  year={2025}
}
``` 
