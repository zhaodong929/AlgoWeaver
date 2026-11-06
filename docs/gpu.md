# Local NVIDIA GPU Plan

The v0.1.0 extraction path uses a remote model API or deterministic mock mode. It does not require CUDA. Do not install a large CUDA/PyTorch stack until the actual GPU model, VRAM, driver, and local-inference target are known.

## 1. Inspect the machine

Windows PowerShell or Linux shell:

```bash
nvidia-smi
```

Record the GPU model, total VRAM, driver version, and current VRAM usage.

## 2. Choose the local inference mode

- If VRAM is limited or you mainly need local development, start with Ollama and a model that fits the GPU.
- If you need high-throughput serving and have sufficient VRAM, evaluate vLLM.
- If using remote OpenAI/DeepSeek/Qwen APIs, the local GPU can later accelerate embeddings, reranking, and document processing.

## 3. Keep the application interface unchanged

AlgoWeaver calls the model through the `ChatModel` protocol and LiteLLM adapter. A local OpenAI-compatible endpoint can be configured in `.env`:

```dotenv
ALGOWEAVER_LLM_MODE=litellm
ALGOWEAVER_LLM_MODEL=openai/<served-model-name>
ALGOWEAVER_LLM_API_BASE=http://localhost:8000/v1
ALGOWEAVER_LLM_API_KEY=<local-endpoint-key-if-required>
```

For Ollama, use the LiteLLM provider/model identifier supported by the installed LiteLLM version and the local Ollama endpoint.

## 4. GPU embedding and reranking are a later milestone

The retrieval milestone will benchmark Qwen3-Embedding and Qwen3-Reranker on the actual GPU before choosing a model size and batch size. This avoids guessing VRAM requirements and installing incompatible CUDA wheels.
