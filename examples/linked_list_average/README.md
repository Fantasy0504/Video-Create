# 例6：递归求链表平均值（完善版）

[播放第五版成片](linked_list_average_v5_clear_tips.mp4) · [预览](preview.png)

根据提供的 62 秒原视频重新制作，使用 Video-Create main 分支
5f0e40163fec07322b2bbfd7a78459dbd361f3fe 的引擎与递归模板规范。

保留原 C++ 算法与输入 1 → 2 → 3；展示逐句执行、三次调用、两次 ave 赋值，
以及按 3、2.5、2 顺序返回。n 始终是从当前 p 开始的实际结点数。
尾调用直接返回 p->data，不虚构 ave 局部变量。

文字更新采用先淡出旧文字、再淡入新文字，避免原视频返回阶段的叠字。
第五版在调用框右侧增加专用细箭头通道：递归调用用蓝色箭头向下动态绘制，
返回用绿色箭头向上动态绘制，并用移动标记显示流向，返回时显示对应数值。
等待子调用的祖先框保持蓝色，已返回的调用框与对应连接转为绿色。
统一复用 engine.flow.recursion_arrow（thickness=1.2），保留细箭身；tip_width_ratio=8.0 单独放大尖端，1080p 下常规尖端约 19px 宽、17px 长。接入线宽 1.6，移动点半径 0.035。
右侧调用记录包含历史返回条目，左侧当前栈帧只显示真实活动栈顶。
结尾给出结果核对、算法要点、时间 O(n) 和辅助空间 O(n)。
辅助空间仅指递归算法的调用栈，不计渲染对象与动画执行记录。
输入前提为 p 非空，且 n 与剩余链表长度一致。此代码不支持空链表输入。

## 本机渲染

项目根目录执行：

```powershell
& 'D:\Fantasy0504的项目\ManimGL\.venv\Scripts\manimgl.exe' examples/linked_list_average/scene.py LinkedListAverage -w -r 1920x1080 --fps 30 --file_name linked_list_average_v5_clear_tips
```

输出 1920×1080、30fps、H.264 MP4，中文字幕，无配音或背景音乐。
执行记录会写入本目录 execution_trace.json。
