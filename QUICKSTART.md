# Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies (2 minutes)

```bash
cd "/Users/adityasmac/Desktop/ppt evaluator"

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### Step 2: Start the Server (1 minute)

```bash
# Start FastAPI server
uvicorn main:app --reload

# Server will start at http://localhost:8000
# API docs available at http://localhost:8000/docs
```

### Step 3: Evaluate a Presentation (30 seconds)

**Option A: Using cURL**
```bash
curl -X POST "http://localhost:8000/evaluate" \
  -F "file=@your_presentation.pptx" \
  -F "problem_statement=Build a web scraper for e-commerce websites"
```

**Option B: Using Python**
```python
import requests

with open('presentation.pptx', 'rb') as f:
    files = {'file': f}
    data = {'problem_statement': 'Build a web scraper'}
    response = requests.post('http://localhost:8000/evaluate', 
                            files=files, data=data)

result = response.json()
print(f"Score: {result['overall_score']}/50")
print(f"Strengths: {result['strengths']}")
```

**Option C: Using Browser**
1. Go to http://localhost:8000/docs
2. Click on `POST /evaluate`
3. Click "Try it out"
4. Upload your PPT and enter problem statement
5. Click "Execute"

---

## 📁 Project Structure

```
ppt evaluator/
├── config.py                    # Configuration & settings
├── ppt_extractor.py            # Extract content from PPT
├── summarizer.py               # Summarize slides (BART)
├── semantic_scorer.py          # Relevance scoring (embeddings)
├── llm_evaluator.py            # LLM evaluation (Mistral/FLAN-T5)
├── evaluation_orchestrator.py  # Coordinate all components
├── models.py                   # Pydantic schemas
├── main.py                     # FastAPI application
├── test_evaluation.py          # Test suite
├── example_usage.py            # Usage examples
├── requirements.txt            # Dependencies
├── Dockerfile                  # Container config
├── README.md                   # Full documentation
├── ARCHITECTURE.md             # System architecture
└── .gitignore                  # Git exclusions
```

---

## 🎯 Common Use Cases

### 1. Evaluate Single Presentation

```bash
curl -X POST "http://localhost:8000/evaluate" \
  -F "file=@presentation.pptx" \
  -F "problem_statement=Your problem here" \
  | jq '.'  # Pretty print JSON
```

### 2. Batch Evaluate Multiple Presentations

```python
from example_usage import batch_evaluate

files = ['ppt1.pptx', 'ppt2.pptx', 'ppt3.pptx']
results = batch_evaluate(files, "Build a web scraper")

for r in results:
    print(f"{r['file']}: {r['evaluation']['overall_score']}/50")
```

### 3. Check System Health

```bash
curl http://localhost:8000/health | jq '.'
```

### 4. Run Tests

```bash
pytest test_evaluation.py -v
```

---

## ⚙️ Configuration

Edit `config.py` to customize:

```python
# Use smaller models for faster inference (lower quality)
SUMMARIZATION_MODEL = "facebook/bart-base"  # Instead of bart-large
LLM_MODEL = "google/flan-t5-base"  # Instead of Mistral-7B

# Adjust API settings
API_PORT = 8080
MAX_UPLOAD_SIZE = 100 * 1024 * 1024  # 100MB

# Change evaluation parameters
LLM_TEMPERATURE = 0.1  # More deterministic (0.0-1.0)
```

---

## 🐳 Docker Deployment

```bash
# Build image
docker build -t ppt-evaluator .

# Run (CPU)
docker run -p 8000:8000 ppt-evaluator

# Run (GPU)
docker run --gpus all -p 8000:8000 ppt-evaluator
```

---

## 🤖 Models Used

| Component | Model | Size | Speed (GPU) |
|-----------|-------|------|-------------|
| Summarization | facebook/bart-large-cnn | 406M | <1s/slide |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 | 22M | <100ms |
| Evaluation | mistralai/Mistral-7B-Instruct-v0.2 | 7B | 3-5s |
| Fallback | google/flan-t5-base | 250M | 1-2s |

All models download automatically on first use to `~/.cache/huggingface/`

---

## 📊 Expected Output

```json
{
  "scores": {
    "relevance": 8.5,
    "clarity": 7.0,
    "technical_accuracy": 9.0,
    "structure": 8.0,
    "completeness": 7.5
  },
  "overall_score": 40.0,
  "strengths": [
    "Clear technical explanation",
    "Good use of examples",
    "Well-structured flow"
  ],
  "weaknesses": [
    "Missing performance metrics",
    "Could improve visual design"
  ],
  "improvement_suggestions": [
    "Add benchmark results",
    "Include architecture diagrams",
    "Provide code examples"
  ],
  "missing_elements": [
    "Error handling strategy"
  ],
  "summary_evaluation": "Strong presentation...",
  "metadata": {
    "slide_count": 12,
    "semantic_relevance_score": 8.2
  }
}
```

---

## 🔧 Troubleshooting

### Models downloading slowly?
- Models are 1-14GB, first run takes time
- Downloads cached for future use
- Use `export HF_ENDPOINT=https://hf-mirror.com` for mirrors

### Out of memory?
```python
# In config.py
LLM_MODEL = "google/flan-t5-base"  # Smaller model
USE_8BIT = True  # If GPU available
```

### Slow inference?
- Expected on CPU (30-60s)
- Use GPU for 10x speedup
- Or switch to smaller models

### JSON parsing fails?
- System has 3 retries + default evaluation
- Check logs for details
- May need to adjust prompt template

---

## 📚 Documentation

- **README.md**: Complete documentation
- **ARCHITECTURE.md**: System design & model specs
- **API Docs**: http://localhost:8000/docs (when running)
- **Code Comments**: Inline documentation in all files

---

## 🎓 Next Steps

1. **Test with your presentations**: Upload real PPTs to test
2. **Customize prompts**: Edit evaluation criteria in config.py
3. **Deploy to cloud**: See README for AWS/GCP/Azure instructions
4. **Add features**: Visual analysis, custom rubrics (see walkthrough.md)

---

## 💡 Tips

- **First run is slow**: Models download (1-14GB total)
- **Use GPU**: 10x faster than CPU
- **Batch processing**: Use example_usage.py for multiple files
- **Monitor logs**: Check terminal for detailed progress
- **Adjust temperature**: Lower = more consistent, higher = more creative

---

## 📞 Support

- Check `/docs` endpoint for API documentation
- Review test_evaluation.py for usage examples
- See ARCHITECTURE.md for model details
- Read README.md for comprehensive guide

---

**Ready to evaluate presentations! 🚀**
