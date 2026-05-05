#!/usr/bin/env python3
"""
Chutes Vision - Image analysis using Chutes AI API
Supports local files, URLs, and various analysis presets
"""

import argparse
import base64
import json
import os
import sys
import urllib.request
from pathlib import Path
from typing import Optional


# API Configuration
CHUTES_API_URL = "https://llm.chutes.ai/v1/chat/completions"
CHUTES_API_TOKEN = os.environ.get("CHUTES_API_TOKEN")

# Analysis Presets
PRESETS = {
    "detailed": "Provide a comprehensive, detailed description of this image. Describe all visible elements including people, objects, colors, lighting, composition, and any text. Be as thorough as possible.",
    "brief": "Provide a concise 100-word description of this image, focusing on the main subjects and overall impression.",
    "ocr": "Extract and transcribe all text visible in this image. If no text is present, state that clearly.",
    "objects": "List and describe all objects visible in this image. Be specific about what each object is and its position.",
    "colors": "Analyze the color palette of this image. Describe the dominant colors, color harmony, and how colors contribute to the mood.",
    "composition": "Analyze the composition and framing of this image. Discuss balance, leading lines, depth, and visual hierarchy.",
    "safety": "Analyze this image for any concerning content including violence, adult material, or safety issues. If safe, confirm it explicitly."
}


def read_api_token():
    """Read API token from environment or argument"""
    token = os.environ.get("CHUTES_API_TOKEN")
    return token


def verify_api_token(token):
    """Verify API token is present and properly formatted"""
    if not token:
        print("Error: API token not found.", file=sys.stderr)
        print("Set CHUTES_API_TOKEN environment variable or use --api-token", file=sys.stderr)
        sys.exit(1)
    
    if not token.startswith(("cpk_", "Bearer ")) and "." not in token:
        print("Warning: API token format looks unusual. Verify your token is correct.", file=sys.stderr)
    
    if token.startswith("Bearer "):
        token = token.replace("Bearer ", "")
    
    return token


def encode_image_to_base64(image_path: str) -> str:
    """Encode image file to base64 string"""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    except FileNotFoundError:
        print(f"Error: Image file not found: {image_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading image: {e}", file=sys.stderr)
        sys.exit(1)


def download_image_from_url(url: str) -> tuple[str, str]:
    """Download image from URL and return (base64_data, content_type)"""
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            content_type = response.headers.get("Content-Type", "image/jpeg")
            image_data = response.read()
            return base64.b64encode(image_data).decode("utf-8"), content_type
    except urllib.error.URLError as e:
        print(f"Error: Failed to download image from URL: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error downloading image: {e}", file=sys.stderr)
        sys.exit(1)


def detect_mime_type(image_path: str) -> str:
    """Detect image MIME type from file extension"""
    ext = Path(image_path).suffix.lower()
    mime_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".bmp": "image/bmp",
        ".gif": "image/gif"
    }
    return mime_types.get(ext, "image/jpeg")


def build_api_request(
    base64_image: str,
    mime_type: str,
    prompt: str,
    model: str,
    max_tokens: int,
    temperature: float
) -> dict:
    """Build API request payload"""
    request = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": max_tokens,
        "temperature": temperature
    }
    return request


