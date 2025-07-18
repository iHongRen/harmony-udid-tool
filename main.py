import os
import platform
import subprocess
import sys
import threading
import tkinter as tk
from time import sleep
from tkinter import ttk


class HdcUdidApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("HarmonyOS UDID 获取工具")
        # --- 设置图标 ---
        self.set_app_icon()

        menubar = tk.Menu(self)
        if platform.system() == "Darwin":
            app_menu = tk.Menu(menubar, name='apple')
            menubar.add_cascade(menu=app_menu)
            app_menu.add_command(label="关于", command=self.show_about)
        else:
            helpmenu = tk.Menu(menubar, tearoff=0)
            helpmenu.add_command(label="关于", command=self.show_about)
            menubar.add_cascade(label="帮助", menu=helpmenu)
       
        self.config(menu=menubar)


        self.configure(bg="#f7f7f7")

        # --- 窗口居中 ---
        window_width = 500
        window_height = 220
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        center_x = int(screen_width / 2 - window_width / 2)
        center_y = int(screen_height / 2 - window_height / 2)
        self.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        self.resizable(False, False)

        # --- 统一字体 ---
        default_font = ("Arial", 11)
        title_font = ("Arial", 13, "bold")

        # 颜色常量定义
        COLOR_PRIMARY = "#4F8EF7"        # 主色调-蓝色
        COLOR_PRIMARY_DARK = "#2566d8"   # 主色调深色(悬停)
        COLOR_PRIMARY_LIGHT = "#7ba6f1"  # 主色调浅色(禁用)
        COLOR_BACKGROUND = "#f7f7f7"     # 背景色
        COLOR_FOREGROUND = "#333333"     # 前景色
        COLOR_DISABLED = "#999999"       # 禁用文本色
        COLOR_BORDER = "#cccccc"         # 边框色
        COLOR_SELECTION = "#4a86e8"      # 选中状态色

        style = ttk.Style(self)
        style.theme_use('clam')
        # 按钮圆角+禁用时字体白色
        style.configure('Rounded.TButton',
                        font=default_font,
                        padding=6,
                        relief="flat",
                        background=COLOR_PRIMARY,
                        foreground="white",
                        borderwidth=0)
        style.map('Rounded.TButton',
                  background=[('active', COLOR_PRIMARY_DARK), ('disabled', COLOR_PRIMARY_LIGHT)],
                  foreground=[('disabled', 'white')])
        
        # Combobox 样式 - 增强圆角模拟和交互
        style.configure('Rounded.TCombobox',
                        padding=2,
                        font=default_font,
                        fieldbackground="white",
                        background=COLOR_BACKGROUND,
                        relief="flat",
                        bordercolor=COLOR_BORDER,
                        arrowcolor=COLOR_FOREGROUND,
                        selectbackground=COLOR_SELECTION,
                        selectforeground="white")

        style.map('Rounded.TCombobox',
                fieldbackground=[('focus', 'white'), 
                                ('readonly', COLOR_BACKGROUND)],
                background=[('active', COLOR_BACKGROUND)],
                bordercolor=[('focus', COLOR_PRIMARY)],
                arrowcolor=[('disabled', COLOR_DISABLED)])
        
        style.configure('TLabel', font=default_font, background=COLOR_BACKGROUND)

        self.hdc_path = self.find_hdc_executable()
        self.status_value = tk.StringVar(value="请刷新设备")

        # --- UI 布局 ---
        container = tk.Frame(self, bg=COLOR_BACKGROUND)
        container.pack(expand=True, fill=tk.BOTH, padx=30, pady=18)

        # --- 设备选择 ---
        device_frame = tk.Frame(container, bg=COLOR_BACKGROUND)
        device_frame.pack(fill='x', pady=(0, 8))
        tk.Label(device_frame, text="设备", font=title_font, bg=COLOR_BACKGROUND).pack(side=tk.LEFT)
        self.device_combobox = ttk.Combobox(device_frame, state="readonly", font=default_font, style='Rounded.TCombobox')
        self.device_combobox.pack(side=tk.LEFT, fill='x', expand=True, padx=12)
        self.device_combobox.bind("<<ComboboxSelected>>", self.on_device_select)

        # --- UDID 显示 ---
        tk.Label(container, text="UDID", font=title_font, bg=COLOR_BACKGROUND).pack(pady=(0, 2))
        self.udid_text = tk.Text(container, font=default_font, wrap=tk.WORD, height=2, relief=tk.FLAT,
                                bg=COLOR_BACKGROUND, bd=0, highlightthickness=0, fg=COLOR_FOREGROUND)
        self.udid_text.pack(pady=4, fill="x", expand=True)
        self.udid_text.tag_configure("center", justify='center')
        self.udid_text.insert("1.0", "请先选择设备", "center")
        self.udid_text.config(state="disabled")
        self.udid_text.bind("<Button-3>", self.show_udid_menu)  # 添加右键菜单绑定

        # 创建右键菜单
        self.udid_menu = tk.Menu(self.udid_text, tearoff=0)
        self.udid_menu.add_command(label="复制", command=self.copy_udid_selection)

        # --- 状态栏 ---
        status_bar = tk.Label(container, textvariable=self.status_value, font=("Arial", 9), fg="#888", bg=COLOR_BACKGROUND, anchor="w")
        status_bar.pack(fill='x', pady=(2, 8))

        # --- 按钮区域 ---
        button_frame = tk.Frame(container, bg=COLOR_BACKGROUND)
        button_frame.pack(fill='x', pady=2)  # 使用 fill='x' 让按钮区域横向填充

        # 使用 grid 布局并设置权重，让三个按钮均分空间
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)

        self.refresh_button = ttk.Button(button_frame, text="刷新设备", command=self.refresh_devices, style='Rounded.TButton')
        self.refresh_button.grid(row=0, column=0, padx=8, pady=8, sticky='ew')  # 使用 sticky='ew' 实现左右对齐

        self.copy_button = ttk.Button(button_frame, text="复制 UDID", command=self.copy_udid, state=tk.DISABLED, style='Rounded.TButton')
        self.copy_button.grid(row=0, column=1, padx=8, pady=8, sticky='ew')  # 使用 sticky='ew' 实现左右对齐

        self.exit_button = ttk.Button(button_frame, text="退出", command=self.on_exit, style='Rounded.TButton')
        self.exit_button.grid(row=0, column=2, padx=8, pady=8, sticky='ew')  # 使用 sticky='ew' 实现左右对齐

        self.protocol("WM_DELETE_WINDOW", self.on_exit)
        self.refresh_devices()

    def get_resource_path(self, relative_path):
        """获取资源文件的绝对路径，兼容 PyInstaller 打包"""
        try:
            # PyInstaller 打包后的临时目录
            base_path = sys._MEIPASS
        except AttributeError:
            # 开发环境
            base_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_path, relative_path)

    def set_app_icon(self):
        """跨平台设置应用图标"""
        if platform.system() == "Windows":
            # Windows 需要 .ico 格式
            icon_path = self.get_resource_path("icon.ico")
            if os.path.exists(icon_path):
                self.iconbitmap(default=icon_path)
            
        elif platform.system() == "Darwin":
            # macOS 下可以尝试使用 iconphoto，但主要依赖打包时的配置
            icon_path = self.get_resource_path("icon.png")
            try:
                if os.path.exists(icon_path):
                    icon = tk.PhotoImage(file=icon_path)
                    self.iconphoto(True, icon)
            except:
                pass  # macOS 主要通过打包配置图标
                
        else:  # Linux 及其他系统
            # Linux 支持 .png 格式
            icon_path = self.get_resource_path("icon.png")
            try:
                if os.path.exists(icon_path):
                    icon = tk.PhotoImage(file=icon_path)
                    self.iconphoto(True, icon)
            except:
                pass  # 失败则使用默认图标

    def find_hdc_executable(self):
        hdc_path = self.get_resource_path('hdc')
        
        # 检查 hdc 文件是否存在
        if not os.path.isfile(hdc_path):
            raise FileNotFoundError(f"hdc executable not found at {hdc_path}")
        
        return hdc_path 

    def run_hdc_command(self, command):
        try:
            hdc_path = self.find_hdc_executable()
            if platform.system() != "Windows":
                if not os.access(hdc_path, os.X_OK):
                    os.chmod(hdc_path, 0o755)
            
            # 设置动态库搜索路径
            env = os.environ.copy()
            if platform.system() == "Darwin":
                # macOS 动态库路径 - 使用资源目录而不是 hdc 文件路径
                lib_dir = os.path.dirname(self.get_resource_path('libusb_shared.dylib'))
                env["DYLD_LIBRARY_PATH"] = lib_dir
                # 强制加载指定路径的库（即使系统已有同名库）
                env["DYLD_FORCE_FLAT_NAMESPACE"] = "1"

            startupinfo = None
            if platform.system() == "Windows":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            process = subprocess.run(
                [hdc_path] + command,
                capture_output=True, text=True, encoding='utf-8', check=False, startupinfo=startupinfo
            )
            print(f"Command: {' '.join([hdc_path] + command)}")
            print(f"process: {process}")
          
            return process.stdout.strip(), process.stderr.strip()
        except Exception as e:
            print(f"Error running command: {command} - {e}")
            return None, str(e)
    def refresh_devices(self):
        self.status_value.set("正在刷新设备列表...")
        # self.device_combobox.set('')
        self.device_combobox.config(state=tk.DISABLED)
        self.refresh_button.config(state=tk.DISABLED)
        self.copy_button.config(state=tk.DISABLED)
        self.update_ui_text("正在刷新...")
        threading.Thread(target=self.fetch_devices_task, daemon=True).start()

    def fetch_devices_task(self):
        list_stdout, _ = self.run_hdc_command(["list", "targets"])
        device_sns = list_stdout.splitlines()
        if not device_sns:
            self.after(0, self.update_device_list, [], "未检测到设备，请连接...")
            return
        self.after(0, self.update_device_list, device_sns, "请从列表中选择一个设备")

    def update_device_list(self, device_names, status):
        # 记录当前选中项
        current = self.device_combobox.get()
        self.device_combobox['values'] = device_names
        if device_names:
            self.device_combobox.config(state="readonly")
            # 如果当前选中项还在新列表里，则保持不变，否则选中第一个
            if current in device_names:
                self.device_combobox.set(current)
            else:
                self.device_combobox.set(device_names[0])
            self.on_device_select(None) # 自动触发第一个设备的选择事件
        else:
            # 只有真正没有设备时才清空
            self.device_combobox.set('')
            self.device_combobox.config(state="disabled")
            self.update_ui_text("未检测到设备")
        self.status_value.set(status)
        self.refresh_button.config(state=tk.NORMAL)

    def on_device_select(self, event):
        selected_display_name = self.device_combobox.get()
        if selected_display_name:
            self.status_value.set(f"正在为 {selected_display_name} 获取UDID...")
            self.copy_button.config(state=tk.DISABLED)
            self.update_ui_text("...")
            threading.Thread(target=self.fetch_udid_task, args=(selected_display_name,), daemon=True).start()
        # 取消 Combobox 的选中高亮
        self.device_combobox.selection_clear()
        self.device_combobox.icursor(0)
        self.focus()  # 让 Combobox 失去焦点

    def fetch_udid_task(self, selected_display_name):
        udid_stdout, udid_stderr = self.run_hdc_command(["-t", selected_display_name, "shell", "bm", "get", "-u"])
        final_udid, final_status = self.parse_udid(udid_stdout, udid_stderr)
        self.after(0, self.update_udid_display, final_udid, final_status)

    def parse_udid(self, stdout, stderr):
        if stdout and "udid" in stdout.lower():
            try:
                udid = stdout.split(':', 1)[1].strip()
                if len(udid) > 10:
                    return udid, "成功获取UDID"
                else:
                    raise ValueError("Invalid UDID format")
            except (IndexError, ValueError):
                return "获取UDID失败", f"设备返回无效结果: {stdout}"
        elif stdout:
            return stdout.strip(), ""
        else:
            if "not found" in stderr.lower():
                return "获取UDID失败", "错误: 设备上未找到 'bm' 工具。"
            else:
                return "获取UDID失败", "错误: 请确保设备已解锁且HDC已授权。"

    def update_udid_display(self, udid, status):
        self.update_ui_text(udid)
        self.status_value.set(status)
        if "失败" not in udid and "未检测" not in udid:
            self.copy_button.config(state=tk.NORMAL)
        else:
            self.copy_button.config(state=tk.DISABLED)

    def update_ui_text(self, text):
        self.udid_text.config(state=tk.NORMAL)
        self.udid_text.delete("1.0", tk.END)
        self.udid_text.insert("1.0", text, "center")
        self.udid_text.config(state=tk.DISABLED)

    def copy_udid(self):
        current_udid = self.udid_text.get("1.0", tk.END).strip()
        if current_udid and "失败" not in current_udid and "未检测" not in current_udid and "..." not in current_udid:
            self.clipboard_clear()
            self.clipboard_append(current_udid)
            self.show_toast("UDID 已复制到剪贴板")

    def show_toast(self, message):
        # 水平居中弹窗
        toast = tk.Toplevel(self)
        toast.overrideredirect(True)
        toast.configure(bg="#333333")
        toast.attributes("-topmost", True)
        x = self.winfo_x() + (self.winfo_width() - 140) // 2
        y = self.winfo_y() + self.winfo_height() - 60
        toast.geometry(f"140x30+{x}+{y}")
        label = tk.Label(toast, text=message, fg="white", bg="#333333", font=("Arial", 9))
        label.pack(expand=True, fill="both")
        toast.after(1500, toast.destroy)

    def show_udid_menu(self, event):
        try:
            self.udid_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.udid_menu.grab_release()

    def copy_udid_selection(self):
        try:
            selected = self.udid_text.get(tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError:
            selected = self.udid_text.get("1.0", tk.END).strip()
        if selected:
            self.clipboard_clear()
            self.clipboard_append(selected)

    def on_exit(self):
        self.destroy()

    def show_about(self):
        about = tk.Toplevel(self)
        about.title("关于")
        about.geometry("320x180")
        about.resizable(False, False)
        
        # 标题
        tk.Label(about, text="HarmonyOS UDID 获取工具", font=("Arial", 13, "bold")).pack(pady=(20, 5))
        tk.Label(about, text="版本：v1.0.0", font=("Arial", 11)).pack(pady=2)
        tk.Label(about, text="作者：@仙银", font=("Arial", 11)).pack(pady=2)
        
        # 链接标签 - 显示为蓝色并添加下划线
        link = tk.Label(
            about, 
            text="https://github.com/iHongRen/hdc-uuid-tool", 
            font=("Arial", 10, "underline"),
            fg="#0057ff",  # 链接蓝
            cursor="hand"  # 鼠标悬停时显示手型
        )
        link.pack(pady=(10, 0))
        
        # 绑定点击事件 - 使用默认浏览器打开链接
        def open_link(event):
            import webbrowser
            webbrowser.open_new("https://github.com/iHongRen/hdc-uuid-tool")
        
        link.bind("<Button-1>", open_link)
        link.bind("<Enter>", lambda e: link.config(fg="#1e1eff"))  # 鼠标悬停时颜色加深
        link.bind("<Leave>", lambda e: link.config(fg="#0057ff"))  # 鼠标离开时恢复原色


if __name__ == "__main__":
    app = HdcUdidApp()
    app.mainloop()
