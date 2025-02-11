import random
import time
from pywinauto import Desktop,Application
import win32gui
from sqlalchemy.testing.plugin.plugin_base import warnings

from wechat_image_recognition import *
# import pyautogui
# import ctypes
import autoit
# import llm
import uiautomation as uia
import warnings
def sys_shot():
    taskbar_handle = win32gui.FindWindow("Shell_TrayWnd", None)  # 获取任务栏句柄
    systray_handle = win32gui.FindWindowEx(taskbar_handle, 0, "TrayNotifyWnd", None)  # 获取托盘句柄
    SYS = Desktop().windows(handle=systray_handle)  # 获取托盘对象
    for i in SYS:
        # print('托盘句柄---开始快照')
        image = i.capture_as_image()  # 获取窗口截图作为PIL图像对象
        image.save(f'sys.png')  # 保存图像
        rect=i.rectangle()
        return rect.left,rect.top

def close_wechat_Main_Window():
    wechat_windows = Desktop().windows(title='微信')  # 获取微信窗口列表
    for t, w in enumerate(wechat_windows):
        if w.class_name() == 'WeChatMainWndForPC':  # 微信主窗口的类名：WeChatMainWndForPC，可见时：'style': 370081792
            if w.is_visible is True:
                w.set_focus()
                w.close_alt_f4()
                if w.is_visible is True:
                    warnings.warm(f"窗口依然存在,关闭失败,进入强制循环调用,可能卡死:{w}")
                    close_wechat_Main_Window()#循环调用

def refresh_wechat_window(Main=False,Notify=True,):
    """
    刷新微信窗口到可见状态.
    刷新失败返回False
    """
    #FIXME 这样查找窗口句柄是不行的 因为后面多开需要分线程
    print("refresh_wechat_window")
    wechat_windows = Desktop().windows(title='微信')  # 获取微信窗口列表
    for t, w in enumerate(wechat_windows):
        if w.class_name() == 'WeChatMainWndForPC' and Main:  # 微信主窗口的类名：WeChatMainWndForPC，可见时：'style': 370081792
            if w.is_visible is False:
                w.restore()
            else:
                w.set_focus()  # 如果窗口可见
            if w.is_visible() is False:
                return False
        if w.class_name() == 'TrayNotifyWnd' and Notify:  # 微信消息提示窗口类名 TrayNotifyWnd
            move_to_wechat_sys()
            time.sleep(1)
            if w.is_visible is False:
                w.restore()
            else:
                w.set_focus()  # 如果窗口可见
            if w.is_visible() is False:
                return False
            # print('Wechat未读消息---开始快照')
    return True
#TODO refresh_wechat_window需要修改 将两种查找分离开

def wechat_shot_screen(Main=True,Notify=True,close=True):
    """
    返回[Main,Notify],失败是F,否则返回图片
    """
    back=[Main,Notify]
    wechat_windows = Desktop().windows(title='微信')  # 获取微信窗口列表
    #此处使用的实际是:findwindows.find_elements()
    #TODO 此处接受PROCESS参数,应该修改以适应将来的多进程

    # 微信登录窗口类名：WeChatLoginWndForPC
    # 微信浏览器类名：Chrome_WidgetWin_0
    for t, w in enumerate(wechat_windows):
        # print(f"wechat_shot_screen当前正在查找：{w.get_properties()}")
        if w.class_name() == 'WeChatMainWndForPC' and Main:  # 微信主窗口的类名：WeChatMainWndForPC，可见时：'style': 370081792
            if w.is_visible is False:
                # 如果窗口当前不可见：
                w.restore()
            else:
                w.set_focus()  # 如果窗口可见
            # print('Wechat聊天主界面---开始快照')
            if w.is_visible() is False:
                while refresh_wechat_window(Main=True,Notify=False) is False:
                    #循环刷新直到窗口显示
                    time.sleep(1)
                    continue
            image = w.capture_as_image()  # 获取窗口截图作为PIL图像对象
            image.save(f'Main_Window.png')  # 保存图像
            back[0] = image
            if close:
                if w.is_visible():
                    try:
                        w.close_alt_f4()  # 关闭窗口
                    except Exception as e:
                        warnings.warn(f"出现异常,跳过本次关闭{w}")

        if w.class_name() == 'TrayNotifyWnd' and Notify:  # 微信消息提示窗口类名 TrayNotifyWnd
            if w.is_visible is False:
                w.restore()
            else:
                w.set_focus()  # 如果窗口可见

            if w.is_visible() is False:
                # 如果找不到 就一直把鼠标移到托盘 尝试启动
                if refresh_wechat_window(Main=False,Notify=True) is False:
                    warnings.warn("没有找到Notify窗口,无法快照")
                    back[1]=False
                    continue
            else:
                image = w.capture_as_image()  # 获取窗口截图作为PIL图像对象
                image.save(f'Notify_window.png')  # 保存图像
                back[1]=image
            if close:
                if w.is_visible():
                    try:
                        w.close_alt_f4()  # 关闭窗口
                    except Exception as e:
                        warnings.warn(f"出现异常,跳过本次关闭{w}")

    print(back)
    return back


