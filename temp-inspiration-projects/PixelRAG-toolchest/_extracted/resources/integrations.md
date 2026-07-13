# Third-Party Resources & Integrations

## Hugging Face — datasets & models
Chrisyichuan/madqa-training
Chrisyichuan/moca-colpali-training
Chrisyichuan/moca-visrag-ind-training
Chrisyichuan/moca-visrag-syn-training
Chrisyichuan/qwen3vl-4b-wiki-screenshot-multik-3x-lora
Chrisyichuan/screenshot-training
Chrisyichuan/screenshot-training-natural-filtered-4o-40k
Chrisyichuan/screenshot-training-natural-filtered-v2
Chrisyichuan/text-qa-pair
Chrisyichuan/wiki-screenshot-embedding-lora
Qwen/Qwen2-VL-2B-Instruct
Qwen/Qwen2-VL-72B-Instruct
Qwen/Qwen2.5-VL-3B-Instruct
Qwen/Qwen2.5-VL-72B-Instruct
Qwen/Qwen3-Embedding-0.6B
Qwen/Qwen3-VL-235B-A22B
Qwen/Qwen3-VL-2B
Qwen/Qwen3-VL-4B-Instruct
Qwen/Qwen3-VL-Embedding-2B
Qwen/Qwen3-VL-Reranker-8B
Qwen/Qwen3.5-0.8B
Qwen/Qwen3.5-35B-A3B
Qwen/Qwen3.5-4B
Qwen/Qwen3.5-4B-Instruct
Qwen/Qwen3.6-27B
Qwen/Qwen3.6-35B-A3B

## Core PyPI dependencies (root pyproject.toml)
- pillow, websockets, pymupdf, pyturbojpeg, cef-capi-py, anthropic (core)
- [embed]: torch, torchvision, transformers, faiss-cpu, numpy, tqdm
- [serve]: fastapi, uvicorn, faiss-cpu, transformers, torch, qwen-vl-utils, pydantic
- [index]: pyyaml, markdown (+ embed)
- [train]: torch==2.9.1, transformers==4.57.1, peft, accelerate, wandb, safetensors, datasets, openai
- [eval]: aiohttp, datasets, openai, selenium, litellm, fastmcp, trafilatura

## Key npm packages (web)
- next 16.1.7, react 19, @anthropic-ai/claude-agent-sdk, @anthropic-ai/claude-code, framer-motion, shadcn, base-ui/react, lucide-react

## Cloud / infra
- Vercel (web/ frontend hosting)
- GitHub Actions self-hosted runner (egress-only CD)
- nginx (blue-green search API upstream)
- systemd (pixelrag-api, pixelrag-api-green, pixelrag-agent services)
- Hugging Face Hub (FAISS indexes: StarTrail-org/pixelrag-faiss-indexes)
- boto3 [distributed] extra (S3)

## Auth / AI providers
- Anthropic (anthropic SDK + Claude Agent SDK — chat agent, reader model)
- OpenAI (openai SDK — eval grader, training query generation)
- vLLM / sglang (embedding serving backends)
