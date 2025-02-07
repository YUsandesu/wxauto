# import openai
import os
# import random
import requests

desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')#os.path.expanduser('~') 获取当前用户的主目录路径。os.path.join() 将主目录路径与 'Desktop' 拼接，得到桌面路径。
setup_file_name = 'MY-AI.txt'# 指定文件名
setup_file_path = os.path.join(desktop_path, setup_file_name)# 拼接文件的完整路径

def read_txtfile(path):
    """
    格式:XXX:123 #内容注释 --> {'XXX':'123'}
    REPLACE:A=1;2||B=3 -->D{A:(1,2),B:3}
    :return:返回指定文件中的内容为字典
    """
    data_dict = {}
    with open(path, 'r', encoding='utf-8') as file:
        text = file.read()# 读取文件内容
        # print(text)
    lines = text.strip().split('\n')# 按行分割文本,返回一个列表型
    # 遍历每一行
    for line in lines:
        if '#' in line: # 去掉'#'后面的内容
            line, _ = line.split('#', 1)
        if line.strip()=='':
            continue
        try:
            if 'REPLACE:' in line:
                rp={}
                line=line.replace('REPLACE:','')
                each_replace=line.split('||')
                for i in each_replace:
                    key,value_text=i.split('=')
                    try:
                        value_list=value_text.split(';')
                    except Exception as e:
                        value_list=[value_text]
                    rp[key] = value_list
                data_dict['REPLACE'] = rp


            else:
                the_key, value = line.split(':', 1)  # 按冒号分割键和值
                data_dict[the_key.strip()] = value.strip()  # 去除键和值的前后空格，并添加到字典中
        except Exception as e:
            print(f'"{line}"转换发生错误,已经跳过')

    return data_dict

setup_info = read_txtfile(setup_file_path)
print(setup_info)
key, url, model = setup_info['KEY'], setup_info['URL'], setup_info['model']
system_front = setup_info['SYS_F']
system_down = setup_info['SYS_D']
#model='gpt-4o'|'gpt-3.5-turbo'|'o1-mini'
replace_word_list= setup_info['REPLACE']
def element_2_text(controls,my_name):
    """
    :param controls: >一组control对象
    :return: 一组纯文本的消息记录,聊天对象名
    """
    def is_int(num):#判断是否为整数
        try:
            int(num)
            return True
        except ValueError:
            return False
    user=''
    back=''
    for i in controls:
        if ':' in i.Name:
            sp=str(i.Name).split(':')
            if all(is_int(num) for num in sp):
                continue
        if i.LocalizedControlType == '列表项目':
            text=i.Name
            text=text.replace("\n", "||")
            back += f'"{text}"'
        if i.LocalizedControlType == '按钮':
            if i.Name == my_name:
                back += f'<--[我说]\n'
            else:
                back +=f'<--[{i.Name}]\n'
                user=i.Name
    return back,user

def text_2_message_list(text,user):
    back_list = []
    text = reduce_error(text,'message_text')
    lines = text.strip().split('\n')
    for i in lines:
        message_dict={}
        if '<--[我说]' in i:
            message_dict['role']='assistant'
        elif f'<--[{user}]' in i:
            message_dict['role']='user'
        else:
            print(f'没有查找到role对象,{i}')
            continue
        content = reduce_error(i,'output',[f'[{user}]']).strip()
        if content == '':
            continue
        if '||' in content:
            content=content.replace('||','\n')
        message_dict['content'] = content
        back_list.append(message_dict)
    return back_list


def chat(message_list,question,system_front=system_front,system_down=system_down,base_url=url,key=key,model=model):
    """
    message是一个列表,其中每个项为dict
    question 是最终问题,是一个 text
    dict需要提供:role:(system|assistant|user),content:message
    """
    url = base_url  # API 地址
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {key}"  # API 密钥
    }
    first_message={'role':'system','content':system_front}
    down_message={'role':'system','content':system_down}
    question_message=[{'role':'user','content':question}]
    last_message=message_list
    input_message=[first_message]+last_message+[down_message]+question_message
    print(f'开始投递消息:\n{input_message}')
    data = {
        "model": model,
        "messages": input_message,
        "temperature": 1
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            # return response.json()  # 返回 JSON 数据
            back = response.json()
            return back['choices'][0]['message']['content']
        else:
            return f"gotostop---API 调用失败，状态码: {response.status_code}, 响应内容: {response.text}"
    except Exception as e:
        return f"gotostop---API 调用异常: {str(e)}"

def reduce_error(text, type, del_words_list=[],replace=replace_word_list):
    if type== 'message_text':
        no_words = ['<--[查看更多消息]\n','收到红包，请在手机上查看']
    elif type== 'output':
        no_words = ['[我说]', '<--', '-->', '"', '\n','以下为新消息','收到红包，请在手机上查看']
    else: raise ValueError("不符合规范")
    no_words.extend(del_words_list)
    for word in no_words:
        if word in text:
            text = text.replace(word, '')
    for key,val in replace_word_list.items():
        for the_word in val:
            text = text.replace(the_word,key)
    return text
# 测试
def quick_chat(question):
    chat([{'role': 'assistant', 'content': "初次见面,很高兴认识你."}], question)
print( quick_chat('你好,我是MCyj,你在哪边?') )
