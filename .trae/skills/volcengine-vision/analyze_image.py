import argparse
import sys
import os

# 将当前目录添加到 Python 路径，以便导入 volcengine_client
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from volcengine_client import VolcengineVision

def analyze(image_url, prompt, model):
    client = VolcengineVision()
    
    # 检查 API Key 是否已配置
    if not client.api_key:
        print("API Key not found. Please initialize first.")
        if not client.initialize():
            return

    print(f"Analyzing image: {image_url}")
    print(f"Prompt: {prompt}")
    print("Waiting for response...")
    
    result = client.analyze_image(image_url, prompt, model)
    
    print("\n" + "="*20 + " Analysis Result " + "="*20)
    print(result)
    print("="*57)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="使用火山引擎 Doubao Vision 模型分析图片")
    parser.add_argument("image_url", help="图片的 URL 地址")
    parser.add_argument("--prompt", default="图片主要讲了什么?", help="对图片的提问 (默认: '图片主要讲了什么?')")
    parser.add_argument("--model", default="doubao-1-5-vision-pro-32k-250115", help="使用的模型版本")
    
    args = parser.parse_args()
    
    analyze(args.image_url, args.prompt, args.model)
