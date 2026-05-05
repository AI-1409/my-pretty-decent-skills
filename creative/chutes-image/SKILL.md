---
name: chutes-image
description: Generate images using the Chutes AI Image Generation API using the chutes-z-image-turbo model. 
version: 1.0.0
author: AVA
license: MIT
metadata:
  hermes:
    tags: [image-generation, chutes-ai, ai-art, turbo]
    related_skills: [chutes-vision, pixel-art, ascii-art]
required_environment_variables:
  - name: CHUTES_API_TOKEN
    prompt: Enter your Chutes API key
    required_for: Image generation API access
---

# Chutes Image Generation

Generate images using the Chutes AI Image Generation API with the chutes-z-image-turbo model for fast, high-quality image creation.

## Prerequisites

- Chutes API token (set as `CHUTES_API_TOKEN` environment variable)
- Internet connection for API calls

## Environment Variables

```bash
# Chutes API token for image generation
export CHUTES_API_TOKEN="cpk_xxx.xxx.xxx"

# Verify token is set
echo $CHUTES_API_TOKEN
```

## Usage

### Basic Image Generation

Generate an image from a text prompt:

```bash
python3 ~/.hermes/skills/creative/chutes-image/scripts/chutes_image.py \
  --prompt "a high quality photo of a sunrise over the mountains"
```

### Save to Specific File

```bash
python3 ~/.hermes/skills/creative/chutes-image/scripts/chutes_image.py \
  --prompt "a serene lake at sunset" \
  --output /tmp/lake_sunset.png
```

### Auto-Generate Filename

```bash
python3 ~/.hermes/skills/creative/chutes-image/scripts/chutes_image.py \
  --prompt "cyberpunk cityscape" \
  --auto-filename
```

### Image Quality Settings

```bash
python3 ~/.hermes/skills/creative/chutes-image/scripts/chutes_image.py \
  --prompt "a beautiful garden" \
  --quality high
```

### Custom Width/Height

```bash
python3 ~/.hermes/skills/creative/chutes-image/scripts/chutes_image.py \
  --prompt "a majestic eagle in flight" \
  --width 1024 \
  --height 768
```

## Script Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--prompt` | str | - | Text description of the image to generate (required) |
| `--output` | str | - | Path to save the generated image |
| `--auto-filename` | flag | False | Generate filename from prompt |
| `--width` | int | 1024 | Image width in pixels |
| `--height` | int | 1024 | Image height in pixels |
| `--quality` | str | `standard` | Image quality: standard, high, ultra |
| `--steps` | int | 20 | Number of generation steps (higher = better quality, slower) |
| `--guidance-scale` | float | 7.5 | Guidance scale (how closely to follow prompt) |
| `--seed` | int | Random | Random seed for reproducibility |
| `--model` | str | `chutes-z-image-turbo` | Model to use |
| `--api-token` | str | `$CHUTES_API_TOKEN` | Override API token |
| `--show-info` | flag | False | Show generation metadata |

## Generated Image Formats

The API returns PNG format by default. Supported output formats:
- **PNG** (default) — Lossless compression, best quality
- **JPEG** — Smaller file size, good for photos
- **WebP** — Modern format, good balance of size/quality

## Filename Auto-Generation

When using `--auto-filename`:

```
Prompt: "Sunset over mountains"
Output: sunset_over_mountains_20260428_123456.png

Prompt: "Cyberpunk city at night"
Output: cyberpunk_city_at_night_20260428_123457.png
```

Filename format: `{sanitized_prompt}_{timestamp}.png`

## Quality Settings

| Quality | Steps | Description |
|---------|-------|-------------|
| **standard** | 20 | Good quality, fast generation |
| **high** | 40 | Better quality, slower |
| **ultra** | 60 | Best quality, slowest |

## Guidance Scale

Controls how strictly the model follows your prompt:

- **3.0-5.0** — More creative, may deviate from prompt
- **7.0-9.0** — Balanced (default: 7.5)
- **10.0-15.0** — Strict adherence to prompt

## Common Dimensions

| Use Case | Width | Height | Aspect Ratio |
|----------|-------|--------|--------------|
| Square | 1024 | 1024 | 1:1 |
| Landscape (16:9) | 1024 | 576 | 16:9 |
| Portrait (9:16) | 576 | 1024 | 9:16 |
| Landscape (4:3) | 1024 | 768 | 4:3 |
| Portrait (3:4) | 768 | 1024 | 3:4 |
| Wallpaper (21:9) | 1344 | 576 | 21:9 |

## Workflows

### Generate and Send via Matrix

```bash
# Generate image
IMAGE_PATH=$(python3 ~/.hermes/skills/creative/chutes-image/scripts/chutes_image.py \
  --prompt "a peaceful forest stream" \
  --auto-filename \
  2>&1 | grep "saved to" | awk '{print $3}')

# Send to Matrix
python3 ~/.hermes/skills/social-media/matrix-media-sender/scripts/matrix_media_sender.py \
  --file "$IMAGE_PATH" \
  --message "Generated image of forest stream 🌲"
```

### Batch Generation for Variations

```bash
# Generate multiple variations with different seeds
for seed in 42 123 456 789; do
  python3 ~/.hermes/skills/creative/chutes-image/scripts/chutes_image.py \
    --prompt "abstract geometric patterns in blue" \
    --seed $seed \
    --auto-filename
done
```

### High-Quality Portrait

