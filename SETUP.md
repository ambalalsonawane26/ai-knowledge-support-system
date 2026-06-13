# Setup Guide for AI Knowledge and Decision Support System

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Pinecone account and API key
- Hugging Face account (for API token)

## Step-by-Step Installation

### 1. Clone the Repository

```bash
git clone https://github.com/ambalalsonawane26/ai-knowledge-support-system.git
cd ai-knowledge-support-system
```

### 2. Create Virtual Environment

```bash
# On macOS/Linux
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Get API Keys

#### Pinecone Setup
1. Sign up at [pinecone.io](https://www.pinecone.io/)
2. Create a new index with:
   - **Name**: `documents`
   - **Dimension**: `384` (for all-MiniLM-L6-v2 model)
   - **Metric**: `cosine`
3. Copy your API key and environment from the dashboard

#### Hugging Face Setup
1. Sign up at [huggingface.co](https://huggingface.co/)
2. Go to Settings → Access Tokens
3. Create a new token with read access
4. Copy your API token

### 5. Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your values
nano .env  # or use your preferred editor
```

Fill in the following:
```
PINECONE_API_KEY=your_pinecone_key
PINECONE_ENVIRONMENT=your_environment_name
PINECONE_INDEX_NAME=documents
HUGGINGFACE_API_TOKEN=your_huggingface_token
LLM_MODEL_NAME=mistral-7b
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

### 6. Run the Application

```bash
# Start Streamlit app
streamlit run app/main.py
```

The application will open at `http://localhost:8501`

### 7. (Optional) Run Backend API

```bash
# In a separate terminal
uvicorn backend.api:app --reload
```

API will be available at `http://localhost:8000`
API documentation at `http://localhost:8000/docs`

## Troubleshooting

### Pinecone Connection Error
```
Error: Failed to initialize Pinecone
```
- Verify API key is correct
- Check environment name (e.g., "us-east1-aws")
- Ensure index exists in your Pinecone account

### Model Download Issues
```
Error downloading model from Hugging Face
```
- Ensure internet connection is stable
- Check Hugging Face token is correct
- Models will be cached locally after first download

### Memory Issues
- Reduce `CHUNK_SIZE` in .env
- Use smaller models like `distilbert-base-uncased`
- Process fewer documents at once

## Testing

Run tests with:
```bash
pytest tests/
```

Run with coverage:
```bash
pytest --cov=app tests/
```

## Project Structure

```
.
├── app/                          # Main Streamlit application
│   ├── main.py                  # Entry point
│   ├── config.py                # Configuration
│   └── utils/                   # Utility modules
│       ├── document_processor.py
│       ├── embeddings.py
│       ├── llm_handler.py
│       └── vector_store.py
├── backend/                      # FastAPI backend (optional)
│   ├── api.py
│   ├── models.py
│   └── services/
├── data/                         # Data storage
│   ├── uploaded_documents/
│   └── processed/
├── tests/                        # Test suite
├── requirements.txt              # Dependencies
├── .env.example                  # Environment template
└── setup.py                      # Package setup
```

## Next Steps

1. **Customize the LLM**: Modify `LLM_MODEL_NAME` in `.env` to use different models
2. **Add Frontend**: Build a React/Vue.js frontend using the API
3. **Deploy**: Deploy to Heroku, AWS, or your preferred platform
4. **Fine-tune**: Fine-tune models on your specific domain

## Common Configuration Options

### Using Different LLM Models

```bash
# Smaller, faster models
LLM_MODEL_NAME=google/flan-t5-base

# Larger, more capable
LLM_MODEL_NAME=meta-llama/Llama-2-7b

# For faster inference
LLM_MODEL_NAME=gpt2
```

### Using Different Embedding Models

```bash
# Larger, more accurate
EMBEDDING_MODEL=sentence-transformers/all-mpnet-base-v2

# Smaller, faster
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

### Adjusting Chunk Sizes

```bash
# For longer documents
CHUNK_SIZE=1000
CHUNK_OVERLAP=100

# For shorter snippets
CHUNK_SIZE=250
CHUNK_OVERLAP=25
```

## Support & Documentation

- [Pinecone Documentation](https://docs.pinecone.io/)
- [Hugging Face Documentation](https://huggingface.co/docs)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [LangChain Documentation](https://docs.langchain.com/)

## License

MIT License - See LICENSE file for details