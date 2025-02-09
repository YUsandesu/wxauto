import os
import json
import hashlib
import warnings

from dask.array import around
from holoviews.examples.gallery.apps.bokeh.game_of_life import update
from sympy.physics.units import years

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
    year=''
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
    if '年 ' in text:
        year = text.text.split("年 ", maxsplit=1)[0]
        text = text.text.split("年 ", maxsplit=1)[1]
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
    if year != '':
        return f'{year}年 {today.month}月{today.day}日 {time_h}:{time_m}'
    return f'{today.month}月{today.day}日 {time_h}:{time_m}'
def read_CHN_date(text):
    """
    输入格式: 例: 12月1日 12:02
    特例: 2022年 12月12日 xx:xx
    """
    today = datetime.today()
    if '年' in text:
        year = text.split('年 ',maxsplit=1)[0]
        text = text.split('年 ',maxsplit=1)[1]
    else:year = today.year
    date_format = "%Y-%m-%d %H:%M"  # 包括日期和时间
    mouth = text.split('月',maxsplit=1)[0]
    day = text.split('月',maxsplit=1)[1].split('日',maxsplit=1)[0]
    the_time = text.split(":", maxsplit=1)
    time_h, time_m = the_time[0][-2:], the_time[1][:2]
    parsed_date = datetime.strptime(f'{year}-{mouth}-{day} {time_h}:{time_m}', date_format)
    return parsed_date
