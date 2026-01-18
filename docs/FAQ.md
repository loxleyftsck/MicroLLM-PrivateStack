# Frequently Asked Questions (FAQ)

## General Questions

### Q: What is MicroLLM-PrivateStack?
A: MicroLLM-PrivateStack is an on-premise AI assistant designed for corporate environments that prioritize data privacy and security. It runs entirely on your local infrastructure without sending any data to external servers.

### Q: What makes it different from ChatGPT or other cloud AI services?
A: The key difference is data privacy. MicroLLM-PrivateStack:
- Runs 100% locally on your own hardware
- Never sends data to external servers
- Doesn't require internet connectivity for inference
- Gives you full control over the model and data
- Is fully auditable and compliant with enterprise regulations

### Q: What are the minimum system requirements?
A: 
- RAM: 2GB minimum (4GB recommended)
- CPU: Any modern x86-64 processor
- Storage: 2GB for model and application
- OS: Windows 10+, Ubuntu 20.04+, or macOS 12+

### Q: Can I use my own documents with the AI?
A: Yes! MicroLLM-PrivateStack includes a RAG (Retrieval-Augmented Generation) system. You can upload PDF, TXT, MD, and CSV files, and the AI will use them as context when answering your questions.

## Technical Questions

### Q: What LLM model does it use?
A: By default, it uses DeepSeek-R1-1.5B in quantized Q4 format. This model offers a good balance between capability and resource efficiency.

### Q: Can I use a different model?
A: Yes, any GGUF-format model compatible with llama.cpp can be used. Simply place the model file in the `models/` directory and update the `MODEL_PATH` environment variable.

### Q: How does the caching system work?
A: The system uses a Struct-of-Arrays (SoA) semantic cache that:
- Stores embeddings of previous queries
- Uses cosine similarity to find semantically similar questions
- Returns cached responses for similar questions (>95% similarity)
- Provides up to 3.5x faster response times for cached queries

### Q: Is GPU acceleration supported?
A: Yes, but it's optional. The system defaults to CPU-only mode for maximum compatibility. To enable GPU acceleration, set `n_gpu_layers` in the model configuration.

### Q: How do I deploy multiple instances for high availability?
A: Use Docker Compose with a load balancer:
1. Scale the `app` service: `docker-compose up --scale app=3`
2. Configure Nginx upstream to include all instances
3. Use Redis for shared cache across instances

## Security Questions

### Q: What security certifications does MicroLLM-PrivateStack support?
A: The system is designed for:
- GDPR compliance (data never leaves your premises)
- SOC 2 Type II readiness (audit logging, access controls)
- ISO 27001 alignment (security-first architecture)
- OWASP ASVS Level 2 compliance

### Q: How does prompt injection detection work?
A: The security guardrail system:
- Scans user inputs for known injection patterns
- Detects attempts to override system prompts
- Blocks malicious requests before they reach the LLM
- Logs all security events for audit purposes

### Q: Is my data encrypted?
A: Yes:
- Data in transit: TLS 1.2/1.3 via HTTPS
- Data at rest: AES-256-GCM encryption for uploaded documents
- Passwords: bcrypt hashing with automatic salting

### Q: How long is chat history stored?
A: Chat history is stored in the local SQLite database indefinitely by default. You can configure retention policies by modifying the database cleanup schedule.

## Troubleshooting

### Q: The model is loading slowly. What can I do?
A: Model loading typically takes 30-60 seconds. To speed it up:
- Ensure you have at least 2GB of free RAM
- Use an SSD instead of HDD
- Close other memory-intensive applications
- Consider using a smaller quantized model (Q2_K)

### Q: I'm getting "Out of Memory" errors. How do I fix this?
A: Try these solutions:
1. Reduce context length: Set `MODEL_CONTEXT_LENGTH=256`
2. Reduce batch size: Set `MODEL_BATCH=128`
3. Use a smaller model (Q2_K quantization)
4. Close other applications to free RAM
5. Add more RAM to your system

### Q: The API is returning 401 Unauthorized errors.
A: This means your JWT token is invalid or expired. Solutions:
1. Log in again to get a fresh token
2. Check that you're including the token correctly: `Authorization: Bearer <token>`
3. Verify that JWT_SECRET_KEY hasn't changed since the token was issued

### Q: Document upload is failing.
A: Check the following:
1. File size: Maximum 50MB per file
2. File type: Only PDF, TXT, MD, CSV are supported
3. File encoding: Text files should be UTF-8 encoded
4. Permissions: Ensure the server can write to the data directory

### Q: How do I backup my data?
A: Important files to backup:
- `backend/data/llm_database.db` - User accounts, chat history
- `data/rag_store.json` and `data/rag_store.npy` - RAG knowledge base
- `.env` files - Configuration (excluding secrets)
