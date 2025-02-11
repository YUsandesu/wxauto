import math
import random
import time
import warnings
from time import sleep
import traceback
from Database import *
from get_wechat_handle import *
from llm import *
import autoit
import sys
from user_hash import *
import keyboard
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
run=True
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
        while not refresh_wechat_window(Main=True, Notify=False):
            time.sleep(1)
            b_inf=refresh_wechat_window(Main=True, Notify=False)
            print(b_inf)
        x, y = get_search_control_location()
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
    random_seed=random.randint(-5,12)
    message_json = message_chain_to_json(get_message_chain())
    newest_reply = message_json[-1]['content']  # 最新的一条消息
    if random_seed>=0:
        emoj=False
    else:emoj=True
    text_len = math.sqrt(random.randint(1,5))
    text_len = round(text_len)+10
    if text_len >25:
        text_len=round(text_len+(text_len-25)/3)
    print(f'会话长度:{text_len},{emoj}')
    # FIXME 这里乱的要死 很多重复获取了控件
    controls = get_chat_element()
    myname=get_my_name()
    text,user = element_2_text(controls,myname)
    if user == ADMIN_USER:
        con=get_chat_element(Chatbox=False,Msg=True)
        admin_code(con[-1].Name)

    if '[我说]' in text[-10:]:
        print("由于对方还未回复,跳过")
        return None

    if any(i in user for i in USER_DONT_REPLY):#如果昵称在不回复的列表中
        print(f"{user}在不回复的列表中")
        user_hash=save_name_hash(user)
        send_message_to_user(ADMIN_USER, f"Hash: [{user_hash}]-->用户:[{user}] 发送了消息: {newest_reply}")
        return None

    if '[图片]' in newest_reply:
        print(f'{newest_reply},暂时还没有照片功能')
        user_hash = save_name_hash(user)
        send_message_to_user(ADMIN_USER, f"Hash: [{user_hash}]-->用户: {user} 发送了一张照片")
        return None
    back_word= chat_base_on_memory(reason=False)
    print(f'OPENAI返回值:{back_word}')
    if 'gotostop' in back_word:
        user_hash = save_name_hash(user)
        send_message_to_user(ADMIN_USER, f"Hash:[{user_hash}]-->用户:[{user}] 发送了消息: {newest_reply} \n-->系统拒绝回答,OPENAI: {back_word} ")
        return None
    return back_word

def toggle_pause():
    global run
    run = not run
    print(f"收到按键,当前状态run:{run}")
keyboard.add_hotkey("ctrl+space", toggle_pause) # 监听键按下
print("开始监听按键,按下ctrl+space键暂停运行")
def start():
    # send_message_to_user(ADMIN_USER, f'启动成功') #TODO正式加载应该开启
    print("start循环")
    while True:
        if not run:
            time.sleep(1)
            continue
        close_window(Main=True, Notify=False, close=True)
        time.sleep(1.1)
        autoit.mouse_move(0, 0, 2)
        if is_new_information():
            print('**识别到新消息**,进入等待时间')
            close_window(Main=True, Notify=False, close=True)
            time.sleep(2)  # 给2秒时间由本人回复
            autoit.mouse_move(0, 0, 2)
            if not is_new_information():
                print("已经人工回复,重新监听")
                time.sleep(3)
                continue
            move_to_wechat_sys() #移动到托盘图标
            autoit.mouse_click() #点击托盘
            while refresh_wechat_window(Main=True, Notify=False) is False:#刷新wechat直到成功显示
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
start()
# while True:
#     try:
#         start()  # 尝试启动程序
#     except Exception as e:
#         print(f"发生严重错误，错误信息：{e}")
#         print("尝试重新启动...")
#         time.sleep(1)  # 等待 1 秒后再次尝试
#         try:
#             # send_message_to_user(ADMIN_USER, f'程序运行发生错误, 错误代码: {e}')
#             tb = traceback.extract_tb(sys.exc_info()[2])  # 提取调用过程
#             call_stack = []
#             for frame in tb:
#                 call_stack.append({
#                     "function": frame.name,  # 只保留函数名
#                     "line_number": frame.lineno,  # 出错的行号
#                     "code": frame.line  # 代码内容
#                 })
#
#             error_info = {
#                 "error_message": str(e),
#                 "call_stack": call_stack  # 仅保留调用栈，不含文件路径
#             }
#             warnings.warn(f"保存错误内容:{error_info}")
#             data=load_json_file_dict('run_error.json')
#             data[get_now_time()]=error_info
#             save_json_file_dict('run_error.json',data)
#         except Exception as inner_error:
#             print(f"发送/保存 错误报告失败，错误信息: {inner_error}")