def make_api_request(request: dict, api_token: str, stream: bool = False) -> dict:
    """Make API request to Chutes AI"""
    if stream:
        request["stream"] = True
    
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    try:
        req = urllib.request.Request(
            CHUTES_API_URL,
            data=json.dumps(request).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        
        with urllib.request.urlopen(req, timeout=120) as response:
            if stream:
                # Handle streaming response
                response_text = ""
                for chunk in response:
                    if chunk:
                        # Remove "data: " prefix if present
                        chunk_str = chunk.decode("utf-8")
                        if chunk_str.startswith("data: "):
                            chunk_str = chunk_str[6:]
                        if chunk_str.strip() == "[DONE]":
                            break
                        try:
                            data = json.loads(chunk_str)
                            delta = data.get("choices", [{}])[0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                print(content, end="", flush=True)
                                response_text += content
                        except json.JSONDecodeError:
                            pass
                print()  # Final newline
                return {"content": response_text, "streamed": True}
            else:
                # Handle non-streaming response
                response_data = json.loads(response.read().decode("utf-8"))
                return response_data
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"API Error {e.code}: {error_body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Network Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error during API request: {e}", file=sys.stderr)
        sys.exit(1)


def extract_content(response: dict, stream: bool) -> str:
    """Extract content from API response"""
    if stream:
        return response.get("content", "")
    else:
        try:
            return response.get("choices", [{}])[0].get("message", {}).get("content", "")
        except (IndexError, KeyError):
            print("Error: Unexpected API response format", file=sys.stderr)
            sys.exit(1)


def print_usage_stats(response: dict, stream: bool):
    """Print token usage statistics"""
    if not stream and "usage" in response:
        usage = response["usage"]
        print(f"\n=== Usage ===", file=sys.stderr)
        print(f"Prompt tokens: {usage.get('prompt_tokens', 0)}", file=sys.stderr)
        print(f"Completion tokens: {usage.get('completion_tokens', 0)}", file=sys.stderr)
        print(f"Total tokens: {usage.get('total_tokens', 0)}", file=sys.stderr)


def save_output(content: str, output_path: str):
    """Save analysis to file"""
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"\nAnalysis saved to: {output_path}", file=sys.stderr)
    except Exception as e:
        print(f"Error saving output: {e}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze images using Chutes AI Vision API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --image photo.jpg --prompt "Describe this image"
  %(prog)s --image photo.png --preset detailed
  %(prog)s --url https://example.com/image.jpg --preset brief
  %(prog)s --image photo.jpg --stream --prompt "What do you see?"
  
Presets: detailed, brief, ocr, objects, colors, composition, safety
        """
    )
    
    # Input sources (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--image", help="Path to local image file")
    input_group.add_argument("--url", help="URL to fetch image from")
    
    # Analysis parameters
    parser.add_argument("--prompt", default="What is in this image? Describe it in detail.",
                        help="Analysis question (default: detailed description)")
    parser.add_argument("--preset", help="Use built-in prompt preset")
    parser.add_argument("--model", default="unsloth/gemma-3-12b-it",
                        help="Model to use (default: unsloth/gemma-3-12b-it)")
    parser.add_argument("--temperature", type=float, default=0.7,
                        help="Temperature 0.0-2.0 (default: 0.7)")
    parser.add_argument("--max-tokens", type=int, default=1024,
                        help="Maximum tokens in response (default: 1024)")
    
    # Output options
    parser.add_argument("--stream", action="store_true",
                        help="Stream responses in real-time")
    parser.add_argument("--output", help="Save analysis to file")
    parser.add_argument("--api-token", help="Override API token (or use CHUTES_API_TOKEN env var)")
    parser.add_argument("--stats", action="store_true",
                        help="Show token usage statistics")
    
    args = parser.parse_args()
    
    # Get API token
    api_token = args.api_token or read_api_token()
    api_token = verify_api_token(api_token)
    
    # Handle preset
    prompt = args.prompt
    if args.preset:
        if args.preset not in PRESETS:
            print(f"Error: Unknown preset '{args.preset}'", file=sys.stderr)
            print(f"Available presets: {list(PRESETS.keys())}", file=sys.stderr)
            sys.exit(1)
        prompt = PRESETS[args.preset]
    
    # Load image
    if args.image:
        if not os.path.exists(args.image):
            print(f"Error: Image file not found: {args.image}", file=sys.stderr)
            sys.exit(1)
        base64_image = encode_image_to_base64(args.image)
        mime_type = detect_mime_type(args.image)
        image_source = f"file: {args.image}"
    else:
        base64_image, mime_type = download_image_from_url(args.url)
        image_source = f"url: {args.url}"
    
    print(f"Analyzing {image_source}...", file=sys.stderr)
    print(f"Model: {args.model}", file=sys.stderr)
    print(f"Prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}", file=sys.stderr)
    print("---", file=sys.stderr)
    
    # Build and make API request
    request = build_api_request(
        base64_image,
        mime_type,
        prompt,
        args.model,
        args.max_tokens,
        args.temperature
    )
    
    response = make_api_request(request, api_token, args.stream)
    
    # Extract and output content
    content = extract_content(response, args.stream)
    
    if not args.stream:
        print(content)
    
    # Save output if requested
    if args.output:
        save_output(content, args.output)
    
    # Print usage stats if requested
    if args.stats:
        print_usage_stats(response, args.stream)


if __name__ == "__main__":
    main()
