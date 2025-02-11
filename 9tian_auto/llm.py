# import openai
import os
# import random
import requests
import warnings
desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
#os.path.expanduser('~') 获取当前用户的主目录路径。os.path.join() 将主目录路径与 'Desktop' 拼接，得到桌面路径。
setup_file_name = 'MY-AI.txt'# 指定文件名
setup_file_path = os.path.join(desktop_path, setup_file_name)# 拼接文件的完整路径

def read_txtfile(path):
    """
    格式:XXX:123 #内容注释 --> 'XXX':'123'
        XXX_dict:A=1;2||B=3 -->'XXX':{A:(1,2),B:3}
    :return:返回指定文件中的内容为字典
    """
    # 以_list:结尾的为列表
    # 以_dict:结尾的为列表
    #最后都装到一个字典中,前缀是名字

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
            if '_list:' in line:
                back_list=[]
                tittle,infor=line.split('_list:',1)
                each=infor.split('||')
                for i in each:
                    back_list.append(i)
                data_dict[tittle]=back_list
            elif '_dict:' in line:
                back_dict={}
                tittle,infor=line.split('_dict:',1)
                each_dict_infor=infor.split('||')
                for i in each_dict_infor:
                    key,value_text=i.split('=')
                    try:
                        value_list=value_text.split(';')
                    except Exception as e:
                        value_list=[value_text]
                    back_dict[key] = value_list
                data_dict[tittle] = back_dict
            else:
                the_key, value = line.split(':', 1)  # 按冒号分割键和值
                data_dict[the_key.strip()] = value.strip()  # 去除键和值的前后空格，并添加到字典中
        except Exception as e:
            print(f'"{line}"转换发生错误,已经跳过')

    return data_dict

try:
    setup_info = read_txtfile(setup_file_path)
    KEY, URL, MODEL = setup_info['KEY'], setup_info['URL'], setup_info['MODEL']
    REPLACE = setup_info['REPLACE']
    print(f'key:{KEY}\nurl:{URL}\nmodel:{MODEL}')
except Exception as e:
    warnings.warn(f"加载配置文件失败{e}")
    REPLACE = {}


class CHAT:
    def __init__(self):
        self.post_json = []
        self.api_key = KEY if 'KEY' in globals() else ''
        self.api_url = URL if 'URL' in globals() else ''
        self.api_model = MODEL if 'MODEL' in globals() else ''

    def url(self,the_url):
        self.api_url = the_url

    def key(self,the_key):
        self.api_key = the_key

    def model(self,the_model):
        self.api_model = the_model

    def user(self,content):
        """
        增加一个user角色的JSON块(字典块)
        """
        message = {'role': "user",
                   'content': content}
        self.post_json=self.post_json+[message]

    def assistant(self,content):
        """
        增加一个assistant角色的JSON块(字典块)
        """
        message = {'role': "assistant",
                   'content': content}
        self.post_json=self.post_json+[message]

    def system(self,content):
        """
        增加一个system角色的JSON块(字典块)
        """
        message = {'role': "system",
                   'content': content}
        self.post_json=self.post_json+[message]

    def post(self, temperature=0.2, timeout=60,test_text=True):
        post_list = self.post_json
        the_key = self.api_key
        the_url = self.api_url
        the_model = self.api_model

        # 定义需要检查的字段
        missing_fields = {"api_key": the_key,"api_url": the_url,"api_model": the_model,"post_json": post_list}
        # 找出为空的字段
        missing = [key for key, value in missing_fields.items() if not value]
        # 如果有缺失的字段，抛出异常并返回具体信息
        #if not value 这样会捕获所有 "假" 值（如 None、''、[]、0、False 等）。
        if missing:
            raise ValueError(f"缺少参数: {', '.join(missing)}")


        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {the_key}"  # API 密钥
        }

        data = {
            "model": the_model,
            "messages": post_list,
            "temperature": temperature
        }

        if test_text:
            print(f"开始投递:\n"
                  f"model:{the_model}\n"
                  f"messages:\n{post_list}")
        try:
            response = requests.post(the_url, json=data, headers=headers, timeout=timeout)
            if response.status_code == 200:
                # return response.json()  # 返回 JSON 数据
                back = response.json()
                return back['choices'][0]['message']['content']
            else:
                return f"gotostop-->API调用失败 状态码: {response.status_code} 响应内容: {response.text}"
        except requests.exceptions.Timeout:
            return f"gotostop-->请求超时"
        except Exception as e:
            return f"gotostop-->API调用异常: {str(e)}"

