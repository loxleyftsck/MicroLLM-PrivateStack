export const REPO_URL = "https://github.com/loxleyftsck/MicroLLM-PrivateStack";

export const NAV_LINKS = [
  { label: "How it works", href: "#how-it-works" },
  { label: "Capabilities", href: "#capabilities" },
  { label: "Compare", href: "#compare" },
  { label: "FAQ", href: "#faq" },
];

export const STEPS = [
  {
    number: "01",
    title: "Install it on your own box",
    body: "Clone the repo, create a venv, and run scripts/download_model.py. It pulls DeepSeek-R1-1.5B as a GGUF Q4 file onto your disk. No account, no API key, no vendor in the loop.",
  },
  {
    number: "02",
    title: "Load your own knowledge",
    body: "Drop PDF, TXT, or CSV files into a workspace. Chunks are embedded and written to SQLite, so the RAG index rehydrates automatically the next time the server starts.",
  },
  {
    number: "03",
    title: "Ask, and check the receipts",
    body: "Every chat response carries rag_sources — the document, a relevance score, and the exact chunk that was used — alongside the measured ttft_ms for that request.",
  },
  {
    number: "04",
    title: "Ship it hardened",
    body: "Docker Compose for a single host, Kubernetes manifests with non-root pods and probes, and an Nginx front door with TLS, HSTS, and a self-only CSP. All in the repo.",
  },
];

export const CAPABILITIES = [
  {
    tag: "inference",
    module: "ttft_optimizer.py",
    title: "TTFT Optimizer",
    body: "KV-cache warmup plus a p50/p95/p99 histogram exposed at /api/perf/ttft, so first-token latency is a number you can watch, not a vibe.",
  },
  {
    tag: "cache",
    module: "semantic_cache_soa.py",
    title: "Semantic Cache (SoA)",
    body: "A struct-of-arrays cache that recognises a re-phrased question as the same question — 105x faster lookups and 40% faster repeat queries.",
  },
  {
    tag: "retrieval",
    module: "rag_engine.py",
    title: "RAG with citations",
    body: "PDF, TXT, and CSV ingestion with per-source scores and chunk previews. Documents persist to the database and survive a restart.",
  },
  {
    tag: "models",
    module: "model_registry.py",
    title: "Model registry",
    body: "A three-model catalogue with runtime hot-swap. Switch the active model from the UI without restarting the gateway or losing your session.",
  },
  {
    tag: "security",
    module: "security/guardrails.py",
    title: "Guardrails on every hop",
    body: "15+ prompt-injection patterns blocked, PII masked on the way out, secrets scanned before anything is returned. OWASP ASVS Level 2, 8 of 8 passing.",
  },
  {
    tag: "deploy",
    module: "k8s/deployment.yaml",
    title: "Runs where you run",
    body: "Docker, Kubernetes with PVCs and probes, an Electron desktop wrapper, or plain Gunicorn on a VM. Same stack, no hosted control plane.",
  },
];

export const METRICS = [
  { value: "<50ms", label: "TTFT p50", note: "with KV-cache warmup" },
  { value: "18ms", label: "Cached response", note: "semantic cache hit" },
  { value: "450/s", label: "Throughput", note: "requests, with caching" },
  { value: "≤2GB", label: "Memory footprint", note: "hard capped" },
];

export const COMPARISON = {
  columns: ["What you need", "With MicroLLM", "Cloud LLM APIs"],
  rows: [
    [
      "Where your prompts go",
      "Nowhere. Model, index, and audit log all sit on your disk",
      "To a vendor endpoint, retained under their policy",
    ],
    [
      "Cost per token",
      "Zero — you already own the machine",
      "Metered per 1K tokens, and it grows with adoption",
    ],
    [
      "Hardware needed",
      "2GB RAM, CPU only, hard capped",
      "None locally — you rent the inference forever",
    ],
    [
      "Repeat questions",
      "18ms from the semantic cache, 86% hit rate",
      "A full round trip, at full price, every time",
    ],
    [
      "Offline or air-gapped",
      "Works with the network cable unplugged",
      "Unusable without egress",
    ],
    [
      "Compliance evidence",
      "Audit trail in your own DB, ASVS L2 mapping in the repo",
      "A signed DPA and somebody else's SOC 2 report",
    ],
  ],
};

export const FAQS = [
  {
    number: "01",
    question: "Do I need a GPU?",
    answer:
      "No. The default build runs DeepSeek-R1-1.5B quantised to Q4 through llama-cpp-python on CPU, with the process memory hard-capped at 2GB. A GPU helps, but nothing in the stack requires one.",
  },
  {
    number: "02",
    question: "Does anything actually leave my machine?",
    answer:
      "The only outbound request in a normal install is the one-time model download from Hugging Face. After that you can cut the network entirely — inference, embeddings, retrieval, and auth are all local, and CORS is locked to an env-configured allowlist.",
  },
  {
    number: "03",
    question: "How is it secured?",
    answer:
      "JWT with bcrypt hashing that hard-fails at startup if the secret is missing or under 32 characters, user/admin RBAC per endpoint, Flask-Limiter on auth routes, prompt-injection and PII and secret-scanning filters around the model, and Nginx terminating TLS with HSTS and a self-only CSP.",
  },
  {
    number: "04",
    question: "Can I swap in a different model?",
    answer:
      "Yes. The model registry ships with a three-model catalogue and hot-swaps the active one at runtime via /api/models/switch. Any GGUF that llama-cpp-python can load and that fits your memory budget will work.",
  },
  {
    number: "05",
    question: "Is this production-ready or a demo?",
    answer:
      "v1.2.0 is the current release: seven phases complete, unit through end-to-end test suites in the repo, Docker Compose and Kubernetes manifests, backup scripts, and a metrics logger writing TTFT percentiles. Read CHANGELOG.md before you deploy it.",
  },
];
