# System Architecture & Model Specifications

## 🏛️ System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                          CLIENT LAYER                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│  │  cURL    │  │ Python   │  │ Browser  │  │  Batch   │            │
│  │ Request  │  │ Requests │  │ (Swagger)│  │ Scripts  │            │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘            │
└───────┼─────────────┼─────────────┼─────────────┼───────────────────┘
        │             │             │             │
        └─────────────┴─────────────┴─────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          API LAYER                                   │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                    FastAPI Application                         │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │  │
│  │  │ POST /evaluate│  │ GET /health  │  │  GET /docs   │        │  │
│  │  └──────┬───────┘  └──────────────┘  └──────────────┘        │  │
│  │         │                                                      │  │
│  │         │  ┌─────────────────────────────────────┐            │  │
│  │         └─▶│  Request Validation (Pydantic)      │            │  │
│  │            │  - File type check (.pptx)          │            │  │
│  │            │  - Size limit (50MB)                │            │  │
│  │            │  - Problem statement validation     │            │  │
│  │            └─────────────┬───────────────────────┘            │  │
│  └──────────────────────────┼────────────────────────────────────┘  │
└─────────────────────────────┼────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATION LAYER                               │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │              Evaluation Orchestrator                           │  │
│  │  - Lazy model loading                                          │  │
│  │  - Pipeline coordination                                       │  │
│  │  - Score combination (70% LLM + 30% Semantic)                 │  │
│  │  - Schema validation                                           │  │
│  │  - Error handling & logging                                    │  │
│  └───┬───────────┬───────────┬───────────┬────────────────────────┘  │
└──────┼───────────┼───────────┼───────────┼────────────────────────────┘
       │           │           │           │
       ▼           ▼           ▼           ▼
┌──────────────────────────────────────────────────────────────────────┐
│                      PROCESSING LAYER                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │   PPT    │  │Summarize │  │ Semantic │  │   LLM    │             │
│  │Extractor │  │  Engine  │  │  Scorer  │  │Evaluator │             │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘             │
└───────┼─────────────┼─────────────┼─────────────┼────────────────────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
┌──────────────────────────────────────────────────────────────────────┐
│                       MODEL LAYER                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │ python-  │  │   BART   │  │ MiniLM   │  │ Mistral  │             │
│  │   pptx   │  │Large-CNN │  │  L6-v2   │  │   7B     │             │
│  │          │  │  406M    │  │   22M    │  │  (8-bit) │             │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘             │
│                                                                        │
│  Fallback: FLAN-T5-Base (250M) for CPU-only environments             │
└────────────────────────────────────────────────────────────────────────┘
```

## 📊 Data Flow Diagram

```
┌─────────────┐
│ User Upload │
│ - PPT File  │
│ - Problem   │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│ 1. PPT Extraction   │
│ ─────────────────── │
│ Input: .pptx file   │
│ Output:             │
│ {                   │
│   slides: [         │
│     {               │
│       title: str    │
│       content: []   │
│       notes: str    │
│     }               │
│   ]                 │
│ }                   │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ 2. Summarization    │
│ ─────────────────── │
│ Input: Slide data   │
│ Process:            │
│ - Per-slide summary │
│ - Meta-summary      │
│ Output:             │
│ "Slide 1: ...       │
│  Slide 2: ..."      │
└──────┬──────────────┘
       │
       ├──────────────────────────┐
       │                          │
       ▼                          ▼
┌─────────────────┐    ┌─────────────────────┐
│ 3a. Semantic    │    │ 3b. LLM Evaluation  │
│     Scoring     │    │ ─────────────────── │
│ ─────────────── │    │ Input:              │
│ Input:          │    │ - Problem statement │
│ - Problem       │    │ - Summary           │
│ - Summary       │    │ Process:            │
│ Process:        │    │ - Structured prompt │
│ - Embed both    │    │ - JSON generation   │
│ - Cosine sim    │    │ - Parse & validate  │
│ Output:         │    │ Output:             │
│ relevance: 8.2  │    │ {                   │
└──────┬──────────┘    │   scores: {...}     │
       │               │   strengths: [...]  │
       │               │   weaknesses: [...] │
       │               │ }                   │
       │               └──────┬──────────────┘
       │                      │
       └──────────┬───────────┘
                  ▼
┌─────────────────────────────┐
│ 4. Score Combination        │
│ ─────────────────────────── │
│ adjusted_relevance =        │
│   0.7 * llm_score +         │
│   0.3 * semantic_score      │
│                             │
│ overall_score =             │
│   sum(all_dimension_scores) │
└──────┬──────────────────────┘
       │
       ▼
