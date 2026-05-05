---
name: chutes-vision
description: Image analysis and visual understanding using Chutes AI API with multimodal LLM support
author: AVA
created: 2026-04-26
version: 1.0.0
metadata:
  hermes:
    tags: [vision, image-analysis, chutes-ai, multimodal, ocr]
required_environment_variables:
  - name: CHUTES_API_TOKEN
    prompt: "Enter your Chutes API key"
    required_for: "LLM API access"
---

# Chutes Vision

Image analysis skill using the Chutes AI API for visual understanding with multimodal LLMs.

## Prerequisites

- Chutes AI API token (set as `CHUTES_API_TOKEN` environment variable or pass to script)

## Installation

1. Set your API token:
```bash
export CHUTES_API_TOKEN="cpk_xxx.xxx.xxx"
```

Or add to `~/.bashrc`:
```bash
echo 'export CHUTES_API_TOKEN="cpk_xxx.xxx.xxx"' >> ~/.bashrc
source ~/.bashrc
```

## Setup

The `CHUTES_API_TOKEN` environment variable must be set before using this skill. Get your API token from the Chutes AI platform (https://chutes.ai).

```bash
# Verify token is set
echo $CHUTES_API_TOKEN
```

## Usage

### Basic Image Analysis

Analyze a local image file:

```bash
python3 ~/.hermes/skills/chutes-vision/scripts/chutes_vision.py \
  --image /path/to/image.png \
  --prompt "What is in this image? Describe it in detail."
```

Analyze an image from URL:

```bash
python3 ~/.hermes/skills/chutes-vision/scripts/chutes_vision.py \
  --url https://example.com/image.jpg \
  --prompt "What objects are visible in this image?"
```

### Advanced Options

Use specific model:

```bash
python3 ~/.hermes/skills/chutes-vision/scripts/chutes_vision.py \
  --image /path/to/image.png \
  --model unsloth/gemma-3-12b-it \
  --prompt "Describe the colors and composition."
```

Adjust response parameters:

```bash
python3 ~/.hermes/skills/chutes-vision/scripts/chutes_vision.py \
  --image /path/to/image.png \
  --temperature 0.5 \
  --max-tokens 2048 \
  --prompt "Provide a very detailed analysis."
```

### Analysis Presets

Use built-in analysis presets:

```bash
# Detailed description
python3 ~/.hermes/skills/chutes-vision/scripts/chutes_vision.py \
  --image photo.jpg --preset detailed

# Brief summary
python3 ~/.hermes/skills/chutes-vision/scripts/chutes_vision.py \
  --image photo.jpg --preset brief

# OCR/text extraction
python3 ~/.hermes/skills/chutes-vision/scripts/chutes_vision.py \
  --image photo.jpg --preset ocr

# Object detection
python3 ~/.hermes/skills/chutes-vision/scripts/chutes_vision.py \
  --image photo.jpg --preset objects
```

Supported presets: `detailed`, `brief`, `ocr`, `objects`, `colors`, `composition`, `safety`

### Streaming Output

Stream responses in real-time:

```bash
python3 ~/.hermes/skills/chutes-vision/scripts/chutes_vision.py \
  --image /path/to/image.png \
  --stream \
  --prompt "What do you see?"
```

## Script Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--image` | str | - | Path to local image file |
| `--url` | str | - | URL to fetch image from |
| `--prompt` | str | "What is in this image?" | Analysis question |
| `--model` | str | `Qwen/Qwen2.5-VL-32B-Instruct` | Model to use |

**Working models:**
- `Qwen/Qwen2.5-VL-32B-Instruct` — Tested and confirmed for web UI screenshots, visual QA, and accessibility analysis. Recommended for UI/UX analysis.
- `unsloth/gemma-3-12b-it` — General image analysis
- Other vision-capable models from Chutes AI may work; test before production use.
| `--temperature` | float | 0.7 | Temperature (0.0-2.0) |
| `--max-tokens` | int | 1024 | Max tokens in response |
| `--stream` | flag | False | Stream responses |
| `--preset` | str | - | Use built-in prompt preset |
| `--api-token` | str | `$CHUTES_API_TOKEN` | Override API token |

## Presets

- `detailed`: Comprehensive visual analysis
- `brief`: Concise 100-word description  
- `ocr`: Extract text from image
- `objects`: List visible objects
- `colors`: Describe color palette
- `composition`: Analyze composition and framing
- `safety`: Content moderation check

## Supported Image Formats

- JPEG/JPG
- PNG
- WebP
- BMP
- GIF (first frame only)

## Error Handling

The script provides clear error messages for:
- Missing API token
- Invalid image files
- Network failures
- API errors
- Rate limiting

## Example Workflows

### Batch Analysis

Analyze multiple images:

```bash
for img in /path/to/images/*.jpg; do
    python3 ~/.hermes/skills/chutes-vision/scripts/chutes_vision.py \
      --image "$img" \
      --preset brief \
      --output "${img%.jpg}_analysis.txt"
done
```

### URL Processing

Fetch and analyze images from URLs:

```bash
cat image_urls.txt | while read url; do
    python3 ~/.hermes/skills/chutes-vision/scripts/chutes_vision.py \
      --url "$url" \
      --prompt "Describe the main subject."
done
```

### Automated Monitoring

Use in cron jobs for scheduled image analysis:

```bash
# Daily analysis of new images
find /data/images -type f -mtime -1 -name "*.png" | \
  xargs -I {} python3 ~/.hermes/skills/chutes-vision/scripts/chutes_vision.py \
    --image {} \
    --preset detailed \
    --output "{}_analysis.txt"
```

## Tips

1. **API Token**: Keep secure; never commit to git. Use environment variables.
2. **Large Images**: API has size limits; consider resizing large photos.
3. **Rate Limits**: Implement delays between batch requests.
4. **Prompt Engineering**: Be specific about what you want to know.
5. **Cost Monitoring**: Track token usage; images require more tokens than text.

## Troubleshooting

**"API token not found"**: Set `CHUTES_API_TOKEN` environment variable or use `--api-token`

**"Failed to read image"**: Check file path and format; verify file exists

**"Rate limit exceeded"**: Add delays between requests or contact Chutes AI

Poor quality analysis: Try different models, adjust temperature, or improve prompt specificity

**Media file path issues**: When using Hermes with Matrix, the Matrix adapter can only embed images from the writable image cache directory (`/root/.hermes/cache/images/`). Images in read-only locations (like `/mnt/vault`) or dynamically generated files outside the cache directory may not display inline. Use the local file path shown in the output to access the image directly if inline embedding is not available.

**"Image file not found"**: **CRITICAL: Matrix images are cached at `~/.hermes/cache/images/` ( `/root/.hermes/cache/images/`) NOT `/mnt/vault/.hermes/image_cache/`.** The Matrix adapter uses a different cache directory. Always check `~/.hermes/cache/images/` first for images sent via Matrix. Verify the correct path with `ls -la ~/.hermes/cache/images/` before running the script.

## API Reference

**Endpoint**: `https://llm.chutes.ai/v1/chat/completions`

**Method**: POST

**Headers**:
- `Authorization: Bearer cpk_xxx.xxx.xxx`
- `Content-Type: application/json`

**Body**: OpenAI-compatible format with multimodal content support

## Version History

- v1.0.0 (2026-04-26): Initial release with vision analysis support
