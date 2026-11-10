#!/usr/bin/env bash
# One-time setup on a RunPod GPU Pod (PyTorch template) before running data/generate.py.
# Run from the repo root, which should live on the volume: /workspace/carbon-aware_multilingual_router_fork
#
#   export HF_TOKEN=hf_...      # accept the Tiny Aya and Gemma 4 licenses on Hugging Face first
#   bash scripts/runpod_setup.sh
#
# Safe to re-run after a Pod restart.
set -euo pipefail

VOLUME=${VOLUME:-/workspace}

if [ -z "${HF_TOKEN:-}" ]; then
    echo "HF_TOKEN is not set; gated models (Tiny Aya, Gemma 4) will fail to download." >&2
    exit 1
fi
if [ ! -d "$VOLUME" ]; then
    echo "$VOLUME not found; attach a volume so models and results survive a Pod stop." >&2
    exit 1
fi

# config/general.yaml caches models in ~/.cache/huggingface, which is on the container disk
# and is wiped when the Pod stops. Point it at the volume instead (~170 GB for all six models).
mkdir -p "$VOLUME/hf" ~/.cache
if [ ! -L ~/.cache/huggingface ]; then
    rm -rf ~/.cache/huggingface
    ln -s "$VOLUME/hf" ~/.cache/huggingface
fi

pip install -q -r requirements-gpu.txt
command -v tmux >/dev/null || { apt-get update -qq && apt-get install -y -qq tmux; }

nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
df -h "$VOLUME" | tail -1
python - <<'EOF'
from importlib.metadata import version
import torch
print(f"torch {torch.__version__}, transformers {version('transformers')}, zeus {version('zeus')}, "
      f"CUDA available: {torch.cuda.is_available()}")
EOF
echo "Setup done. Next: python scripts/preflight.py --download, then the pilot:"
echo "  python data/generate.py --items-per-dataset 5 --output results/pilot_runpod.jsonl"
