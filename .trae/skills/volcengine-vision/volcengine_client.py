import json
import os
import requests

CONFIG_FILE = os.path.expanduser("~/.volcengine_config.json")
LOCAL_CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".volcengine_config.json")
DEFAULT_MODEL = "doubao-seed-1-6-vision-250815"
API_ENDPOINT = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"

class VolcengineVision:
    def __init__(self):
        self.config = self._load_config()
        self.api_key = self.config.get("ark_api_key")
        
    def _load_config(self):
        # 优先读取本地配置
        if os.path.exists(LOCAL_CONFIG_FILE):
             try:
                with open(LOCAL_CONFIG_FILE, "r") as f:
                    return json.load(f)
             except Exception:
                pass

        # 然后读取用户目录配置
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_config(self, config):
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)
        self.config = config
        self.api_key = config.get("ark_api_key")

    def initialize(self):
        """初始化配置：输入 ARK API Key"""
        print("Initializing Volcengine Vision...")
        api_key = input("Enter your Volcengine ARK API Key: ").strip()
        
        if not api_key:
            print("API Key cannot be empty.")
            return False

        config = {
            "ark_api_key": api_key
        }
        self._save_config(config)
        print("Initialization successful!")
        return True

    def analyze_image(self, image_url, prompt="图片主要讲了什么?", model=DEFAULT_MODEL):
        """
        调用火山引擎视觉模型分析图片
        :param image_url: 图片 URL
        :param prompt: 提示词 (默认: "图片主要讲了什么?")
        :param model: 模型版本 (默认: doubao-seed-1-6-vision-250815)
        :return: 模型返回的文本描述
        """
        if not self.api_key:
            print("API Key is missing. Please run initialize() first.")
            # 尝试自动初始化
            if not self.initialize():
                return None

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
        }
        
        try:
            response = requests.post(API_ENDPOINT, headers=headers, json=payload)
            response.raise_for_status() # 检查 HTTP 错误
            
            resp_json = response.json()
            
            # 解析返回结果
            if "choices" in resp_json and len(resp_json["choices"]) > 0:
                content = resp_json["choices"][0]["message"]["content"]
                return content
            else:
                return f"Error: Unexpected response format: {resp_json}"
                
        except requests.exceptions.RequestException as e:
            return f"API Request Failed: {e}"
        except Exception as e:
            return f"An error occurred: {e}"

if __name__ == "__main__":
    client = VolcengineVision()
    if not client.api_key:
        client.initialize()
    else:
        print("Volcengine Vision is configured.")
