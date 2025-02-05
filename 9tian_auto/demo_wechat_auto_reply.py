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
        print("由于对方还未回复,跳过")
        return None
    # input_pre = ((f"我创造你的目的是代替人工来回复信息:我是一个互联网主播,这是我的聊天记录,"
    #               f"我的发言写作:'[我说]',我在和对方在即时聊天软件中,对方的发言写作'[{input_user}]'\n"
    #               f"你的任务是根据聊天记录,为我选择(1)进行回复 (2)中断交流 (3)告诉我,让我本人来处理"
    #               f"以下是聊天记录,其中我的消息用'<--[我说]'已经标出 :\n") + input_word +
    #               f"(1)请直接给出发言,方便我复制到聊天框,要简短,不要使用标点符号,"
    #               f"但可以使用可爱的颜文字(聊天中出现频率低于15%),并体现出我们对聊天方的重视"
    #               f"(2)如果交流进行到必须要结束才可以体现出礼貌的程度:请直接回复'gotostop'来让我明白"
    #               f"(3)如果出现问我有没有时间 或者向我预约一些事项,请返回'!!gotostop!!'来提醒我")
    input_pre=(('我创造这个智能体的目的是：“代替喵喵（我）在微信回复别人”\n应用背景：用户是在及时聊天软件中通过文字和喵喵交流不是使用视频聊天回复时候不要包含表情动作信息\n'
               '人物背景：喵喵是一名互联网爱豆用户在及时聊天软件中与她对话,她不用喵喵自称因为感到害羞也不使用括号的方式增加信息内容'
               '有一点小名气但是实际上性格自卑平时不直播，现在抖音偶尔使用（频率比较低）\n'
               '喵喵经常为了一点小钱而为对方专门拍摄照片作为感谢但这不是免费的要打赏获得好感度才可以如果对方花188的话喵喵会很高兴的收下。\n'
               '喵喵平日住在北京的公寓，具体地址是北京市朝阳区/n接下来你要负责模仿喵喵的发言'
               '由我来作为用户与你对话你的回答要非常简单便于及时沟通不要使用标点符号但可以使用可爱的颜文字（只是偶尔使用，频率很低大约为10%）'
               '还可以使用波浪线“～”这个可以加在句尾或者类似撒娇的语气处（频率20%）要关注上下文 不要频繁的要求打赏（10%）'
               '以下是聊天记录 请你根据聊天记录来预测回复内容 之前聊天的内容,喵喵说的话已经用<--[我说]标记出来了:/n')
                +input_word
                +'/n 内容结束 请作答')

    print(f'==========================')
    print(f'向OPENAI输入内容:{input_pre}')
    print(f'==========================')
    back_word = chat(input_pre)
    print(f'OPENAI返回值:{back_word}')
    if 'gotostop' in back_word:
        return None
    no_word=['[我说]','<--','-->','[动画表情]','"','\n']
    for t in range(10):
        for i in no_word:
            back_word.replace(i, '')
    return back_word

wechat_shot_screen(True, False, False)

while True:
    time.sleep(5.2)
    autoit.mouse_move(0, 0, -1)
    if is_new_information():
        print('**识别到新消息**')
        move_to_wechat_sys()
        autoit.mouse_click()
        answer=get_rely(get_chat_message())
        if answer is not None:
            time.sleep(5)
            autoit.send(answer)
            time.sleep(2)
            autoit.send('{ENTER}')
            autoit.send('{ENTER}')
            autoit.send('{ENTER}')
            autoit.send('{ENTER}')
            autoit.send('{ENTER}')
            time.sleep(5)