def close_window(Main=True,Notify=True,close=True):
    wechat_windows = Desktop().windows(title='微信')  # 获取微信窗口列表
    for t, w in enumerate(wechat_windows):
        if w.class_name() == 'WeChatMainWndForPC' and Main:  # 微信主窗口的类名：WeChatMainWndForPC，可见时：'style': 370081792
            if w.is_visible is False:
                # 如果窗口当前不可见：
                continue
            if close:
                if w.is_visible():
                    w.close_alt_f4()  # 关闭窗口

        if w.class_name() == 'TrayNotifyWnd' and Notify:  # 微信消息提示窗口类名 TrayNotifyWnd
            if w.is_visible is False:
               continue
            if close:
                if w.is_visible():
                    w.close_alt_f4()  # 关闭窗口

def move_to_wechat_sys():
    """
    循环调用自己，等待找到托盘图标，然后滑动指针过去，来激活微信的Notify_window
    """
    autoit.mouse_move(random.randint(0,100), random.randint(0,100), speed=2)
    x, y = sys_shot()
    location=recognition_color(blur=True)
    if location is not False:
        w_x, w_y = location
        # print(x, y)
        # print(w_x, w_y)
        # print(x + w_x, y + w_y)
        tray_x, tray_y = x + w_x, y + w_y
        autoit.mouse_move(tray_x, tray_y, speed=2)  # 速度 10 表示平滑移动
    else:
        move_to_wechat_sys()

def is_new_information():
    """
    通过颜色识别来判断是否存在新消息
    """
    print("进入is_new_information")
    move_to_wechat_sys()
    _,notify_shot=wechat_shot_screen(Main=False,Notify=True,close=True)
    if not notify_shot:
        return False
    shot=np.array(notify_shot)
    shot_bgr = cv2.cvtColor(shot, cv2.COLOR_RGB2BGR)
    back = recognition_color(find_image=shot_bgr, color_smooth=0, color=wechat_red_BGR)
    # back = recognition_color(find_image='Notify_window.png',color_smooth=0, color=wechat_red_BGR)
    print('查找是否含有红色点',back)
    if back is not False:
        return True
    else:
        return False

def get_my_name():
    #FIXME 将来需要处理进程名称,这样是不行的
    Wechat_main = uia.WindowControl(ClassName='WeChatMainWndForPC', searchDepth=1)
    MainControl1 = [i for i in Wechat_main.GetChildren() if not i.ClassName][0]
    MainControl2 = MainControl1.GetFirstChildControl()
    NavigationBox, SessionBox, ChatBox = MainControl2.GetChildren()
    A_MyIcon = NavigationBox.ButtonControl()
    return A_MyIcon.Name
def get_chat_user_name():
    """
    用户吗是在Chatbox中的 需要重新获取,聊天记录用的都是Msglist
    """
    refresh_wechat_window(Main=True, Notify=False)
    con = get_chat_element(Chatbox=True, Msg=False)
    return con[0].Name
