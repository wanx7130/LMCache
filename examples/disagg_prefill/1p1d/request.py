#!/usr/bin/env python3
"""
stream_completion.py
向 vLLM 本地服务器发送流式 completions 请求并实时拼接结果。
"""

import json
import requests

# URL = "http://127.0.0.1:9000/v1/completions"
URL = "http://10.9.113.132:9000/v1/completions"
HEADERS = {"Content-Type": "application/json"}

PAYLOAD = {
    "model": "/home/yao.qiu/llama_1b/Llama-3.2-1B-Instruct",
    "prompt": "我有3000元钱，想去南京旅游，帮忙制定一份南京3日游的旅游计划。",
    "max_tokens": 1000,
    "temperature": 0.0,
    "stream": True,          # 关键：开启流式
}

def main():
    response = requests.post(
      URL,
      headers=HEADERS,
      json=PAYLOAD,
      stream=True,  # 关键：开启流式响应
    )
    response.raise_for_status()

    full_text = ""
    for raw in response.iter_lines(delimiter=b"\n\n"):
        if not raw:
            continue
        line = raw.decode("utf-8").strip()
        if line.startswith("data: "):
            chunk = line[len("data: "):]
            if chunk == "[DONE]":
                break
            try:
                data = json.loads(chunk)
                delta = data["choices"][0].get("text", "")
                finish_reason = data["choices"][0].get("finish_reason")
                full_text += delta
                # 实时打印
                print(delta, end="", flush=True)
                if finish_reason is not None:
                    print(f"\n[finish_reason: {finish_reason}]")
            except Exception as e:
                print("\n[parse error]", e, line)

    print("\n---- Full Answer ----")
    print(full_text)

if __name__ == "__main__":
    main()