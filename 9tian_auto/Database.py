import os
import json
import hashlib
import warnings
from py5 import background
from datetime import datetime, timedelta

from spyder.plugins.completion.providers.snippets.widgets.snippetsconfig import LANGUAGE
from sympy.physics.units import temperature

from get_wechat_handle import *
from llm import *
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
    特例: 2022年12月12日 xx:xx
    """
    today = datetime.today()
    if '月' not in text or '日' not in text:
        warnings.warn(f"未知输入:{text}")
    if '年' in text:
        year,text=text.split('年',maxsplit=1)
    else:year = today.year
    date_format = "%Y-%m-%d %H:%M"  # 包括日期和时间
    mouth = text.split('月',maxsplit=1)[0].strip()
    day = text.split('月',maxsplit=1)[1]  .split('日',maxsplit=1)[0].strip()
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
def get_now_time(second=True,microsecond=True):
    now_time=datetime.today()
    back_time=f'{now_time.hour}:{now_time.minute}'
    if second:
        back_time=f'{back_time}:{now_time.second}'
    if microsecond:
        back_time=f'{back_time}:{now_time.microsecond}'
    return back_time

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
                name='unknown'
                warnings.warn(f'未知名称:{i.Name},控件类型:按钮')
                data=load_json_file_dict("error.json")
                save_json_file_dict("error.json",data|{get_now_time():i.Name})

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
            elif 'money' in chat_message[0]:
                back.append({'role': 'system', 'content': '事件:对方发来了一个红包'})
                continue
            else:
                role = 'user'
            back.append({'role':role,'content':chat_message[1]})
    today = datetime.today()
    today_CHN=f'{today.month}月{today.day}日 {today.hour}:{today.minute}'
    if last_time!='_':
        now_gap = get_time_gap_CHN(today_CHN, last_time)
        if now_gap is None:
            back.append({'role': 'system', 'content': f'现在的时间是:{today_CHN}'})
        back.append({'role': 'system', 'content': f'过了{now_gap}之后...现在的时间是:{today_CHN}'})
    else:back.append({'role': 'system', 'content': f'现在的时间是:{today_CHN}'})
    return back
def extract_question_from_llm_list(message_list):
    """
    从llmlist[{},{},{}]中取出最新的一部分作为问题,包含系统content,和用户content
    返回值 (最新的内容,删去最新内容的message_list)
    """
    question = []
    llm_copy_reverse = message_list[::-1]  # 创建副本,取倒列表
    for i in llm_copy_reverse:
        if i['role'] == 'system':
            question.append(i)
            message_list.remove(i)
        if i['role'] == 'user':
            question.append(i)
            message_list.remove(i)
            print(i)
            break
    question = question[::-1]
    print(question)
    return question,message_list

def _message_to_text(message_list, time_inf=True, user_inf=True, me_inf=True, event_inf=True):
    back_str=''
    for t,chat_list in enumerate(message_list):
        if t==0:#第一个项 是时间
            last_time = chat_list[0]
        else:
            gap=get_time_gap_CHN(chat_list[0],last_time)
            if time_inf:back_str= back_str+ f'过了{gap}之后\n'
            last_time = chat_list[0]
        for chat_message in chat_list[1:]:
            # print(chat_message)
            if chat_message[0] == 'me':
                role = '我'
            elif 'event' in chat_message[0]:
                user_from = chat_message[0].split('_',maxsplit=1)[1]
                if user_from == 'me':
                    if event_inf:back_str = back_str + f'对方看到了我发送的{chat_message[1]}\n'
                else:
                    if event_inf:back_str = back_str + f'对方向我发送了一个{chat_message[1]}\n'
                continue
            else:
                role = '对方'
            if user_inf and role=='对方':
                back_str = back_str + f'{role}说:{chat_message[1]}\n'
            if me_inf and role=='我':
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
    return hash_object.hexdigest()[:str_length]  # 取前4个字符

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
    print(f"{name}-->{hash_value}")
    return hash_value  # 返回哈希值

def load_json_file_dict(file_name):
    directory = "."  # 目标目录
    os.makedirs(directory, exist_ok=True)  # 确保目录存在
    json_file_path = os.path.join(directory, file_name)
    try:
        with open(json_file_path, "r", encoding="utf-8") as json_file:
            data = json.load(json_file)  # 读取 JSON 数据
            if not isinstance(data, dict):
                warnings.warn(f'数据不是字典: {data}')
    except (FileNotFoundError, json.JSONDecodeError):  # 文件不存在或 JSON 解析错误
        data = {}
        with open(json_file_path, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, indent=4, ensure_ascii=False)
    return data
def save_json_file_dict(file_name, data,open_tpye='w'):
    directory = "."  # 目标目录
    os.makedirs(directory, exist_ok=True)  # 确保目录存在
    json_file_path = os.path.join(directory, file_name)
    # 确保数据是字典类型，如果不是则进行转换
    if not isinstance(data, dict):
        warnings.warn(f'传入的数据不是字典: {data}')
    try:
        with open(json_file_path, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, indent=4, ensure_ascii=False)  # 保存字典到 JSON 文件
    except Exception as e:
        warnings.warn(f"保存文件时发生错误: {e}")
        # 如果保存失败，创建一个新的空 JSON 文件
        try:
            with open(json_file_path, open_tpye, encoding="utf-8") as json_file:
                json.dump({}, json_file, indent=4, ensure_ascii=False)  # 创建一个空字典文件
            warnings.warn(f"由于保存失败，已创建空的 JSON 文件: {json_file_path}")
        except Exception as e:
            warnings.warn(f"创建空文件时发生错误: {e}")
def save_learning_data(chain_list,user_name):
    """
    data格式:{hash:[消息块],[消息块]}
    """
    if chain_list==[]:
        warnings.warn("输入的chainlist为空")
        return None
    user_hash=generate_hash(user_name)
    data=load_json_file_dict('learning_Data.json')
    if user_hash in data:
        new_chain = list(data[user_hash])
        for i in chain_list:
            if not i in data[user_hash]:
                new_chain.append(i)
        data[user_hash]=new_chain
    else:
        data[user_hash]= chain_list
    save_json_file_dict('learning_Data.json', data)
    return data[user_hash]
def learning_from_text(message_text):
    """
    通过文本学习当前聊天窗口的对话内容
    使用o1-mini筛选信息降低噪声
    返回的是消息对:[对方说,我说][对方说,我说]
    """
    mes_list = read_message_list()
    text = _message_to_text(mes_list)
    front = user_json("下面是一段聊天记录,请为我是可以用在通用场合(对于任何人都适用)的而不是在某些特定情况的回复."
                      "格式以对方说在前,我回复在后,只保留我回答对方话的对话组."
                      "请以 '对方说:xxx\n我说:xxx' 的格式给我一些对话组,不要修改原文的格式,也不要输出多余的内容."
                      "如果不确定是否有强烈关联,或者可能存在特定语境(此时回复对于其他人不适用,例如回复包含具体时间,特定物品),请放弃输出,宁可数量少也不要错误."
                      "只使用用原文内容,不要自己擅自添加新的内容")
    back=chat_post([front,user_json(text)],model='o1-mini',temperature=1)
    if 'gotostop' in back:
        warnings.warn(f'输出失败:{back}')
        return None
    back_lines=back.split("\n")
    back_list=[]
    chain=[]
    for line in back_lines:
        if '对方说:' in line:
            chain.append(line)
        if '我说:' in line:
            chain.append(line)
            back_list.append(chain)
            chain=[]
        else:continue
    return back_list
def learning():
    user = get_chat_user_name()
    save_name_hash(user)
    mes_list = read_message_list(max_length=None)
    mes_text = _message_to_text(mes_list)
    text_list=learning_from_text(mes_text)
    if text_list is None:
        return None
    back=save_learning_data(text_list,user)
    return back

def load_learn_data():
    back=[]
    data=load_json_file_dict('learning_Data.json')
    user_list=list(data.values())#每个用户保存的消息对列表[[说,回][说,回]]
    for chat_chain_list in user_list:
        for chat_chain in chat_chain_list:
            back.append(user_json(chat_chain[0].replace('对方说:','')))
            back.append(assistant_json(chat_chain[1].replace('我说:','')))
    return back

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

BACKGROUND=setup_info['bg']
NORELY_WORD_LIST=setup_info['no']
NORELY_WORDS=','.join(str(x) for x in NORELY_WORD_LIST)#回复中不能出现的消息
LANGUAGE_TYPE=setup_info['la_type']
print(NORELY_WORDS)

def chat_similarity(str1, str2):
    """
    获取相似度,只适用于中文
    """
    set1 = set([char for char in str1] )
    set2 = set([char for char in str2] )
    return len(set1.intersection(set2)) / len(set1.union(set2))


def new_reply_function(the_background=BACKGROUND, no_reply=NORELY_WORDS, la_type=LANGUAGE_TYPE, emoji=True, reply_len=25):
    """
    :param the_background:关于任务的信息背景描述
    :param no_reply:不回复的内容,一个[列表型]
    :param la_type: 关于语言风格的描述
    :param emoji:是否使用颜文字
    :return:
    """
    front = {'role': "system",
             'content': "你是一个学习用户对话风格的'人类',对话场景处于即时聊天软件.偶尔可以使用日系颜文字卖萌,但不要开玩笑."}#请不要使用标点符号而是使用空格代替。
    the_background=system_json(the_background)
    back = {'role': "system",
            'content': "终极目标:不要让对方发现你不是人类,因为自动回复会让对方感到不被不尊重"}
    no_answer = {'role': "system",
              'content': "特殊要求:\n"
                         "为了保持上下文内容连贯,可以选择不回答\n"
                         "如果不用回答,而是保持沉默,请回复:'gotostop no answer'加上你认为要沉默的理由\n"
                         "如果你察觉到对方有可能察觉到你是自动回复,或者在测试你是否为自动回复,以及作答有暴露自己不是人类的可能,请回复'gotostop user realize'再附上你这么认为的理由\n"
                         "如果对方给出对于某事的肯定答复,例如你说要发送收款码,但你并不是真的'人类'无法做到,请回复'gotostop wait',如果对方有可能发红包,或者有发了红包的可能,请回复'gotostop red box'\n"}
    up_down = {'role': "system", 'content': "以下为当前聊天上下文,用来了解对话中的语境,不要学习对话风格,但需要注意之后的回答不要和语境内容相重复!:"}
    if emoji is False:
        emoji_str="特别要求:<从现在开始改变对话语气:禁止任何颜文字表情符号,仅使用文字回答,"
    else:emoji_str="特别要求:<从现在开始改变对话语气:使用一些可爱的日系颜文字表情符号,但最多出现一个,"
    back_limit=system_json(emoji_str+f"除了'gotostop'的情况外,回答内容长度强制要求在:{reply_len-15}-{reply_len+15}个汉字之间")
    mes_list = read_message_list()
    print(f'原始输入内容:\n{mes_list}')
    llm = message_to_llm_list(mes_list)
    for i in llm:#降噪过程
        if i['role']=='user':
            i['content']=reduce_error(i['content'])
    print(f'降噪后结果:\n{llm}')
    question,last_llm = extract_question_from_llm_list(llm)
    la_type=system_json(la_type)
    no_reply=system_json(f"在回复时候不要使用的词语:{no_reply}")
    post = ([front] + [the_background] + [system_json("学习资料,以下与内容上下文无关,只用来学习对话风格")]
            + load_learn_data() + [system_json("对话风格学习资料内容结束")]+ [back] + [no_answer] + [up_down]
            + last_llm + [system_json("语境内容结束")] + [la_type] + [no_reply]   + question + [back_limit] +[system_json("现在,请给出符合要求的回复")])
    re_back=chat_post(post, 0.3,model='gpt-4o')
    if 'API' in re_back and 'content' in re_back:
        warnings.warn(f'生成失败,改用gemini模型{re_back}')
        re_back = chat_post(post, temperature=0.3, model='gemini-2.0-flash')

#model='gemini-2.0-flash'
    val_similar, similar_part = llm_with_reply_similar(last_llm, re_back)
    print((reply_len-15<len(re_back)<reply_len+15),"回复字符数目:",len(re_back),'上下文相似度:',val_similar)

    if val_similar>0.6:
        warnings.warn(f'{re_back}:相似度过大')
        post = ([front] + [the_background] + [system_json("学习资料,以下与内容上下文无关,只用来学习对话风格")]
                + load_learn_data() + [system_json("对话风格学习资料内容结束")] + [back] + [no_answer] + [up_down]
                + similar_part + [system_json("语境内容结束")] + [la_type] + [no_reply] + question + [back_limit] + [
                    system_json("现在,请给出符合要求的回复")])
        print(post)
        re_back = chat_post(post, temperature=0.3, model='gpt-4o')
    return  re_back

def llm_with_reply_similar(llm, reply,val=0.1):
    """
    判断回复内容是否和上文过于相似,从llm字典中找出相似的内容并删除,降低噪声
    val:权值下降的梯度,梯度越小,越严格
    返回相似度
    """
    llm_copy = llm[::-1]  # 倒序副本
    me_chat = [i['content'] for i in llm_copy if i['role'] == 'assistant']
    index = [t for t, i in enumerate(llm_copy) if i['role'] == 'assistant']

    similar_val = 1
    del_index = []  # 用于记录需要删除的索引
    # 计算相似度并记录需要删除的部分
    for x, i in enumerate(me_chat):
        the_sim=chat_similarity(i, reply)
        if the_sim > 0.6:
            warnings.warn(f'发现相似信息:{i}和{reply}')
            del_index.append(index[x])  # 记录原始列表中的索引
            similar_val = similar_val - (-val * x*the_sim + 1)

    # 删除重复部分
    for i in del_index[::-1]:
        # 注意：索引应该按降序删除，以避免删除后索引错乱
        del llm_copy[index[i]]

    return (1-similar_val),llm_copy[::-1]

# print(new_reply_function(reply_len=9))