```bash
python3 ~/.hermes/skills/creative/chutes-image/scripts/chutes_image.py \
  --prompt "professional portrait of a woman, soft lighting, blurred background, 85mm lens" \
  --width 768 \
  --height 1024 \
  --quality ultra \
  --output portrait.png
```

### Reproducible Generation

```bash
# Same seed produces same image
python3 ~/.hermes/skills/creative/chutes-image/scripts/chutes_image.py \
  --prompt "a red telephone booth in London" \
  --seed 1337 \
  --output telephone_booth_v1.png

# Later, regenerate same image
python3 ~/.hermes/skills/creative/chutes-image/scripts/chutes_image.py \
  --prompt "a red telephone booth in London" \
  --seed 1337 \
  --output telephone_booth_v2.png
```

## API Details

**Endpoint:** `https://chutes-z-image-turbo.chutes.ai/generate`

**Method:** `POST`

**Headers:**
- `Authorization: Bearer cpk_xxx.xxx.xxx`
- `Content-Type: application/json`

**Request Body:**
```json
{
  "prompt": "text description of the image",
  "width": 1024,
  "height": 1024,
  "steps": 20,
  "guidance_scale": 7.5,
  "seed": 42
}
```

**Response:**
- Binary image data (PNG format)
- Or JSON with image data URL

## Troubleshooting

### **"API token not found"**

Set the environment variable:

```bash
export CHUTES_API_TOKEN="cpk_xxx.xxx.xxx"
echo $CHUTES_API_TOKEN  # Verify it's set
```

### **"Network error"**

Check internet connection and API availability:

```bash
curl -X POST \
  https://chutes-z-image-turbo.chutes.ai/generate \
  -H "Authorization: Bearer $CHUTES_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "test"}' \
  --head
```

### **"Invalid prompt"**

Ensure your prompt is descriptive and specific:

```bash
# Too vague
--prompt "landscape"

# Better
--prompt "alpine meadow at sunrise with wildflowers and snow-capped mountains"
```

### **"Image generation failed"**

Try simpler prompts or different parameters:

```bash
# Reduce complexity
--prompt "simple mountain landscape"

# Reduce steps (faster processing)
--steps 15

# Use standard quality
--quality standard
```

### **"Out of memory"**

Reduce image resolution:

```bash
--width 512 --height 512
```

## Prompt Engineering Tips

### Be Specific
```
Good: "A golden retriever dog running through a wheat field at sunset, photorealistic, warm golden hour lighting, motion blur"
Poor: "dog running"
```

### Include Art Style
```
Good: "abstract painting in the style of Kandinsky with bold geometric shapes and vibrant colors"
Poor: "abstract art"
```

### Add Technical Details
```
Good: "product photography of coffee beans, 100mm macro lens, softbox lighting, wooden table background, depth of field"
Poor: "coffee beans"
```

### Use Camera Terminology
```
Good: "architectural shot of a modern glass building, 24mm wide-angle lens, blue sky, reflections, cinematic composition"
Poor: "glass building"
```

### Include Lighting
```
Good: "portrait of elderly fisherman, natural window light, weathered face, sepia tones, evocative mood"
Poor: "fisherman"
```

## Best Practices

1. **Start Simple** — Test with basic prompts before adding complexity
2. **Iterate** — Refine prompts based on results
3. **Use Seeds** — Save good seeds for reproducibility
4. **Experiment** — Try different guidance scales and steps
5. **Batch Test** — Generate variations to find best result
6. **Organize** — Use descriptive filenames or directories
7. **Monitor Usage** — Track API usage and costs

## Integration Examples

### With Vision Analysis

```bash
# Generate image
python3 ~/.hermes/skills/creative/chutes-image/scripts/chutes_image.py \
  --prompt "a cozy coffee shop interior" \
  --output coffee_shop.png

# Analyze the result
python3 ~/.hermes/skills/vision/chutes-vision/scripts/chutes_vision.py \
  --image coffee_shop.png \
  --prompt "Describe the mood and atmosphere of this image"
```

### With Image Transformation

```bash
# Generate base image
python3 ~/.hermes/skills/creative/chutes-image/scripts/chutes_image.py \
  --prompt "simple geometric mandala" \
  --output mandala.png

# Convert to pixel art
python3 ~/.hermes/skills/creative/pixel-art/scripts/pixel_art.py \
  --image mandala.png \
  --pixel-size 8 \
  --output mandala_pixels.png
```

### Automated Content Pipeline

```bash
#!/bin/bash
# Generate themed image set

THEME="cyberpunk"
PROMPTS=(
  "futuristic city skyline at night with neon lights"
  "cybernetic character portrait with glowing implants"
  "flying vehicle traffic through holographic advertisements"
)

for prompt in "${PROMPTS[@]}"; do
  echo "Generating: $prompt"
  python3 ~/.hermes/skills/creative/chutes-image/scripts/chutes_image.py \
    --prompt "$prompt" \
    --auto-filename
done
```

## Limitations

- API may have rate limits or quotas
- Response time varies with image size and quality settings
- Specific object rendering may vary (people, text, logos)
- Very complex prompts may require more steps/tuning

## Costs

Monitor your API usage:
- Check Chutes dashboard for current quotas
- Higher quality/steps settings consume more credits
- Batch processing accumulates costs quickly
- Implement rate limiting in automated workflows

## Version History

- **v1.0.0** (2026-04-28): Initial release with chutes-z-image-turbo model support