┌─────────────────────┐
│ 5. Validation       │
│ ─────────────────── │
│ - Pydantic schema   │
│ - Score ranges      │
│ - Required fields   │
│ - Type checking     │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ JSON Response       │
│ {                   │
│   scores: {...}     │
│   overall_score: 40 │
│   strengths: [...]  │
│   weaknesses: [...] │
│   ...               │
│ }                   │
└─────────────────────┘
```

## 🤖 Model Specifications

### 1. Summarization Model

**Model ID**: `facebook/bart-large-cnn`

**Specifications**:
- **Architecture**: BART (Bidirectional and Auto-Regressive Transformers)
- **Parameters**: 406 million
- **Training Data**: CNN/DailyMail dataset (news articles)
- **Max Input**: 1024 tokens
- **Max Output**: 142 tokens (configurable)
- **License**: Apache 2.0

**Performance**:
- CPU: 2-3 seconds per slide
- GPU: <1 second per slide
- Memory: ~1.6GB (model weights)

**Why This Model**:
- State-of-the-art abstractive summarization
- Excellent at condensing verbose content
- Trained on news articles (similar to presentation content)
- Good balance of quality and speed

**Configuration**:
```python
from transformers import pipeline

summarizer = pipeline(
    "summarization",
    model="facebook/bart-large-cnn",
    device=0  # GPU, or -1 for CPU
)

summary = summarizer(
    text,
    max_length=130,
    min_length=30,
    do_sample=False
)
```

---

### 2. Embedding Model

**Model ID**: `sentence-transformers/all-MiniLM-L6-v2`

**Specifications**:
- **Architecture**: MiniLM (distilled from RoBERTa)
- **Parameters**: 22 million
- **Embedding Dimensions**: 384
- **Max Sequence Length**: 256 tokens
- **Training**: Trained on 1B+ sentence pairs
- **License**: Apache 2.0

**Performance**:
- Speed: ~1000 sentences/second on CPU
- Memory: ~90MB (model weights)
- Inference: <100ms for full presentation

**Why This Model**:
- Best speed/quality tradeoff in sentence-transformers
- Optimized specifically for semantic similarity
- Very fast on CPU (no GPU needed)
- Compact 384-dim embeddings

**Configuration**:
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
embeddings = model.encode([text1, text2])
similarity = cosine_similarity(embeddings[0], embeddings[1])
```

---

### 3. LLM Evaluation Model (Primary)

**Model ID**: `mistralai/Mistral-7B-Instruct-v0.2`

**Specifications**:
- **Architecture**: Mistral (decoder-only transformer)
- **Parameters**: 7 billion
- **Context Length**: 8192 tokens
- **Quantization**: 8-bit (optional, reduces VRAM by 50%)
- **Training**: Instruction-tuned on diverse tasks
- **License**: Apache 2.0

**Performance**:
- GPU (8-bit): 3-5 seconds, 7GB VRAM
- GPU (FP16): 2-3 seconds, 14GB VRAM
- CPU: 30-60 seconds, 16GB RAM

**Why This Model**:
- Excellent instruction following
- Strong JSON generation capabilities
- 8K context handles long presentations
- Apache 2.0 license (commercial use OK)
- Active community and support

**Configuration**:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.2")
model = AutoModelForCausalLM.from_pretrained(
    "mistralai/Mistral-7B-Instruct-v0.2",
    load_in_8bit=True,  # 8-bit quantization
    device_map="auto"
)

outputs = model.generate(
    inputs,
    max_new_tokens=1024,
    temperature=0.3,
    top_p=0.9
)
```

---

### 4. LLM Evaluation Model (Fallback)

**Model ID**: `google/flan-t5-base`

**Specifications**:
- **Architecture**: T5 (encoder-decoder)
- **Parameters**: 250 million
- **Context Length**: 512 tokens
- **Training**: Instruction-tuned on 1800+ tasks
- **License**: Apache 2.0

**Performance**:
- CPU: 10-15 seconds
- GPU: 1-2 seconds
- Memory: ~1GB

**Why This Model**:
- CPU-friendly (250M vs 7B params)
- Good instruction following
- Fast inference
- Reliable JSON generation

**When Used**:
- Automatically selected on CPU if Mistral is too large
- Manual override in config.py
- Resource-constrained environments

**Configuration**:
```python
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-base")
model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-base")

outputs = model.generate(
    inputs,
    max_new_tokens=512,
    temperature=0.3
)
```

---

## 🔄 Model Selection Decision Tree

```
Start: Evaluate Presentation
│
├─ Is GPU available?
│  │
│  ├─ YES
│  │  │
│  │  ├─ VRAM >= 14GB?
│  │  │  ├─ YES → Use Mistral-7B (FP16)
│  │  │  └─ NO → VRAM >= 7GB?
│  │  │         ├─ YES → Use Mistral-7B (8-bit)
│  │  │         └─ NO → Use FLAN-T5-Base
│  │  │
│  │  └─ Summarization: BART-Large-CNN (GPU)
│  │     Embeddings: MiniLM-L6-v2
│  │
│  └─ NO (CPU only)
│     │
│     ├─ RAM >= 16GB?
│     │  ├─ YES → Use Mistral-7B (slow but accurate)
│     │  └─ NO → Use FLAN-T5-Base (fast, good quality)
│     │
│     └─ Summarization: BART-Large-CNN (CPU)
│        Embeddings: MiniLM-L6-v2
│
End: Return Evaluation
```

---

## 📦 Model Download & Caching

### Automatic Download

All models are automatically downloaded on first use:

```python
# Models cached to: ~/.cache/huggingface/hub/
# Typical sizes:
# - BART-Large-CNN: ~1.6GB
# - MiniLM-L6-v2: ~90MB
# - Mistral-7B: ~14GB (FP16) or ~7GB (8-bit)
# - FLAN-T5-Base: ~1GB
```

### Pre-download (Optional)

```python
from transformers import AutoModel
from sentence_transformers import SentenceTransformer

