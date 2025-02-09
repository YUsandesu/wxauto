import time
from time import sleep

from fontTools.misc.cython import returns
from twisted.words.protocols.irc import split

from get_wechat_handle import *
from llm import *
import autoit
import sys
from user_hash import *
#+---+
#|流程|
#+---+

#监听 是否存在新消息 -->循环调用,is_new_information()
#      ||
#     \||/
#      \/     |-----(1)获取消息记录
#    获取消息---
#      ||     |-----(2)#TODO 创建一个JSON文件来储存用户的聊天记录
#     \||/             #TODO创建一个JSON文件来为用户对象增加特殊描述
#      \/
#从GPT获取回复--->llm.py #TODO 将输入分为role:'user'用户提问|'system'背景信息|'assistant'智能体答复
#      ||              #system可以重复传入.
#      ||              #TODO 在桌面建立一个txt文件来保存项目设置方便修改
#     \||/
#      \/
#    发送消息 ctrl+v,点击'发送(S)' #TODO 发送之前检查用户是否又输入了新文本
                                #TODO 向指定人发送信息
USER_DONT_REPLY=setup_info['dontreply']
ADMIN_USER=setup_info['ADMIN']
def admin_code(input_val):
    """
    输入*UserID_send_XXXXX 可以向user发送XXXXX
    """
    if "_send_" in input_val:
        user_value_hash,message=input_val.split('_send_')
        found_user = hash_2_user(user_value_hash)
        if found_user is not None:
            send_message_to_user(hash_2_user(user_value_hash),message)
        else:
            send_message_to_user(ADMIN_USER,f"发送失败,HASH: [{user_value_hash}] 没有找到")

def send_message_to_user(user,message):
    def get_user_window():
        """
        调用搜索,找到聊天对象,如果错误返回False,成功返回True
        :return:
        """
        refresh_wechat_window(Main=True, Notify=False)
        x, y = get_search_element()
        autoit.mouse_move(x, y, 2)
        autoit.mouse_click()
        time.sleep(1)
        autoit.send(user)
        time.sleep(1)
        autoit.send('{ENTER}')
        autoit.send('{ENTER}')
        autoit.send('{ENTER}')
        time.sleep(1)
        return get_chat_user_name()==user
    wait_times=0
    while get_user_window() is False:
        autoit.send('{ESC}')
        autoit.send('{ESC}')
        autoit.send('{ESC}')
        close_window(Main=True,Notify=False,close=True)
        wait_times+=1
        print("查找失败,重新查找")
        if wait_times==10:
            raise TimeoutError(f"发送消息对象:{user}名称始终不匹配")
        time.sleep(1)
        continue
    time.sleep(1)
    autoit.send(message)
    time.sleep(1)
    autoit.send('{ENTER}')
    autoit.send('{ENTER}')
    autoit.send('{ENTER}')
    time.sleep(1)
    autoit.send('{ENTER}')
    autoit.send('{ENTER}')
    close_window(Main=True, Notify=False, close=True)

def get_rely():
    controls , myname = get_chat_element()
    text,user = element_2_text(controls,myname)
    if user == ADMIN_USER:
        con,_=get_chat_element(Chatbox=False,Msg=True)
        admin_code(con[-1].Name)
    if '[我说]' in text[-10:]:
        print("由于对方还未回复,跳过")
        return None
    message_list = text_2_message_list(text,user)#聊天消息列表
    if any(i in user for i in USER_DONT_REPLY):#如果昵称在不回复的列表中
        print(f"{user}在不回复的列表中")
        user_hash=save_name_hash(user)
        send_message_to_user(ADMIN_USER, f"Hash: [{user_hash}]-->用户:[{user}] 发送了消息: {message_list[-1]['content']}")
        return None
    if len(message_list)>=1:
        input_message_list = message_list[:-1]
        question = message_list[-1]['content']#最新的一条消息
        if '[图片]' in question:
            print(f'{question},暂时还没有照片功能')
            user_hash = save_name_hash(user)
            send_message_to_user(ADMIN_USER, f"Hash: [{user_hash}]-->用户: {user} 发送了一张照片")
            return None
        back_word = chat(input_message_list, question)
    elif len(message_list)==1:
        back_word = quick_chat(message_list[0])
    else:
        back_word = quick_chat('~ o(*￣▽￣*)ブ')
    print(f'OPENAI返回值:{back_word}')
    if 'gotostop' in back_word:
        user_hash = save_name_hash(user)
        send_message_to_user(ADMIN_USER, f"Hash:[{user_hash}]-->用户:[{user}] 发送了消息: {message_list[-1]['content']} \n但系统拒绝回答,OPENAI: {back_word} ")
        return None
    return back_word


def start():
    send_message_to_user(ADMIN_USER, f'启动成功 测试: {LLM_load_test} ')
    while True:
        close_window(Main=True, Notify=False, close=True)
        time.sleep(1.1)
        autoit.mouse_move(0, 0, 2)
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
            while refresh_wechat_window(Main=True, Notify=False) is False:
                move_to_wechat_sys()
                autoit.mouse_click()
                continue
            answer = get_rely()
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

# while True:
#     try:
#         start()  # 尝试启动程序
#     except Exception as e:
#         print(f"发生严重错误，错误信息：{e}")
#         print("尝试重新启动...")
#         time.sleep(2)  # 等待 2 秒后再次尝试
#         try:
#             send_message_to_user(ADMIN_USER, f'程序运行发生错误, 错误代码: {e}')
#         except Exception as inner_error:
#             print(f"发送错误报告失败，错误信息: {inner_error}")
