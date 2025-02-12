import os
import json
import hashlib
import warnings

from datetime import datetime, timedelta

from PIL.ImImagePlugin import split

from get_wechat_handle import *
from llm import *
def is_int(num):  # 判断是否为整数
    try:
        int(num)
        return True
    except ValueError:
        return False
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
def _read_element(control_list):
    """
    <<这是一个内部函数,如果获取消息记录,建议使用get_message_chain>>
    将元素列表转换为可用信息
    [ [时间,[ user_name,xx],[me,xx],[gpt,xxx],[money,money],[event,[图片] ] ],[时间,...]]
    按照时间分出了一些列表,每个列表的第一项是时间,之后的项目是聊天记录
    :param control_list: >一组control对象
    :return: (一组纯文本的消息记录,聊天的对象名)
    """
    event_message='[图片]','[位置]','语音通话','视频通话','[语音]','[动画表情]','[链接]','[视频号]'#完整信息:[语音]?秒 语音通话 对方已取消 视频通话 对方已取消
    important_event_message = '收到红包，请在手机上查看', '微信转账'
    useless_message= {'以下为新消息','以下是新消息'}#使用set速度更快

    me = get_my_name()
    user_name = get_chat_user_name()
    print(user_name)
    name = '_'
    the_time = ''
    chat_list=['_'] #其中填写了占位符,占位日期 [日期,chat_detail,chat_detail]
    chat_detail=['_','_'] #其中填写了占位符,占位用户名 [对象,内容]
    back=[]
    for i in control_list:
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
def get_message_chain(max_length=None):
    """
    程序流程:
    get_chat_element()获取控件列表-->_read_element()获取聊天内容列表-->处理列表信息为单个信息块
    max_length: 获取到的对话最大长度(以对方的消息为计数)
    None-->无限长度
    返回:[时间,用户名,内容],[时间,用户名,内容],...
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
def message_chain_to_text(message_list,my_reply='我说:',he_say='对方说:', time_inf=True, user_inf=True, me_inf=True, event_inf=True):
    back_str=''
    for t,chat_list in enumerate(message_list):
        if t==0:#第一个项 是时间
            last_time = chat_list[0]
            back_str = back_str + f'我们是从{last_time}开始聊天的\n'
        else:
            gap=get_time_gap_CHN(chat_list[0],last_time)
            if time_inf:
                back_str= back_str+ f'过了{gap}之后\n'
            last_time = chat_list[0]
        for chat_message in chat_list[1:]:
            if chat_message[0] == 'me':
                if me_inf:
                    back_str = back_str + f'{my_reply}{chat_message[1]}\n'
            elif 'event' in chat_message[0]:
                user_from = chat_message[0].split('_',maxsplit=1)[1]
                if user_from == 'me':
                    if event_inf:back_str = back_str + f'对方看到了我发送的{chat_message[1]}\n'
                else:
                    if event_inf:back_str = back_str + f'对方向我发送了一个{chat_message[1]}\n'
                continue
            else:
                if user_inf:
                    back_str = back_str + f'{he_say}{chat_message[1]}\n'
    today = datetime.today()
    today_CHN = f'{today.month}月{today.day}日 {today.hour}:{today.minute}'
    now_gap = get_time_gap_CHN(today_CHN, last_time)
    if now_gap is None:
        back_str = back_str + f'距离刚才的聊天已经过了{now_gap},现在是{today.hour}点{today.minute}分'
    else:
        back_str = back_str + f'现在是{today.hour}点{today.minute}分'
    return back_str
def message_chain_to_json(message_chain):
    """
    将[MessageChain]转化为OPENAI接受的json格式
    """
    back=[]
    update_dict={}
    for t,chat_list in enumerate(message_chain):
        if t==0:#第一个项 是时间
            last_time = chat_list[0]
        else:
            gap=get_time_gap_CHN(chat_list[0],last_time)
            back.append({'role':'system','content':f'{gap}之后'})
            last_time = chat_list[0]
        for chat_message in chat_list[1:]:

            if chat_message[0] == 'me':
                role = 'assistant'
                back.append({'role': role, 'content': chat_message[1]})
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
                back.append({'role': role, 'content': '对方发来了内容:'+chat_message[1]})

    today = datetime.today()
    today_CHN=f'{today.month}月{today.day}日 {today.hour}:{today.minute}'
    if last_time!='_':
        now_gap = get_time_gap_CHN(today_CHN, last_time)
        if now_gap is None:
            back.append({'role': 'system', 'content': f'现在的时间是:{today_CHN}'})
        back.append({'role': 'system', 'content': f'过了{now_gap}之后...现在的时间是:{today_CHN}'})
    else:back.append({'role': 'system', 'content': f'现在的时间是:{today_CHN}'})
    return back
def extract_question_from_json(openai_json, distance=1):
    """
    从OPENAI_JSON中取出最新的一部分作为问题,包含系统content,和用户content
    distance:一直截取到第几次用户提问
    返回值 (最新的内容,删去最新内容的message_list)
    """
    stop=False
    question = []
    llm_copy_reverse = openai_json[::-1]  # 创建副本,取倒列表
    for i in llm_copy_reverse:
        if i['role'] == 'system':
            question.append(i)
            openai_json.remove(i)
        if i['role'] == 'user':
            question.append(i)
            openai_json.remove(i)
            distance=distance-1
            if distance<=0:
                stop=True
        if i['role'] == 'assistant' and stop:
            break
    question = question[::-1]
    print(question)
    return question,openai_json
def load_learning_data_to_text(file='learning_Data.json'):
    learn_words = ''
    learn_data = list(load_json_file_dict(file).values())
    for i in learn_data:
        for e in i:
            learn_words = learn_words + e[0].strip() + "---" + e[1].strip() + '\n'
    return learn_words
bg=setup_info['bg']

def chat_base_on_memory(my_nick='我',user_nick='',back_ground=bg,len_limit=0,reason=True):
    """
    提示词过程:
    学习文本--->背景信息--->对话情景--->拒绝回答情况--->输出要求
    reason:是否给出这么回答的理由,用于调试,如果选择True,会返回:[回答,理由]的列表
    len_limit:回复的长度限制,0:自动选择
    不过高要求回复长度,过高限制会导致乱回
    """
    if not user_nick:
        user_nick=create_nick_name(test=False)
    mes_chain = get_message_chain()
    if len_limit==0:
        len_limit=get_reply_len_limit(mes_chain)
        print("字数限制:",len_limit)
        if len_limit<5:
            len_limit=5#防止过小
    chatmes = message_chain_to_text(mes_chain, he_say=f'{user_nick}对我说:', my_reply=f"{my_nick}对他说:")
    chat = CHAT()
    chat.model('claude-3-5-sonnet-20241022') #grok-beta #llama-3.2-90b-vision-instruct
    #claude-3-5-sonnet-20241022  8.5分
    # claude-3-5-sonnet-20240620 8分
    #deepseek-chat 7.5分
    #ERNIE-4.0-8K 7分--->速度比较慢,但准确率很高
    #deepseek-r1  7分--->非常准确 但是太慢了,思维链太长
    #qwen-72b             6.5分
    #qwen2.5-72b-instruct 6分 --->逻辑能力不足,搞不清前后时间关系
    # #gemini-2.0-flash  6分
    # #gpt-4o            5分-->上下文能力不足
    # ERNIE-Speed-128K 4分---> 逻辑较差,长文本时所问非所答
    #llama-3.1-405b  2.5 机械重复说过的话
    #glm-4-0520   2.5分(7.5分) --->输出内容非常好,但是不稳定,总是说一些无关的话.
    #glm-4-airx   2.5分
    # claude-3-haiku-20240307 2分 思维能力差,所问非所答
    #学习文本:
    chat.system("你要学习互联网即时聊天的语言模式,接下来用户会给你一些聊天实例,不用回答")
    chat.user(load_learning_data_to_text())  # 加载学习文本
    #人物背景信息
    chat.system("现在,你要学习一些关于'我'的基本信息,接下来用户会发出来,不用回答")
    chat.user(back_ground)
    #对话情景信息:
    chat.system("你的任务是模仿用户的语言模式去回复他人,接下来用户会给你一些对话情景,不用回答")
    chat.user(chatmes)
    chat.user(f'以上就是对话情景,把他当作是你的记忆,请注意内容中关于我的自称,还要注意你的回复是否与在时间上自洽') #可选:请注意我对于对方的程序,这是我通常对他的称呼
    #拒绝回答情况说明:
    chat.user  (  "特殊要求:\n"
                  "为了防止对话无限期进行下去,可以选择不回答,例如对方已经给出对于某事的肯定答复:'好的','嗯',此时应该并回复:'gotostop no answer' 加上沉默的理由\n"
                  "如果察觉到对方有可能察觉到你是自动回复,或者在测试你是否为自动回复,以及作答有暴露自己不是人类的可能,请回复'gotostop user realize' 加上怀疑的理由\n"
                  "如果有些事因为你并不是真的'人类'无法做到,例如对方索要收款码,或者询问我们一些事情,我们无法确认,请不要猜测,而是回复'gotostop wait'\n"
                  "如果对方有可能发了红包,或者根据上下文,有已经发过红包的可能,请回复'gotostop red box'\n")
    #输出要求:
    chat.user(f'现在,请给出应该给对方({user_nick})的回复,字数强制要求在{len_limit}个汉字左右:')
    chat.system(f"除了'gotostop'的情况外,给出最符合用户风格的回复,只输出回复的短信内容,不输出任何其他信息,如果选择回复,字数要在{len_limit}个汉字以下")
    back = chat.post(timeout=120)
    if reason:
        chat.assistant(back)
        chat.user('为什么要这么回答,请给出推理理由')
        chat.system('现在给出用户:对于上文回答的理由')
        the_reason=chat.post()
        back=[back,the_reason]
    return back
def create_nick_name(test=False,model='claude-3-5-sonnet-20241022'):#deepseek-r1
    user_name=get_chat_user_name()
    chat=CHAT()
    chat.model(model)
    mes_chain = get_message_chain()
    back_ground=message_chain_to_text(mes_chain)
    chat.system('帮助用户判断昵称或代称')
    chat.user(f'对方的微信昵称叫做{user_name},请根据下文的聊天情景推断应该如何称呼他的小名,要求必须是中文字符')
    chat.user(f'{back_ground}')
    chat.user(f"避免让对方感到意外,只有存在明确的证据时,才可以使用小名,否则选择使用代称."
              f"例如:'哥哥','姐姐','亲','宝贝','弟弟','客人'等.请自由发挥,不要局限于上述."
              f"\n请直接回答我那个名称,别说其他多余的.")
    chat.system('现在直接说出代称,不附带任何多余的文本')
    back=deep_seek_r1_text(chat.post())
    if 'gotostop' in back or len(back)>5:
        chat.model('claude-3-5-sonnet-20241022')
        back = chat.post()
    if test:
        chat.assistant(back)
        chat.user("请给出为什么这么起名的理由")
        chat.system("现在直接回答理由")
        back=[back,deep_seek_r1_text(chat.post())]

    return back
def get_reply_len_limit(message_chain):
    js = message_chain_to_json(message_chain)
    new_que,_ = extract_question_from_json(js)
    back=0
    weight=[1,0.5,0.2,0.2,0.1,0.05]
    t=0
    for i in new_que:
        if i['role']=='user':
            if '引用' in i['content']:
                i['content']=i['content'].split("引用")[0]
            back = back+(len(i['content'].replace(' ',''))-len("对方发来了内容:"))*weight[t]  #FIXME 这个减法很蠢
            t = t + 1 if t < len(weight) - 1 else t
            #len取出的是字符数,可以正确取出中文字符数
    return round(back)

def deep_seek_r1_text(text):
    if '</think>' in text:
        return text.split('</think>')[-1].strip()
    else:return text

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
    mes_list = get_message_chain()
    text = message_chain_to_text(mes_list)
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
    mes_list = get_message_chain(max_length=None)
    mes_text = message_chain_to_text(mes_list)
    text_list=learning_from_text(mes_text)
    if text_list is None:
        return None
    back=save_learning_data(text_list,user)
    return back

def load_learn_data_to_json():
    back=[]
    data=load_json_file_dict('learning_Data.json')
    user_list=list(data.values())#每个用户保存的消息对列表[[说,回][说,回]]
    for chat_chain_list in user_list:
        for chat_chain in chat_chain_list:
            back.append(CHAT.user(chat_chain[0].replace('对方说:','')))
            back.append(CHAT.assistant(chat_chain[1].replace('我说:','')))
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
    # front = {'role': "system",
    #          'content': "你是一个学习用户对话风格的'人类',对话场景处于即时聊天软件.偶尔可以使用日系颜文字卖萌,但不要开玩笑."}#请不要使用标点符号而是使用空格代替。
    # the_background=system_json(the_background)
    # back = {'role': "system",
    #         'content': "终极目标:不要让对方发现你不是人类,因为自动回复会让对方感到不被不尊重"}

    up_down = {'role': "system", 'content': "以下为当前聊天上下文,用来了解对话中的语境,不要学习对话风格,但需要注意之后的回答不要和语境内容相重复!:"}
    if emoji is False:
        emoji_str="特别要求:<从现在开始改变对话语气:禁止任何颜文字表情符号,仅使用文字回答,"
    else:emoji_str="特别要求:<从现在开始改变对话语气:使用一些可爱的日系颜文字表情符号,但最多出现一个,"
    back_limit=system_json(emoji_str+f"除了'gotostop'的情况外,回答内容长度强制要求在:{abs(reply_len-15)}-{abs(reply_len+15)}个汉字之间")
    mes_list = get_message_chain()
    print(f'原始输入内容:\n{mes_list}')
    llm = message_chain_to_json(mes_list)
    for i in llm:#降噪过程
        if i['role']=='user':
            i['content']=reduce_error(i['content'])
    print(f'降噪后结果:\n{llm}')
    question,last_llm = extract_question_from_json(llm)
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
                    system_json("现在,请给出符合要求的回复,要及时通过拒绝回答来终止聊天,防止聊天无限期进行下去")])
        print(post)
        re_back = chat_post(post, temperature=0.3, model='gpt-4o')
    return  re_back


def llm_with_reply_similar(llm, reply, val=0.3):
    """
    判断回复内容是否和上文过于相似,从llm字典中找出相似的内容并删除,降低噪声
    val: 权值下降的梯度,梯度越小,越严格
    返回相似度
    """
    llm_copy = llm[::-1]  # 倒序副本
    me_chat = [i['content'] for i in llm_copy if i['role'] == 'assistant']
    index = [t for t, i in enumerate(llm_copy) if i['role'] == 'assistant']

    similar_val = 1
    del_index = []  # 用于记录需要删除的索引
    # 计算相似度并记录需要删除的部分
    for x, i in enumerate(me_chat):
        the_sim = chat_similarity(i, reply)

        # 使用递增的权重，使得后面的内容相关性更大
        weight = (1 + val * x)  # 权重随着x值增大而增大
        weighted_sim = the_sim * weight

        if weighted_sim > 0.3:
            warnings.warn(f'发现相似信息:{i}和{reply}')
            del_index.append(index[x])  # 记录原始列表中的索引
            similar_val = similar_val - (-val * x * weighted_sim + 1)

    # 删除重复部分
    # 按照索引降序排序，确保删除时不会影响到后续的索引
    for i in sorted(del_index, reverse=True):
        if i < len(llm_copy):  # 在删除前检查索引是否合法
            del llm_copy[i]  # 删除元素
    if similar_val>1:
        similar_val=0
    return (1 - similar_val), llm_copy[::-1]


# print(llm_with_reply_similar(mes_list,"手机号码:18811120311"))
# # print(new_reply_function(reply_len=0))