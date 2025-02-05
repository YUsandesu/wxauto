# import openai
import os
# import random
import requests

default_prompt = '''you are a helpful assistant'''

def setup():
    # 获取桌面路径
    desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
    #os.path.expanduser('~') 获取当前用户的主目录路径。os.path.join() 将主目录路径与 'Desktop' 拼接，得到桌面路径。
    # 指定文件名
    file_name = 'MY-AI.txt'
    # 拼接文件的完整路径
    file_path = os.path.join(desktop_path, file_name)
    # 读取文件内容
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
            print(text)
    except FileNotFoundError:
        print(f"文件 {file_name} 未找到")
    except Exception as e:
        print(f"读取文件时发生错误: {e}")

    data_dict = {}
    # 按行分割文本
    lines = text.strip().split('\n')

    # 遍历每一行
    for line in lines:
        # 按冒号分割键和值
        key, value = line.split(':', 1)
        # 去除键和值的前后空格，并添加到字典中
        data_dict[key.strip()] = value.strip()

    # 输出字典
    print(data_dict)
    return data_dict


info = setup()
key, url, model = info['KEY'], info['URL'], info['model']
model='gpt-4o'
# model='gpt-3.5-turbo'
#TODO 应该包含Prompt上下文信息，帮助模型更好地理解任务。
def chat(prompt,base_url=url, key=key, model=model):
    url = base_url  # API 地址
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {key}"  # API 密钥
    }
    data = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}  #TODO 关于ROLE是什么作用?
        ],
        "temperature": 0.5
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            # return response.json()  # 返回 JSON 数据
            back = response.json()
            return back['choices'][0]['message']['content']
        else:
            return f"API 调用失败，状态码: {response.status_code}, 响应内容: {response.text}"
    except Exception as e:
        return f"API 调用异常: {str(e)}"

# 测试
# print(chat("你好，我是喵喵，请和我打个招呼"))