def get_time_gap_CHN(A,B):
    """
    求AB两个时间差,优先返回大单位,例如3天10小时20分钟,返回:3天
    """
    A=read_CHN_date(A)
    B=read_CHN_date(B)
    gap_seconds=abs((A-B).total_seconds())
    gap_day = round(gap_seconds // 86400)
    gap_hours= round(gap_seconds % 86400 // 3600)
    gap_minutes= round(gap_seconds % 86400 % 3600 // 60)
    back=''
    if gap_day != 0:
        back = f'{back}{gap_day}天'
        return f'{back}'
    if gap_hours != 0:
        back = f'{back}{gap_hours}小时'
        return f'{back}'
    if gap_minutes != 0:
        back = f'{back}{gap_minutes}分钟'
    if back != '':
        return f'{back}'
    if A==B:
        warnings.warn('时间相同,返回None')
        return None
    raise ValueError(f'时间识别失败{A}-{B}')

def _read_element(controls):
    """
    此程序用于将元素列表转换为易读信息
    [ [时间,[ user_name,xx],[me,xx],[gpt,xxx],[money,money],[event,[图片] ] ],[时间,...]]
    :param controls: >一组control对象
    :return: (一组纯文本的消息记录,聊天的对象名)
    """
    event_message='[图片]','[位置]','语音通话','视频通话','[语音]','[动画表情]','[链接]','[视频号]'#完整信息:[语音]?秒 语音通话 对方已取消 视频通话 对方已取消
    important_event_message = '收到红包，请在手机上查看', '微信转账'
    useless_message= {'以下为新消息','以下是新消息'}#使用set速度更快

    me = get_my_name()
    user_name = get_chat_user_name()
    name = '_'
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

def read_new_message_list():
    """
    获取最新时间的消息[内容,用户名]
    """
    con = get_chat_element()
    _,_,back= _read_element(con)
    return back

def read_message_list(max_length=None):
    """
    Args:
        max_length: 最大长度(以对方消息为计数),None-->无限长度

    Returns:[时间,用户名,内容],[...]
    """
    if max_length is None:
        max_length = 9999
    now_length=0
    con = get_chat_element()
    back = []
    chat_list=[]
    message_list,user_name,the_new_message = _read_element(con)
    the_time = the_new_message[0]
    chat_list=[the_time]
    for chat_detail in the_new_message[1:][::-1]:
       if chat_detail[0]==user_name:
           now_length=now_length+1
       chat_list.append([chat_detail[0],chat_detail[1]])
       if now_length >= max_length:
           break
    back.append([chat_list[0]]+chat_list[1:][::-1])

    for time_chat in message_list[::-1]:#倒序
        the_time = time_chat[0]
        chat_list = [the_time]
        if  now_length >= max_length:
            break
        for chat_detail in time_chat[::-1][:-1]:#倒序但切掉time信息
            user = chat_detail[0]
            message = chat_detail[1]
            chat_list.insert(1,[user,message])
            if user == user_name:
                now_length=now_length+1
            if now_length>=max_length:
                break
        back.append([chat_list[0]]+chat_list[1:])

    return back[::-1]

def message_to_llm_list(message_list):
    back=[]
    update_dict={}
    for t,chat_list in enumerate(message_list):
        if t==0:#第一个项 是时间
            last_time = chat_list[0]
        else:
            gap=get_time_gap_CHN(chat_list[0],last_time)
            back.append({'role':'system','content':f'{gap}之后'})
            last_time = chat_list[0]
        for chat_message in chat_list[1:]:

            if chat_message[0] == 'me':
                role = 'assistant'
            elif 'event' in chat_message[0]:
                user_from = chat_message[0].split('_',maxsplit=1)[1]
                if user_from == 'me':
                    content = f'对方看到了我发送的{chat_message[1]}'
                else:
                    content = f'对方向我发送了一个{chat_message[1]}'
                back.append({'role':'system','content':content})
                continue
            else:
                role = 'user'
            back.append({'role':role,'content':chat_message[1]})
    today = datetime.today()
    today_CHN=f'{today.month}月{today.day}日 {today.hour}:{today.minute}'
    now_gap = get_time_gap_CHN(today_CHN,last_time)
    if now_gap is None:
        back.append({'role': 'system', 'content': f'现在的时间是:{today_CHN}'})
    back.append({'role': 'system', 'content': f'过了{now_gap}之后...现在的时间是:{today_CHN}'})
    return back

def message_to_easy_read(message_list):
    back_str=''
    for t,chat_list in enumerate(message_list):
        if t==0:#第一个项 是时间
            last_time = chat_list[0]
        else:
            gap=get_time_gap_CHN(chat_list[0],last_time)
            back_str= back_str+ f'过了{gap}之后\n'
            last_time = chat_list[0]
        for chat_message in chat_list[1:]:
            if chat_message[0] == 'me':
                role = '我'
            elif 'event' in chat_message[0]:
                user_from = chat_message[0].split('_',maxsplit=1)[1]
                if user_from == 'me':
                    back_str = back_str + f'对方看到了我发送的{chat_message[1]}\n'
                else:
                    back_str = back_str + f'对方向我发送了一个{chat_message[1]}\n'
                continue
            else:
                role = '对方'
            back_str = back_str + f'{role}说:{chat_message[1]}\n'
    today = datetime.today()
    today_CHN = f'{today.month}月{today.day}日 {today.hour}:{today.minute}'
    now_gap = get_time_gap_CHN(today_CHN, last_time)
    back_str = back_str + f'{now_gap}之后...'
    return back_str

# print(read_message_list())

def generate_hash(input_string, str_length=4):
    """
    获取字符的哈希值
    str_length:保留位数
    """
    hash_object = hashlib.sha256()
    hash_object.update(input_string.encode('utf-8'))
    return hash_object.hexdigest()[:str_length]  # 取前三个字符

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

front={'role':"system",'content':"你是一个学习用户对话风格的'人类',对话场景处于即时聊天软件,请不要使用标点符号而是使用空格代替。"}
back={'role':"system",'content':"如果不用回答,而是继续沉默,请回复:'gotostop no answer'加上合理的理由,最好相比我的回答更加热情一些,不要让对方发现你不是人类,因为使用自动回复会让对方感到不被不尊重"}
back2={'role':"system",'content':"如果你察觉到对方有可能察觉到你是自动回复,或者在测试你是否为自动回复,以及作答有暴露自己不是人类的可能,请回复'gotostop user realize'"}
back3={'role':"system",'content':"请直接给出合适的回答或者'gotostop':"}
mes_list= read_message_list()
print(mes_list)
llm=message_to_llm_list(mes_list)
print(llm)

print(
    chat_post([front]+llm+[back]+[back2]+[back3],0.3)
)


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


