import os
import json
import hashlib

# 生成 3 个字符的哈希值
def generate_hash(input_string):
    hash_object = hashlib.sha256()
    hash_object.update(input_string.encode('utf-8'))
    return hash_object.hexdigest()[:4]  # 取前三个字符

# 保存哈希值到 JSON 文件（追加模式）
def save_name_hash(name):
    directory = "."  # 目标目录
    os.makedirs(directory, exist_ok=True)  # 确保目录存在

    json_file_path = os.path.join(directory, "user_data.json")

    hash_value = generate_hash(name)  # 生成哈希值
    new_entry = {"hash": hash_value, "name": name}  # 生成新数据

    # 读取旧数据（如果文件存在）
    try:
        with open(json_file_path, "r", encoding="utf-8") as json_file:
            data = json.load(json_file)  # 读取 JSON 数据
            if not isinstance(data, list):  # 确保数据是列表
                data = [data]
    except (FileNotFoundError, json.JSONDecodeError):  # 文件不存在或 JSON 解析错误
        data = []

    # 追加新数据
    data.append(new_entry)

    # 重新写入 JSON 文件（格式化，保持 UTF-8）
    with open(json_file_path, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)

    return hash_value  # 返回哈希值

def hash_2_user(value_hash):
    json_file_path = os.path.join(".", "user_data.json")

    if not os.path.exists(json_file_path):
        return None  # 文件不存在，返回 None

    with open(json_file_path, "r", encoding="utf-8") as json_file:
        try:
            data = json.load(json_file)
            if isinstance(data, list):  # 确保 JSON 结构是列表
                for entry in data:
                    if entry.get("hash") == value_hash:
                        return entry.get("name")  # 找到匹配的哈希值，返回名字
        except json.JSONDecodeError:
            return None  # 解析失败，返回 None

    return None  # 没找到匹配的哈希值

# # 测试
# hash_result = save_name_hash("Alice")
# print(f"生成的哈希值: {hash_result}")
# find = '3bc5'
# found_user = hash_2_user(find)
# if found_user:
#     print(f"哈希值 {find} 对应的用户名是: {found_user}")
# else:
#     print(f"未找到哈希值 {find} 的用户")