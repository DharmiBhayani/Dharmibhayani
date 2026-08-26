# AI Project Manager — Final 3-Model PDF RAG

## Models
- Groq: `llama-3.3-70b-versatile`
- Ollama: `llama3.1:8b`
- Ollama: `qwen2.5:7b-instruct`

## Setup

```powershell
pip install -r requirements.txt
```

Create `.env`:

```text
GROQ_API_KEY=YOUR_KEY
GROQ_MODEL=llama-3.3-70b-versatile
```

Install local models:

```powershell
ollama pull llama3.1:8b
ollama pull qwen2.5:7b-instruct
```

Start Ollama if needed:

```powershell
ollama serve
```

Run:

```powershell
streamlit run app.py
```

## Demo flow

1. Open **Project**.
2. Create a project.
3. Upload the project PDF.
4. Save the project. The PDF is indexed into FAISS.
5. Open **PDF RAG Q&A**.
6. Ask a question.
7. Select **Compare All 3 Models**.
8. Compare each answer, latency, input tokens, output tokens and total tokens.
9. Open the source page shown under each answer.
10. Open **Dashboard** to compare all recorded requests.

## Important

No model can be guaranteed to answer every question correctly. The RAG prompt is intentionally grounded: if the retrieved PDF context does not support the answer, the model is instructed not to invent information.

For a fair model comparison, ask the exact same question and keep `PDF chunks to retrieve` the same.


## Updated Task Planner flow

The Task Planner is the main project-PDF Q&A page. It does not use resume data.
1. Create a project on Project page.
2. Upload the project's PDF there.
3. Go to Task Planner.
4. Select the project.
5. Ask a question about that project's PDF.
6. Select one model or compare all 3 models.
7. The answer, model, latency, tokens, and retrieved PDF pages appear on Task Planner.
8. Click "Open Page N" to open the exact retrieved PDF page.