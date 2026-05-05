# Chutes Vision API Reference

## API Endpoint

```
POST https://llm.chutes.ai/v1/chat/completions
```

## Authentication

```bash
# Set as environment variable
export CHUTES_API_TOKEN="your_token_here"

# Or pass directly in requests
Authorization: Bearer cpk_xxx.xxx.xxx
```

## Request Format

### Basic Vision Request

```json
{
  "model": "unsloth/gemma-3-12b-it",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "What is in this image?"
        },
        {
          "type": "image_url",
          "image_url": {
            "url": "data:image/jpeg;base64,<base64_encoded_image>"
          }
        }
      ]
    }
  ],
  "max_tokens": 1024,
  "temperature": 0.7
}
```

### Streaming Request

Add `"stream": true` to enable streaming responses.

## Response Format

### Standard Response

```json
{
  "id": "chatcmpl-xxx",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "unsloth/gemma-3-12b-it",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "<analysis text>"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 280,
    "completion_tokens": 400,
    "total_tokens": 680
  }
}
```

### Streaming Response

Each chunk:
```
data: {"id": "chatcmpl-xxx", "choices": [{"delta": {"content": "<partial_text>"}}]}
```

## Supported Image Formats

- JPEG/JPG (`image/jpeg`)
- PNG (`image/png`)
- WebP (`image/webp`)
- BMP (`image/bmp`)
- GIF (`image/gif`) - First frame only

## Parameters

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| `model` | string | - | `unsloth/gemma-3-12b-it` | Model identifier |
| `max_tokens` | integer | 1-4096 | 1024 | Maximum tokens |
| `temperature` | float | 0.0-2.0 | 0.7 | Randomness |
| `stream` | boolean | true/false | false | Enable streaming |

## Rate Limits

Check API documentation for current rate limits. Implement exponential backoff for retries.

## Error Responses

```json
{
  "error": {
    "message": "Error description",
    "type": "error_type",
    "code": "error_code"
  }
}
```

**Common Error Codes:**
- `invalid_api_key`: Incorrect or invalid API token
- `rate_limit_exceeded`: Too many requests
- `invalid_request`: Malformed request
- `server_error`: Internal API error

## Best Practices

1. **Prompt Engineering**: Be specific about what you want to know
2. **Image Size**: Resize large images (recommend < 5MB)
3. **Temperature**: Use lower values (0.3-0.5) for factual analysis
4. **Batch Processing**: Add delays between requests
5. **Error Handling**: Implement retry logic with exponential backoff

## Python Example

```python
import base64
import json
import urllib.request

# Read and encode image
with open("image.jpg", "rb") as f:
    image_data = base64.b64encode(f.read()).decode("utf-8")

# Build request
request = {
    "model": "unsloth/gemma-3-12b-it",
    "messages": [{
        "role": "user",
        "content": [
            {"type": "text", "text": "Describe this image"},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image_data}"
                }
            }
        ]
    }],
    "max_tokens": 1024,
    "temperature": 0.7
}

# Make request
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

req = urllib.request.Request(
    "https://llm.chutes.ai/v1/chat/completions",
    data=json.dumps(request).encode(),
    headers=headers
)

with urllib.request.urlopen(req) as response:
    result = json.loads(response.read())
    print(result["choices"][0]["message"]["content"])
```
