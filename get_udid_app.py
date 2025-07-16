import os
import platform
import subprocess
import threading
import tkinter as tk
from time import sleep
from tkinter import messagebox, ttk


class HdcUdidApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("HarmonyOS UDID 获取工具")
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

    def find_hdc_executable(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(current_dir, 'hdc-tool', 'hdc')

    def run_hdc_command(self, command):
        try:
            if platform.system() != "Windows":
                os.chmod(self.hdc_path, 0o755)
            startupinfo = None
            if platform.system() == "Windows":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            process = subprocess.run(
                [self.hdc_path] + command,
                capture_output=True, text=True, encoding='utf-8', check=False, startupinfo=startupinfo
            )
            print('----'+process.stdout.strip(), process.stderr.strip())
            return process.stdout.strip(), process.stderr.strip()
        except Exception as e:
            print(f"Error running command: {command} - {e}")
            return None, str(e)

    def refresh_devices(self):
        self.status_value.set("正在刷新设备列表...")
        self.device_combobox.set('')
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
        self.device_combobox['values'] = device_names
        if device_names:
            self.device_combobox.config(state="readonly")
            self.device_combobox.set(device_names[0])
            self.on_device_select(None) # 自动触发第一个设备的选择事件
        else:
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

if __name__ == "__main__":
    app = HdcUdidApp()
    app.mainloop()
