
import os
import platform
import subprocess
import threading
import tkinter as tk
from time import sleep
from tkinter import messagebox, ttk


class Toast:
    def __init__(self, parent, message):
        self.parent = parent
        self.message = message
        
        # --- Toast 窗口创建与居中 ---
        self.toast_window = tk.Toplevel(parent)
        self.toast_window.overrideredirect(True) # 隐藏标题栏
        self.toast_window.attributes("-alpha", 0.9) # 设置透明度
        self.toast_window.attributes("-topmost", True) # 保持在最前

        label = tk.Label(self.toast_window, text=self.message, 
                         bg="#323232", fg="white", 
                         font=("Arial", 10), 
                         padx=20, pady=10)
        label.pack()

        # --- 位置计算 (在父窗口下方) ---
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        self.toast_window.update_idletasks()
        toast_width = self.toast_window.winfo_width()
        toast_height = self.toast_window.winfo_height()

        x = parent_x + (parent_width // 2) - (toast_width // 2)
        y = parent_y + parent_height - toast_height - 30 # 距离底部30像素

        self.toast_window.geometry(f'+{x}+{y}')
        self.toast_window.after(2000, self.destroy)

    def destroy(self):
        self.toast_window.destroy()

class HdcUdidApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("HarmonyOS UDID 获取工具")

        # --- 窗口居中 ---
        window_width = 600
        window_height = 200
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        center_x = int(screen_width / 2 - window_width / 2)
        center_y = int(screen_height / 2 - window_height / 2)
        self.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

        self.resizable(True, False)
        try:
            self.iconbitmap("icon.ico")
        except tk.TclError:
            print("icon.ico not found, skipping.")
            
        self.hdc_path = self.find_hdc_executable()
        self.status_value = tk.StringVar(value="请点击刷新以获取设备列表")

        # --- UI 布局 (整体居中) ---
        container = tk.Frame(self)
        container.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)

        # --- 设备选择 ---
        device_frame = tk.Frame(container)
        device_frame.pack(fill='x', pady=(5,0))
        tk.Label(device_frame, text="选择设备:", font=("Arial", 12)).pack(side=tk.LEFT)
        self.device_combobox = ttk.Combobox(device_frame, state="readonly", font=("Arial", 10))
        self.device_combobox.pack(side=tk.LEFT, fill='x', expand=True, padx=10)
        self.device_combobox.bind("<<ComboboxSelected>>", self.on_device_select)

        # --- UDID 显示 ---
        tk.Label(container, text="设备 UDID:", font=("Arial", 12)).pack(pady=(10, 0))
        self.udid_text = tk.Text(container, font=("Courier", 14), wrap=tk.WORD, height=5, relief=tk.FLAT, bg=self.cget('bg'))
        self.udid_text.pack(pady=5, fill="x", expand=True)
        self.udid_text.tag_configure("center", justify='center')
        self.udid_text.insert("1.0", "请先选择设备", "center")
        self.udid_text.config(state="disabled")

        tk.Label(container, textvariable=self.status_value, font=("Arial", 10), fg="grey").pack(pady=(0, 10))

        # --- 按钮区域 ---
        button_frame = tk.Frame(container)
        button_frame.pack(pady=5)

        self.refresh_button = tk.Button(button_frame, text="刷新设备", command=self.refresh_devices, width=12)
        self.refresh_button.pack(side=tk.LEFT, padx=10)

        self.copy_button = tk.Button(button_frame, text="复制 UDID", command=self.copy_udid, width=12, state=tk.DISABLED)
        self.copy_button.pack(side=tk.LEFT, padx=10)

        self.exit_button = tk.Button(button_frame, text="退出", command=self.on_exit, width=12)
        self.exit_button.pack(side=tk.LEFT, padx=10)

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
        self.run_hdc_command(["start"])
        sleep(1)    
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
            return stdout.strip(), "获取到部分信息(请验证)"
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
            self.show_toast("UDID 已复制到剪贴板！")

    def show_toast(self, message):
        Toast(self, message)

    def on_exit(self):
        print("Killing HDC server...")
        self.run_hdc_command(["kill"])
        self.destroy()

if __name__ == "__main__":
    app = HdcUdidApp()
    app.mainloop()
