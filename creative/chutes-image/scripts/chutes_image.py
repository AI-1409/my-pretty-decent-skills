#!/usr/bin/env python3
"""
Chutes Image Generation - Generate images using Chutes AI API
Uses the chutes-z-image-turbo model for fast image generation
"""

import argparse
import base64
import datetime
import hashlib
import json
import os
import re
import sys
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional, Tuple


class ChutesImageGenerator:
    def __init__(
        self,
        api_token: Optional[str] = None,
        model: str = "chutes-z-image-turbo"
    ):
        self.api_token = api_token or os.environ.get("CHUTES_API_TOKEN", "")
        self.model = model
        self.api_url = "https://chutes-z-image-turbo.chutes.ai/generate"
        
    def generate(
        self,
        prompt: str,
        **kwargs
    ) -> Tuple[Optional[bytes], Optional[dict]]:
        """
        Generate an image from a text prompt.
        Returns (image_data, metadata) tuple.
        """
        if not self.api_token:
            raise ValueError("CHUTES_API_TOKEN environment variable not set")
        
        # Build request payload (only prompt is supported by current API)
        payload = {
            "prompt": prompt
        }
        
        # Make API request
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        print(f"Generating image...")
        print(f"  Prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
        print()
        
        try:
            req = urllib.request.Request(
                self.api_url,
                data=json.dumps(payload).encode(),
                headers=headers,
                method="POST"
            )
            
            # Send request with timeout (image generation can take time)
            resp = urllib.request.urlopen(req, timeout=300)
            
            if resp.status == 200:
                content_type = resp.headers.get("Content-Type", "")
                
                # Direct binary image response (most common)
                if "image/" in content_type:
                    image_data = resp.read()
                    # Extract metadata from response headers if available
                    metadata = {
                        "format": content_type,
                        "invocation_id": resp.headers.get("x-chutes-invocationid"),
                        "quota_remaining": resp.headers.get("x-chutes-quota-remaining")
                    }
                    return image_data, metadata
                
                # JSON response (may contain image data URL)
                elif "application/json" in content_type:
                    response_body = resp.read().decode()
                    response_data = json.loads(response_body)
                    
                    # Check for different response formats
                    if "image" in response_data:
                        image_str = response_data["image"]
                        if image_str.startswith("data:image"):
                            # Data URL format: data:image/png;base64,ABC...
                            image_data = base64.b64decode(
                                image_str.split(",", 1)[1]
                            )
                            metadata = response_data.get("metadata", {})
                            return image_data, metadata
                        else:
                            # Raw base64
                            image_data = base64.b64decode(image_str)
                            metadata = response_data.get("metadata", {})
                            return image_data, metadata
                    elif "data" in response_data:
                        image_str = response_data["data"]
                        if image_str.startswith("data:image"):
                            image_data = base64.b64decode(
                                image_str.split(",", 1)[1]
                            )
                            metadata = response_data.get("metadata", {})
                            return image_data, metadata
                        else:
                            image_data = base64.b64decode(image_str)
                            metadata = response_data.get("metadata", {})
                            return image_data, metadata
                else:
                    print(f"❌ Unknown response format: {content_type}", file=sys.stderr)
                    return None, None
            else:
                print(f"❌ API error: HTTP {resp.status}", file=sys.stderr)
                try:
                    error_body = resp.read().decode()
                    print(f"   Response: {error_body}", file=sys.stderr)
                except:
                    pass
                return None, None
                
        except urllib.error.HTTPError as e:
            print(f"❌ HTTP Error: {e.code} {e.reason}", file=sys.stderr)
            try:
                error_body = e.read().decode()
                print(f"   Response: {error_body}", file=sys.stderr)
            except:
                pass
            return None, None
        except Exception as e:
            print(f"❌ Request failed: {e}", file=sys.stderr)
            return None, None
    
    def sanitize_filename(self, text: str) -> str:
        """
        Convert prompt text to safe filename.
        """
        # Remove special characters, replace spaces with underscores
        safe = re.sub(r'[^\w\s-]', '', text.lower())
        safe = re.sub(r'[\s]+', '_', safe)
        safe = safe.strip('-_')
        
        # Limit length
        safe = safe[:50]
        
        return safe
    
    def save_image(
        self,
        image_data: bytes,
        output_path: Optional[str] = None,
        prompt: Optional[str] = None,
        format: str = "png"
    ) -> str:
        """
        Save image data to file.
        Returns the file path where image was saved.
        """
        if output_path:
            save_path = output_path
        elif prompt:
            # Auto-generate filename from prompt
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = self.sanitize_filename(prompt)
            save_path = f"{safe_name}_{timestamp}.{format}"
        else:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = f"chutes_image_{timestamp}.{format}"
        
        try:
            with open(save_path, "wb") as f:
                f.write(image_data)
            
            file_size = len(image_data)
            print(f"✅ Image saved to: {save_path}")
            print(f"   Size: {file_size:,} bytes ({file_size / 1024:.1f} KB)")
            
            return save_path
        except Exception as e:
            print(f"❌ Failed to save image: {e}", file=sys.stderr)
            return ""


def parse_quality(quality: str) -> int:
    """
    Convert quality string to steps count.
    """
    quality_map = {
        "standard": 20,
        "high": 40,
        "ultra": 60
    }
    return quality_map.get(quality.lower(), 20)


def main():
    parser = argparse.ArgumentParser(
        description="Generate images using Chutes AI Image Generation API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --prompt "a high quality photo of a sunrise over the mountains"
  %(prog)s --prompt "cyberpunk cityscape" --width 1024 --height 768 --auto-filename
  %(prog)s --prompt "beautiful garden" --quality high --output garden.png
  %(prog)s --prompt "abstract painting" --seed 1337 --reproducible
        """
    )
    
    # Prompt (required)
    parser.add_argument("--prompt", "-p", help="Text description of the image to generate")
    
    # Output options
    parser.add_argument("--output", "-o", help="Path to save the generated image")
    parser.add_argument("--auto-filename", action="store_true",
                        help="Generate filename from prompt with timestamp")
    
    # Configuration
    parser.add_argument("--model", default="chutes-z-image-turbo",
                        help="Model to use (default: chutes-z-image-turbo)")
    parser.add_argument("--api-token", help="Override CHUTES_API_TOKEN")
    parser.add_argument("--show-info", action="store_true",
                        help="Show generation metadata")
    
    args = parser.parse_args()
    
    # Validate prompt
    if not args.prompt:
        print("❌ Error: --prompt is required", file=sys.stderr)
        parser.print_help()
        sys.exit(1)
    
    # Create generator instance
    generator = ChutesImageGenerator(
        api_token=args.api_token,
        model=args.model
    )
    
    # Generate image
    print()
    image_data, metadata = generator.generate(
        prompt=args.prompt
    )
    
    if not image_data:
        print(f"\n❌ Failed to generate image", file=sys.stderr)
        sys.exit(1)
    
    # Save image
    output_path = generator.save_image(
        image_data,
        output_path=args.output,
        prompt=args.prompt if args.auto_filename else None
    )
    
    if not output_path:
        print(f"\n❌ Failed to save image", file=sys.stderr)
        sys.exit(1)
    
    # Show metadata if requested
    if args.show_info:
        print(f"\n=== Generation Metadata ===")
        if metadata:
            for key, value in metadata.items():
                print(f"{key}: {value}")
        else:
            print("No metadata available")
        
        # Generate hash for future reference
        image_hash = hashlib.sha256(image_data).hexdigest()[:16]
        print(f"Image hash: {image_hash}")
    
    print()
    print(f"=== SUMMARY ===")
    print(f"Prompt: {args.prompt}")
    print(f"Saved to: {output_path}")
    print()


if __name__ == "__main__":
    main()
