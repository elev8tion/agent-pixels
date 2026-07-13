def build_readme(comp, step, judge, config, base_judge):
    return f"""---
license: apache-2.0
library_name: peft
base_model: Qwen/Qwen3-VL-4B-Instruct
tags:
- peft
- lora
- qwen3-vl
- screenshot-qa
- compressed-images
- {comp}-compression
pipeline_tag: image-text-to-text
---

# Qwen3-VL-4B Wikipedia Screenshot QA LoRA — {comp} compression

LoRA adapter for [Qwen3-VL-4B-Instruct](https://huggingface.co/Qwen/Qwen3-VL-4B-Instruct) fine-tuned to answer natural-language questions about Wikipedia-screenshot chunks, specifically on images compressed by **{comp}** (each dim scaled by 1/√{comp[:-1]}).

## Performance (GPT-4.1 LLM-judge on 500 test examples)

| Setup | LLM-judge |
|---|---|
| Uncompressed (0x) ceiling, base Qwen3-VL-4B | 0.958 |
| **This adapter @ {comp}** | **{judge:.3f}** |
| Base Qwen3-VL-4B @ {comp} (no SFT) | {base_judge:.3f} |

SFT gain over base at {comp}: **+{judge - base_judge:.3f}** ({100 * (judge - base_judge) / base_judge:.1f}% relative).

## Training config

- Method: LoRA ({config})
- Base model: `Qwen/Qwen3-VL-4B-Instruct`
- Checkpoint: step `{step}`
- Framework: [LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory) (fork)
- Trained on 4× H100 80GB (DeepSpeed ZeRO-2, bf16)
- Dataset: Wikipedia screenshot-QA pairs compressed with PIL LANCZOS

## Data preparation

Training images were downscaled by `1/sqrt({comp[:-1]})` per dimension using PIL LANCZOS, e.g. a 1200×800 screenshot becomes {int(1200 / int(comp[:-1]) ** 0.5)}×{int(800 / int(comp[:-1]) ** 0.5)} px (~{100 / int(comp[:-1]):.0f}% of original pixels).

## Usage

```python
from transformers import AutoProcessor, Qwen3VLForConditionalGeneration
from peft import PeftModel
import torch

base = "Qwen/Qwen3-VL-4B-Instruct"
adapter = "{USER}/qwen3vl-4b-wiki-screenshot-{comp}-lora"

model = Qwen3VLForConditionalGeneration.from_pretrained(base, torch_dtype=torch.bfloat16).cuda()
model = PeftModel.from_pretrained(model, adapter).merge_and_unload()
processor = AutoProcessor.from_pretrained(base)

# PIL image already compressed to {comp}
messages = [{{"role": "user", "content": [
    {{"type": "image", "image": your_compressed_image}},
    {{"type": "text",  "text": your_question}},
]}}]
# ... standard Qwen3-VL inference
```

## Notes / limitations

- The adapter is specific to the **{comp} compression level** and does not necessarily generalize to higher or lower compression. Use the adapter whose level matches your deployment.
- At {comp}, SFT recovers {100 * (judge - base_judge) / (0.958 - base_judge):.0f}% of the compression-induced accuracy drop relative to uncompressed Qwen3-VL-4B.
- See the full experiment matrix and findings in `sft/RESULTS.md` of the source repo.
"""
