import time
from get_wechat_handle import *
from llm import *
import autoit

import sys
import os
#+---+
#|流程|
#+---+

#监听 是否存在新消息 -->循环调用,is_new_information()
#      ||
#     \||/
#      \/     |-----(1)获取消息记录
#    获取消息---
#      ||     |-----(2)#TODO处理为可读格式,方便发送到OPENAI
#     \||/             #TODO只保留最近几条消息,节省TOKEN
#      \/              #TODO创建一个JSON文件来为用户对象增加特殊描述
#从GPT获取回复--->llm.py #TODO 将输入分为role:'user'用户提问|'system'背景信息|'assistant'智能体答复
#      ||              #system可以重复传入.
#      ||              #TODO 在桌面建立一个txt文件来保存项目设置方便修改
#     \||/
#      \/
#    发送消息 ctrl+v,点击'发送(S)' #TODO 发送之前检查用户是否又输入了新文本
user_dont_reply=['股','👌','A.','✈️','💓']
def get_rely():
    text,user = element_2_text(*get_chat_element())
    if any(i in user for i in user_dont_reply):#如果昵称在不回复的列表中
        return None
    if '[我说]' in text[-10:]:
        print("由于对方还未回复,跳过")
        return None
    message_list = text_2_message_list(text,user)
    if len(message_list)>=1:
        input_message_list = message_list[:-1]
        question = message_list[-1]['content']
        if '[图片]' in question:
            print(f'{question},暂时还没有照片功能,拒绝回复')
            return None
        back_word = chat(input_message_list, question)
    else:
        back_word = quick_chat('~ o(*￣▽￣*)ブ')
    print(f'OPENAI返回值:{back_word}')
    if 'gotostop' in back_word:
        return None
    return reduce_error(back_word,'output')

# wechat_shot_screen(True, False, False)

while True:
    close_window(Main=True, Notify=False, close=True)
    time.sleep(1.1)
    autoit.mouse_move(0, 0,2)
    if is_new_information():
        print('**识别到新消息**,进入等待时间')
        close_window(Main=True, Notify=False, close=True)
        time.sleep(2)  # 给120秒时间由本人回复
        autoit.mouse_move(0, 0, 2)
        if not is_new_information():
            print("已经人工回复,重新监听")
            time.sleep(3)
            continue
        move_to_wechat_sys()
        autoit.mouse_click()
        while refresh_wechat_window(Main=True,Notify=False) is False:
            move_to_wechat_sys()
            autoit.mouse_click()
            continue

        answer=get_rely()
        if answer is not None:
            autoit.send(answer)
            time.sleep(1)
            autoit.send('{ENTER}')
            autoit.send('{ENTER}')
            autoit.send('{ENTER}')
            time.sleep(1)
            autoit.send('{ENTER}')
            autoit.send('{ENTER}')
            close_window(Main=True, Notify=False, close=True)