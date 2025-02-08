import os
import json
import hashlib
import warnings

from demo_wechat_auto_reply import *
from datetime import datetime, timedelta



def is_int(num):  # 判断是否为整数
    try:
        int(num)
        return True
    except ValueError:
        return False


def read_datetime(text):
    """
    如果输入格式不正确，系统会打印错误并返回 None
    """
    days_mapping = {
        '星期一': 0,
        '星期二': 1,
        '星期三': 2,
        '星期四': 3,
        '星期五': 4,
        '星期六': 5,
        '星期日': 6
    }
    today = datetime.today()
    date = ""
    the_time = ""

    if ':' in text:
        the_time = text.split(":", maxsplit=1)
        try:
            time_h, time_m = the_time[0][-2:], the_time[1][:2]
            if not all([is_int(time_h), is_int(time_m)]):
                return None
        except Exception as e:
            print(f"错误: {e}")  # 打印错误信息
            return None
    else:
        return None

    if " " in text:
        text = text.split(" ", maxsplit=1)
        date, the_time = text[0], text[1]

        if '星期' in date:
            days = today.weekday() - days_mapping[date]
            if days == 0:
                days = 7
            the_day = today - timedelta(days=days)
            return f'{the_day.month}月{the_day.day}日 {time_h}:{time_m}'

        elif '月' in date and '日' in date:
            return date.strip() + ' ' + time_h + ':' + time_m

        elif '昨天' in date:
            # 获取昨天的日期
            yesterday = today - timedelta(days=1)
            return f'{yesterday.month}月{yesterday.day}日 {time_h}:{time_m}'

        else:
            print(f"{text}未知格式, 无法识别")
            return None  # 未知格式

    return f'{today.month}月{today.day}日 {time_h}:{time_m}'


def element_2_text(controls):
    """
    此程序用于将元素列表转换为易读信息
    [ [时间,[ user_name,xx],[me,xx],[gpt,xxx],[money,money],[event,[图片] ] ],[时间,...]]
    :param controls: >一组control对象
    :return: (一组纯文本的消息记录,聊天的对象名)
    """
    event_message='[图片]','[位置]','语音通话','视频通话','[语音]','[动画表情]','[链接]'#完整信息:[语音]?秒 语音通话 对方已取消 视频通话 对方已取消
    important_event_message = '收到红包，请在手机上查看', '微信转账'
    useless_message= {'以下为新消息','以下是新消息'}#使用set速度更快

    me = get_my_name()
    user_name = get_chat_user_name()
    name = '_'
    content= ''
    the_time = ''
    chat_list=['_'] #其中填写了占位符,占位日期 [日期,chat_detail,chat_detail]
    chat_detail=['_','_'] #其中填写了占位符,占位用户名 [对象,内容]
    back=[]
    for i in controls:
        if i.LocalizedControlType == '文本':
            continue
        if i.Name in useless_message:
            continue #无用信息跳过
        if i.Name in important_event_message:
            chat_list.append(["money","money"])
            continue
        if i.Name in event_message:
            chat_list.append(['event',i.Name])
            continue

        if read_datetime(i.Name) is not None:#接受到日期信息
            the_time=read_datetime(i.Name)
            if chat_list[0]=='_':#如果是占位符就填入日期
                chat_list[0]=the_time
                continue
            else:#如果不是,说明当前时间已经填入,这是一个新的时间
                if len(chat_list)>1:#确保chat_list里面有消息
                    back.append(chat_list)
                    chat_list=[the_time]#重新新建一个列表
                    continue
                else:
                    if chat_detail[0]!="_" and chat_detail[1]!="_":
                        #防止因为chat_detail因为没有上传导致空
                        warnings.warn("chat_detail还没有上传")
                        chat_list.append(chat_detail)
                        chat_detail=['_','_']
                        chat_list = [the_time]  # 重新新建一个列表
                    else:
                        warnings.warn("只有时间信息,chat_list却为空,可能是删除过消息")
                    print(chat_detail)
                    continue

        if i.LocalizedControlType == '列表项目':#wechat还有一种控件叫'文本'但是返回信息不如列表项目全
            if chat_detail[1]=='_':#如果内容部分是占位符
                chat_detail[1]=i.Name.strip()
            else:
                if chat_detail[0]=='_': #此时还没有识别到新的Name,但是有内容
                    warnings.warn(f"此时可能是有头像没有识别到,导致错误:chat_detail:{chat_detail}")
                    chat_detail[1] = chat_detail[1].strip() + "\n" + i.Name.strip()
                    continue
                else:
                    warnings.warn(f"此时已经有内容,而且有名字,不应该出现这种情况,因为出现新名字立刻就上传了:chat_detail:{chat_detail}")
        if i.LocalizedControlType == '按钮':#头像信息,可以取到名称
            if i.Name==me:
                name='me'
            elif i.Name==user_name:
                name=user_name
            else:
                warnings.warn(f'未知名称:{i.Name},控件类型:按钮')

            if chat_detail[0]=='_':#如果表头是占位符
                chat_detail[0]=name #填入用户名

                if chat_detail[1]!='_':
                    chat_list.append(chat_detail)
                    chat_detail = ["_", '_']  # 重新初始化列表,清空detail
                    continue

            if chat_detail[0]!='_' and chat_detail[1]=="_":
                if chat_list[-1][0]=='event':
                    chat_list[-1][0]='event_'+name
                else:
                    warnings.warn(f'已经发现出现新名字,但是聊天记录是空的-->'
                                  f'清空detail防止程序错误,但是丢失了信息{chat_detail}')
                chat_detail = ['_','_']#重新更新
                continue

    the_new_message=chat_list #此时因为没有新的时间出现,不会上传chat_list,所以这是最新的消息
    return back,user_name,the_new_message

con = get_chat_element()[0]
print(con)
for i in con:
    if i.LocalizedControlType == '文本':
        continue
    print(f'名称:{i.Name}||{i.LocalizedControlType}')
a,b,c=element_2_text(con)
print(a)
print(b)
print(c)
#TODO 重新修改demo_wechat 来符合新标准


# 生成 3 个字符的哈希值
def generate_hash(input_string):
    hash_object = hashlib.sha256()
    hash_object.update(input_string.encode('utf-8'))
    return hash_object.hexdigest()[:4]  # 取前三个字符

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

    # 检查是否已有相同哈希值的记录
    for entry in data:
        if entry["hash"] == hash_value:
            # 如果找到了相同哈希值的记录，则更新名字
            entry["name"] = name
            break
    else:
        # 如果没有找到，追加新数据
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

