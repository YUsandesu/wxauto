import time
from get_wechat_handle import *
from llm import *
import autoit

import sys
import os

if getattr(sys, 'frozen', False):
    # 代码在 PyInstaller 打包后的可执行文件中
    base_path = sys._MEIPASS
else:
    # 代码在开发环境中运行
    base_path = os.path.dirname(os.path.abspath(__file__))

dll_path = os.path.join(base_path, 'autoit', 'lib', 'AutoItX3_x64.dll')
# 确保加载 DLL 时使用正确的路径

#+---+
#|流程|
#+---+

#监听 是否存在新消息 -->循环调用,间隔(3s),is_new_information()
#      ||
#     \||/
#      \/     |-----(1)#TODO 颜色识别分辨哪些是用户发送的,哪些是自己发送的
#    获取消息---      (2)#TODO 自动化操作鼠标,通过Ctrl+C来获取消息记录
#      ||                                |--->#TODO找到聊天面板精确位置
#     \||/                                    #从聊天面板下方中点位置向上拖动
#      \/
#从GPT获取回复--->llm.py chat()
#      ||
#     \||/
#      \/
#    发送消息 ctrl+v,点击'发送(S)' #TODO 从ORG返回数据中找到发送按钮的位置
def get_rely(get_message):
    input_word, input_user = get_message
    if '[我说]' in input_word[-10:]:
        return None
    input_pre = ((f"请模仿我的口气回复消息:我叫做'宇箭',我是一个帅哥,文中写作:[我说],我在和对方聊天(对方是[{input_user}]),"
                 f"请帮我创造一个新回复,只需要告诉我回复的内容即可,简单的一句话"
                 f"以下是聊天记录,其中我的消息用<--[我说]已经标出,回复时候不需要带人称,不要使用标点符号,仅使用空格"
                 f":\n") + input_word +
                 "如果交流进行到应该结束的程度:请直接回复'gotostop'")

    print(f'==========================')
    print(f'向OPENAI输入内容:{input_pre}')
    print(f'==========================')
    back_word = chat(input_pre)
    if 'gotostop' in back_word:
        return None
    return back_word

wechat_shot_screen(True, False, False)

while True:
    time.sleep(3.2)
    autoit.mouse_move(0, 0, -1)
    if is_new_information():
        print('**识别到新消息**')
        move_to_wechat_sys()
        autoit.mouse_click()
        answer=get_rely(get_chat_message())
        print(f'OPENAI返回值:{answer}')
        if answer is not None:
            autoit.send(answer)
            autoit.send('{ENTER}')
            autoit.send('{ENTER}')
            autoit.send('{ENTER}')
            autoit.send('{ENTER}')
            autoit.send('{ENTER}')