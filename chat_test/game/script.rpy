# 游戏的脚本可置于此文件中。

# 声明此游戏使用的角色。颜色参数可使角色姓名着色。
define config.gl2 = True

define Hiyori = Character("Hiyori")

# 游戏在此开始。


label start:

    # 显示一个背景。此处默认显示占位图，但您也可以在图片目录添加一个文件
    # （命名为 bg room.png 或 bg room.jpg）来显示。不带空格可能renpy显示文件不存在。

    scene bg room

    # 显示角色立绘。此处使用了占位图，但您也可以在图片目录添加命名为
    # eileen happy.png 的文件来将其替换掉。

    # 此处显示各行对话。
    $ import requests
    $ import os
    $ import threading
    $ import time

    init python:
        def MyLive2D(*args, fallback=Placeholder(text="不支持Live2D"), **kwargs):
            if renpy.has_live2d():
                 return Live2D(*args, **kwargs)
            else:
                 return fallback

    image Hiyori = MyLive2D(r"path/to/Hiyori.model3.json", base=0.6, loop=True, fallback="eileen happy")  # 请自己修改地址，建议用绝对路径

    show Hiyori m01  # 关于live2d的动作演示，请下载Live2D Cubims查看。
    Hiyori "开始"

    $ text = renpy.input('输入文本')
    python:
        def start():
            with open(r'path/to/start_time.txt', mode='w', encoding='utf-8') as f:
                f.write('T')

        def get_words():
            with open(r'path/to/words.txt', mode='w', encoding='utf-8') as f:
                f.write(text)

        def get_answer():
            if os.path.exists(r'path/to/output.txt'):
                an = ''
                with open(r'path/to/words.txt', mode='r', encoding='utf-8') as f:
                    for i in f:
                        an +=  ''.join(i)
                return an
            else:
                time.sleep(2)
                get_answer()

        t1 = threading.Thread(target=get_words)
        t2 = threading.Thread(target=start)
        t1.start()
        t2.start()
        t1.join()
        t2.join()

    '请触摸屏幕并稍等'
    python:
        def check_time():
            wd = ''
            with open(r'path/to/success_time_B.txt', mode='r', encoding='utf-8') as f:
                for i in f:
                    wd += ''.join(i)
            if 'T' in wd:
                with open(r'path/to/success_time_B.txt', mode='w', encoding='utf-8') as g:
                    g.write('')
                return True
            else:
                time.sleep(1)
                check_time()
        time.sleep(1)
        check_time()

    jump reply

label reply:
    scene bg room
    show Hiyori

    play sound 'path/to/output.ogg'
    $ answer = get_answer()
    show Hiyori m02
    Hiyori '[answer]'
    jump start
    # 此处为游戏结尾。

    return