# Download all models
AutoModel.from_pretrained("facebook/bart-large-cnn")
SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
AutoModel.from_pretrained("mistralai/Mistral-7B-Instruct-v0.2")
AutoModel.from_pretrained("google/flan-t5-base")
```

### Custom Cache Directory

```python
# In config.py
import os
os.environ['TRANSFORMERS_CACHE'] = '/path/to/cache'
```

---

## ⚡ Performance Optimization Strategies

### 1. 8-bit Quantization (GPU)

```python
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    load_in_8bit=True,  # Reduces VRAM by 50%
    device_map="auto"
)
```

**Impact**:
- VRAM: 14GB → 7GB
- Speed: ~10% slower
- Quality: <1% degradation

### 2. Batch Processing

```python
# Summarize multiple slides at once
summaries = summarizer(
    [slide1, slide2, slide3],
    batch_size=8
)
```

**Impact**:
- Speed: 2-3x faster for large presentations
- Memory: Slightly higher peak usage

### 3. Model Pruning (Future)

```python
# Remove less important weights
from transformers import prune_linear_layer

pruned_model = prune_linear_layer(model, amount=0.3)
```

**Impact**:
- Size: 30% smaller
- Speed: 20-30% faster
- Quality: 2-5% degradation

---

## 🎯 Model Comparison Matrix

| Aspect | BART-Large | MiniLM-L6 | Mistral-7B | FLAN-T5 |
|--------|-----------|-----------|------------|---------|
| **Task** | Summarize | Embed | Evaluate | Evaluate (fallback) |
| **Params** | 406M | 22M | 7B | 250M |
| **Speed (GPU)** | Fast | Very Fast | Medium | Fast |
| **Speed (CPU)** | Medium | Very Fast | Slow | Medium |
| **Quality** | Excellent | Excellent | Excellent | Good |
| **VRAM (GPU)** | 2GB | <1GB | 7-14GB | 1GB |
| **RAM (CPU)** | 4GB | <1GB | 16GB | 2GB |
| **License** | Apache 2.0 | Apache 2.0 | Apache 2.0 | Apache 2.0 |

---

## 🔧 Troubleshooting Model Issues

### Issue: Model Download Fails

**Cause**: Network issues, Hugging Face rate limiting

**Solution**:
```bash
# Use mirror
export HF_ENDPOINT=https://hf-mirror.com

# Or download manually
huggingface-cli download facebook/bart-large-cnn
```

### Issue: Out of Memory

**Cause**: GPU VRAM or system RAM insufficient

**Solution**:
```python
# 1. Enable 8-bit quantization
USE_8BIT = True

# 2. Use smaller models
LLM_MODEL = "google/flan-t5-base"
SUMMARIZATION_MODEL = "facebook/bart-base"

# 3. Reduce batch size
batch_size = 1
```

### Issue: Slow Inference

**Cause**: Running on CPU or large model

**Solution**:
```python
# 1. Use GPU if available
DEVICE = "cuda"

# 2. Use smaller models
LLM_MODEL = "google/flan-t5-base"

# 3. Enable optimizations
torch.backends.cudnn.benchmark = True
```

---

## 📊 Recommended Hardware Configurations

### Minimum (CPU Only)

- **CPU**: 4 cores, 2.5GHz+
- **RAM**: 8GB
- **Storage**: 10GB
- **Models**: FLAN-T5-Base, BART-Base
- **Performance**: ~60s per evaluation

### Recommended (Consumer GPU)

- **GPU**: RTX 3060 (12GB VRAM) or better
- **CPU**: 6 cores
- **RAM**: 16GB
- **Storage**: 20GB
- **Models**: Mistral-7B (8-bit), BART-Large
- **Performance**: ~5-8s per evaluation

### Optimal (Professional GPU)

- **GPU**: RTX 4090 (24GB VRAM) or A100
- **CPU**: 8+ cores
- **RAM**: 32GB
- **Storage**: 50GB
- **Models**: Mistral-7B (FP16), all large variants
- **Performance**: ~3-5s per evaluation

---

**This architecture is designed for production use with automatic fallbacks, comprehensive error handling, and optimal performance across diverse hardware configurations.**