def reduce_error(text, del_words_list=(),replace_dict=REPLACE):
    """
    text:输入的文本
    del_word_list:可以手动添加需要删除的字符列表
    replace_dict:可以手动添加需要替换的字符字典,字典的key是[替换结果],字典的value是[查找的目标]
    """
    if not isinstance(del_words_list,(list,tuple)):
        del_words_list = [del_words_list]
    no_words = ['查看更多消息','以下为新消息'] #无意义字符
    no_words.extend(del_words_list)
    for word in no_words:
        if word in text:
            text = text.replace(word, '')
    for key,val in replace_dict.items():
        for the_word in val:
            text = text.replace(the_word,key)
    return text

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


# system_front = setup_info['SYS_F']
# system_down = setup_info['SYS_D']
# #model='gpt-4o'|'gpt-3.5-turbo'|'o1-mini'
# replace_word_list= setup_info['REPLACE']

# def text_2_message_list(text,user):
#     back_list = []
#     text = reduce_error(text,'message_text')
#     lines = text.strip().split('\n')
#     for i in lines:
#         message_dict={}
#         if '<--[我说]' in i:
#             message_dict['role']='assistant'
#         elif f'<--[{user}]' in i:
#             message_dict['role']='user'
#         else:
#             print(f'没有查找到role对象,{i}')
#             continue
#         content = reduce_error(i,'output',[f'[{user}]']).strip()
#         if content == '':
#             continue
#         if '||' in content:
#             content=content.replace('||','\n')
#         message_dict['content'] = content
#         back_list.append(message_dict)
#     return back_list

# def chat_post(post_list,temperature=0.2,timeout_seconds=60,base_url=url,key=key,model=model):
#     """
#     post_list 一组字典列表
#     """
#     print(post_list)
#     url = base_url  # API 地址
#     headers = {
#         "Content-Type": "application/json",
#         "Authorization": f"Bearer {key}"  # API 密钥
#     }
#
#     data = {
#         "model": model,
#         "messages": post_list,
#         "temperature": temperature
#     }
#
#     try:
#         response = requests.post(url, json=data, headers=headers , timeout=timeout_seconds)
#         if response.status_code == 200:
#             # return response.json()  # 返回 JSON 数据
#             back = response.json()
#             return back['choices'][0]['message']['content']
#         else:
#             return f"gotostop---API 调用失败，状态码: {response.status_code}, 响应内容: {response.text}"
#     except requests.exceptions.Timeout:
#         return f"gotostop---请求超时"
#     except Exception as e:
#         return f"gotostop---API 调用异常: {str(e)}"
#
#
# def chat(message_list,question,system_front=system_front,system_down=system_down,base_url=url,key=key,model=model):
#     """
#     message是一个列表,其中每个项为dict
#     question 是最终问题,是一个 text
#     dict需要提供:role:(system|assistant|user),content:message
#     """
#     url = base_url  # API 地址
#     headers = {
#         "Content-Type": "application/json",
#         "Authorization": f"Bearer {key}"  # API 密钥
#     }
#     first_message={'role':'system','content':system_front}
#     down_message={'role':'system','content':system_down}
#     question_message=[{'role':'user','content':question}]
#     last_message=message_list
#     input_message=[first_message]+last_message+[down_message]+question_message
#     print(f'开始投递消息:\n{input_message}')
#     data = {
#         "model": model,
#         "messages": input_message,
#         "temperature": 0.2
#     }
#
#     try:
#         response = requests.post(url, json=data, headers=headers)
#         if response.status_code == 200:
#             # return response.json()  # 返回 JSON 数据
#             back = response.json()
#             return back['choices'][0]['message']['content']
#         else:
#             return f"gotostop---API 调用失败，状态码: {response.status_code}, 响应内容: {response.text}"
#     except Exception as e:
#         return f"gotostop---API 调用异常: {str(e)}"
#


#model:ERNIE-3.5-8K 上下文功能优异
#gemini-2.0-flash 速度比较快,推理能力不行
#ideogram_describe 图像转文本