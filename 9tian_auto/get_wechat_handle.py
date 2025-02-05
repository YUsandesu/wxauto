import time

from imageio.config.plugins import class_name
from pywinauto import Desktop,Application
import win32gui
from wechat_image_recognition import *
# import pyautogui
# import ctypes
import autoit


def sys_shot():
    taskbar_handle = win32gui.FindWindow("Shell_TrayWnd", None)  # 获取任务栏句柄
    systray_handle = win32gui.FindWindowEx(taskbar_handle, 0, "TrayNotifyWnd", None)  # 获取托盘句柄
    SYS = Desktop().windows(handle=systray_handle)  # 获取托盘对象
    for i in SYS:
        print('托盘句柄---开始快照')
        image = i.capture_as_image()  # 获取窗口截图作为PIL图像对象
        image.save(f'sys.png')  # 保存图像
        rect=i.rectangle()
        return rect.left,rect.top

def wechat_shot_screen(Main=True,Notify=True,close=True):
    back_dict={}
    wechat_windows = Desktop().windows(title='微信')  # 获取微信窗口列表
    # 微信登录窗口类名：WeChatLoginWndForPC
    # 微信浏览器类名：Chrome_WidgetWin_0
    for t, w in enumerate(wechat_windows):
        print(f"wechat_shot_screen当前正在查找：{w.get_properties()}")
        if w.class_name() == 'WeChatMainWndForPC' and Main:  # 微信主窗口的类名：WeChatMainWndForPC，可见时：'style': 370081792
            if w.is_visible is False:
                # 如果窗口当前不可见：
                w.restore()
            else:
                w.set_focus()  # 如果窗口可见
            print('Wechat聊天主界面---开始快照')
            image = w.capture_as_image()  # 获取窗口截图作为PIL图像对象
            image.save(f'Main_Window.png')  # 保存图像
            rect = w.rectangle()
            back_dict['Main']=rect.left, rect.top



        if w.class_name() == 'TrayNotifyWnd' and Notify:  # 微信消息提示窗口类名 TrayNotifyWnd
            if w.is_visible is False:
                w.restore()
            else:
                w.set_focus()  # 如果窗口可见
            print('Wechat未读消息---开始快照')
            image = w.capture_as_image()  # 获取窗口截图作为PIL图像对象
            image.save(f'Notify_window.png')  # 保存图像
            rect = w.rectangle()
            back_dict['Notify'] = rect.left, rect.top

        if close:
            if w.is_visible():
                w.close_alt_f4()  # 关闭窗口

    return back_dict

def move_to_wechat_sys():
    """
    循环调用自己，等待找到托盘图标，然后滑动指针过去，来激活微信的Notify_window
    """
    x, y = sys_shot()
    if recognition_color(blur=True) is not False:
        w_x, w_y = recognition_color()
        print(x, y)
        print(w_x, w_y)
        print(x + w_x, y + w_y)
        tray_x, tray_y = x + w_x, y + w_y
        autoit.mouse_move(tray_x, tray_y, speed=2)  # 速度 10 表示平滑移动
    else:
        move_to_wechat_sys()

def is_new_information():
    """
    通过颜色识别来判断是否存在新消息
    """
    move_to_wechat_sys()
    back = wechat_shot_screen(Main=False)
    print(back)
    back = recognition_color(find_image='Notify_window.png', color_smooth=0, color=wechat_red_BGR)
    if back is not False:
        return True
    else:
        return False

# #TODO 拆分Main_Window窗口
wechat_shot_screen(Main=True,Notify=False)
