import os
import platform
import subprocess
import threading
import tkinter as tk
from time import sleep
from tkinter import messagebox


class HdcUdidApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("HarmonyOS UDID 获取工具")

        # --- 窗口居中 ---
        window_width = 640
        window_height = 240
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        center_x = int(screen_width / 2 - window_width / 2)
        center_y = int(screen_height / 2 - window_height / 2)
        self.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

        self.resizable(True, False)
        try:
            # 确保有一个icon.ico文件在同一目录下
            self.iconbitmap("icon.ico")
        except tk.TclError:
            print("icon.ico not found, skipping.")
            
        self.hdc_path = self.find_hdc_executable()
        
        self.server_started_by_app = False
        self.status_value = tk.StringVar(value="请连接设备并授权USB调试")

        # --- UI 布局 (整体居中) ---
        container = tk.Frame(self)
        container.pack(expand=True)

        tk.Label(container, text="设备 UDID:", font=("Arial", 12)).pack(pady=(10, 0))
        
        self.udid_text = tk.Text(container, font=("Courier", 14), wrap=tk.WORD, height=5, relief=tk.SOLID, borderwidth=1)
        self.udid_text.pack(pady=5, padx=20, fill="x", expand=True)
        self.udid_text.tag_configure("center", justify='center')
        self.udid_text.insert("1.0", "正在初始化...", "center")
        self.udid_text.config(state="disabled")

        tk.Label(container, textvariable=self.status_value, font=("Arial", 10), fg="grey").pack(pady=(0, 10))

        button_frame = tk.Frame(container)
        button_frame.pack(pady=5)

        self.refresh_button = tk.Button(button_frame, text="刷新", command=self.refresh_udid, width=12)
        self.refresh_button.pack(side=tk.LEFT, padx=10)

        self.copy_button = tk.Button(button_frame, text="复制 UDID", command=self.copy_udid, width=12)
        self.copy_button.pack(side=tk.LEFT, padx=10)
        self.copy_button.config(state=tk.DISABLED)

        self.exit_button = tk.Button(button_frame, text="退出", command=self.on_exit, width=12)
        self.exit_button.pack(side=tk.LEFT, padx=10)

        self.protocol("WM_DELETE_WINDOW", self.on_exit)
        self.refresh_udid()

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

    def refresh_udid(self):
        self.status_value.set("正在刷新...")
        self.refresh_button.config(state=tk.DISABLED)
        self.copy_button.config(state=tk.DISABLED)
        
        self.udid_text.config(state=tk.NORMAL)
        self.udid_text.delete("1.0", tk.END)
        self.udid_text.insert("1.0", "...", "center")
        self.udid_text.config(state=tk.DISABLED)
        
        self.update_idletasks()
        threading.Thread(target=self.fetch_udid_task, daemon=True).start()

    def fetch_udid_task(self):
        # 1. 检查并启动HDC服务
        self.after(0, self.status_value.set, "HDC服务正在启动...")
        self.run_hdc_command(["start"])
        self.server_started_by_app = True
        # 等待HDC服务启动 
        sleep(1)


        # 2. 获取设备序列号 (SN)
        self.after(0, self.status_value.set, "正在获取设备列表...")
        list_stdout, list_stderr = self.run_hdc_command(["list", "targets"])
        print(f"设备列表输出: {list_stdout}")
        device_sn = None
        if list_stdout:
            device_lines = list_stdout.splitlines()
            # 找到第一个非空行作为SN
            for line in device_lines:
                if line.strip():
                    device_sn = line.split()[0]
                    break

        if not device_sn:
            self.after(0, self.update_ui, "未检测到设备", "请连接设备或检查HDC授权")
            return

        # 3. 使用SN获取真实UDID
        self.after(0, self.status_value.set, f"检测到设备: {device_sn[:12]}... 正在获取UDID...")
        udid_stdout, udid_stderr = self.run_hdc_command(["-t", device_sn, "shell", "bm", "get", "-u"])

        final_udid = ""
        final_status = ""
        if udid_stdout and "udid" in udid_stdout.lower():
            try:
                # 尝试从 'udid: XXXXX' 格式中提取
                final_udid = udid_stdout.split(':', 1)[1].strip()
                if len(final_udid) > 10: # 简单验证UDID长度
                    final_status = "成功获取UDID"
                else:
                    raise ValueError("Invalid UDID format")
            except (IndexError, ValueError):
                final_udid = "获取UDID失败"
                final_status = f"设备返回无效结果: {udid_stdout}"
        elif udid_stdout: # 如果有输出但格式不符
             final_udid = udid_stdout.strip()
             final_status = "获取到部分信息(请验证)"
        else:
            final_udid = "获取UDID失败"
            if "not found" in udid_stderr.lower():
                final_status = "错误: 设备上未找到 'bm' 工具。"
            else:
                final_status = "错误: 请确保设备已解锁且HDC已授权。"

        self.after(0, self.update_ui, final_udid, final_status)

    def update_ui(self, udid, status):
        self.udid_text.config(state=tk.NORMAL)
        self.udid_text.delete("1.0", tk.END)
        self.udid_text.insert("1.0", udid, "center")
        self.udid_text.config(state=tk.DISABLED)
        
        self.status_value.set(status)
        self.refresh_button.config(state=tk.NORMAL)
        
        if "失败" not in udid and "未检测" not in udid:
            self.copy_button.config(state=tk.NORMAL)
        else:
            self.copy_button.config(state=tk.DISABLED)

    def copy_udid(self):
        current_udid = self.udid_text.get("1.0", tk.END).strip()
        if current_udid and "失败" not in current_udid and "未检测" not in current_udid and "..." not in current_udid:
            self.clipboard_clear()
            self.clipboard_append(current_udid)
            messagebox.showinfo("成功", "UDID 已复制到剪贴板！")

    def on_exit(self):
        if self.server_started_by_app:
            print("Killing HDC server...")
            self.run_hdc_command(["kill"])
        self.destroy()

if __name__ == "__main__":
    app = HdcUdidApp()
    app.mainloop()