def get_chat_element(Chatbox=False,Msg=True):
    """
    Chatbox:整个聊天窗口(更上一层)
    Msg:只有信息部分(下层,面积小)
    返回(元素列表,my_name)
    """
    Wechat_main=uia.WindowControl(ClassName='WeChatMainWndForPC', searchDepth=1) #获取对象
    m_rect=Wechat_main.BoundingRectangle
    # HWND = FindWindow(classname='WeChatMainWndForPC') #获取窗口句柄
    # win32gui.ShowWindow(HWND, 1)
    # Wechat_main.SwitchToThisWindow()
    # 三个布局，导航栏(A)、聊天列表(B)、聊天框(C)
    # _______________
    # |■|———|    -□×|
    # | |———|       |
    # |A| B |   C   |   <--- 微信窗口布局简图示意
    # | |———|———————|
    # |=|———|       |
    # ———————————————
    MainControl1 = [i for i in Wechat_main.GetChildren() if not i.ClassName][0]
    MainControl2 = MainControl1.GetFirstChildControl()
    NavigationBox, SessionBox, ChatBox = MainControl2.GetChildren()
    # print(NavigationBox)#导航栏
    # print(SessionBox)#人物名称栏
    # print(ChatBox)#聊天栏
    #初始化导航栏
    A_MyIcon = NavigationBox.ButtonControl()
    # A_ChatIcon = NavigationBox.ButtonControl(Name='聊天')
    # A_ContactsIcon = NavigationBox.ButtonControl(Name='通讯录')
    # A_FavoritesIcon = NavigationBox.ButtonControl(Name='收藏')
    # A_FilesIcon = NavigationBox.ButtonControl(Name='聊天文件')
    # A_MomentsIcon = NavigationBox.ButtonControl(Name='朋友圈')
    # A_MiniProgram = NavigationBox.ButtonControl(Name='小程序面板')
    # A_Phone = NavigationBox.ButtonControl(Name='手机')
    # A_Settings = NavigationBox.ButtonControl(Name='设置及其他')

    # 初始化聊天列表，以B开头
    B_Search = SessionBox.EditControl(Name='搜索')

    # 初始化聊天栏，以C开头
    C_MsgList = ChatBox.ListControl(Name='消息') #接受消息位置
    # c_rect = C_MsgList.BoundingRectangle
    # print(m_rect)
    # print(c_rect)
    # print(C_MsgList)
    print(A_MyIcon.Name)#我的名称

    # localcation=[c_rect.left-m_rect.left,c_rect.top-m_rect.top]
    # back={}
    # back['location']=localcation
    # back['mouse_range']=[c_rect.xcenter(),c_rect.bottom],[c_rect.xcenter(),c_rect.top]
    if Chatbox is True:
        controls = GetAllControlList(ChatBox)
    elif Msg is True:
        controls = GetAllControlList(C_MsgList)
    else:
        raise ValueError(f'输入参数错误{Chatbox},{Msg}')
    # print(controls)
    # message_list=[(i.Name,i.LocalizedControlType,i.ControlType,i.IsContentElement) for i in controls]
    # print(f'获取到message_list:{message_list}')
    return controls

def get_search_control_location():
    """
    返回search元素的屏幕坐标
    """
    Wechat_main=uia.WindowControl(ClassName='WeChatMainWndForPC', searchDepth=1) #获取对象
    # m_rect=Wechat_main.BoundingRectangle
    MainControl1 = [i for i in Wechat_main.GetChildren() if not i.ClassName][0]
    MainControl2 = MainControl1.GetFirstChildControl()
    NavigationBox, SessionBox, ChatBox = MainControl2.GetChildren()
    B_Search = SessionBox.EditControl(Name='搜索')# 初始化聊天列表
    return B_Search.BoundingRectangle.xcenter(), B_Search.BoundingRectangle.ycenter()

def GetAllControlList(ele):
    def findall(ele, n=0, text=[]):
        if ele.Name:
            text.append(ele)
        eles = ele.GetChildren()
        for ele1 in eles:
            text = findall(ele1, n+1, text)
        return text
    text_list = findall(ele)
    return text_list

def FindWindow(classname=None, name=None):
    """
    查找窗口句柄
    只能根据：
    窗口类名 (classname)
    窗口标题 (name)
    """
    return win32gui.FindWindow(classname, name)

def get_send_button_location():
    """
    查找发送按钮的中心坐标
    """
    Wechat_main = uia.WindowControl(ClassName='WeChatMainWndForPC', searchDepth=1)  # 获取对象
    MainControl1 = [i for i in Wechat_main.GetChildren() if not i.ClassName][0]
    MainControl2 = MainControl1.GetFirstChildControl()
    NavigationBox, SessionBox, ChatBox = MainControl2.GetChildren()
    # 初始化聊天栏，以C开头
    C_MsgList = ChatBox.ListControl(Name='消息')  # 接受消息位置
    controls = GetAllControlList(ChatBox)
    # print(controls)
    message_list = [(i.Name, i.LocalizedControlType, i.ControlType, i.IsContentElement) for i in controls]
    for i in controls:
        if '发送(S)' in i.Name:
            center=[i.BoundingRectangle.xcenter(), i.BoundingRectangle.ycenter()]
            return center



