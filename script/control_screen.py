import os
import sys

# 1. Force Browser to Chrome
os.environ['BROWSER'] = 'google-chrome'

# 2. Fix pkg_resources for Python 3.12+
try:
    import pkg_resources
except ImportError:
    try:
        from setuptools import pkg_resources
        sys.modules["pkg_resources"] = pkg_resources
    except ImportError:
        # Final fallback: mock the version check VPython wants
        import types
        m = types.ModuleType("pkg_resources")
        sys.modules["pkg_resources"] = m
        m.get_distribution = lambda x: types.SimpleNamespace(version="0.0.0")
        m.DistributionNotFound = Exception

# Now it is safe to import the rest
import time
import threading
import math
import tkinter as tk
from tkinter import ttk, messagebox
import serial
import serial.tools.list_ports
from vpython import *

# ... [The rest of your class code follows] ...

# --- 機械參數 (mm) ---
L1, L2 = 105.0, 65.0   

class NTUFRCArm:
    def __init__(self, root):
        self.root = root
        self.root.title("NTU FRC 114-2 - ANIMATED SYNC SYSTEM")
        self.root.geometry("700x950")
        self.root.configure(bg='#0A0A0A')

        # 1. 3D 模擬 (對位視角 + 三軸標註)
        self.init_3d()
        
        # 2. 串口通訊
        self.ser = self.init_serial()
        
        # 3. 數據變數
        self.angles = [tk.DoubleVar(value=0) for _ in range(4)]
        self.angles[3].set(90) 
        self.coords = [tk.StringVar(value=v) for v in ["0", "120", "80"]]
        self.is_animating = False # 防止歸零動畫中被滑桿干擾
        
        self.setup_ui()
        if self.ser:
            threading.Thread(target=self.receive_thread, daemon=True).start()
        self.update_all()

    def init_3d(self):
        self.scene = canvas(title='NTU FRC 114-2 DIGITAL TWIN', width=550, height=450, 
                            center=vector(25, 45, 0), background=color.black)
        self.scene.up = vector(0, 1, 0)
        self.scene.forward = vector(1.0, -0.6, -1.2) 
        
        box(pos=vector(0, -2, 0), size=vector(500, 4, 500), color=color.gray(0.1))
        self.base_v = cylinder(pos=vector(0, 0, 0), axis=vector(0, 15, 0), radius=35, color=color.gray(0.3))
        
        # XYZ 軸標註
        arrow(pos=vector(40, 0.5, 0), axis=vector(60, 0, 0), color=color.red, shaftwidth=2)
        label(pos=vector(110, 5, 0), text='X', height=12, box=False, color=color.red)
        arrow(pos=vector(0, 0.5, 40), axis=vector(0, 0, 60), color=color.green, shaftwidth=2)
        label(pos=vector(0, 5, 110), text='Y', height=12, box=False, color=color.green)
        arrow(pos=vector(0, 15, 0), axis=vector(0, 60, 0), color=color.blue, shaftwidth=2)
        label(pos=vector(0, 85, 0), text='Z', height=12, box=False, color=color.blue)

        self.v_link1 = cylinder(pos=vector(0, 15, 0), axis=vector(L1, 0, 0), radius=7, color=color.cyan, emissive=True)
        self.v_link2 = cylinder(pos=vector(L1, 15, 0), axis=vector(0, L2, 0), radius=5, color=color.red, emissive=True)
        self.v_arrow = arrow(pos=vector(0,0,0), axis=vector(30,0,0), color=color.yellow, shaftwidth=3)

    def init_serial(self):
        for p in serial.tools.list_ports.comports():
            if any(x in p.description for x in ["Arduino", "CH340", "USB"]):
                try: return serial.Serial(p.device, 115200, timeout=0.1)
                except: pass
        return None

    def setup_ui(self):
        style = ttk.Style()
        style.configure("TFrame", background="#0A0A0A")
        style.configure("TLabelframe", background="#0A0A0A", foreground="#39FF14")
        
        main = ttk.Frame(self.root, style="TFrame")
        main.pack(fill="both", expand=True, padx=20, pady=20)
        
        tk.Label(main, text="NTU FRC 114-2 // COMMAND CENTER", bg="#0A0A0A", fg="#39FF14", font=('Consolas', 14, 'bold')).pack(pady=10)

        a_frame = ttk.LabelFrame(main, text="[ AXIS_DIRECT_CONTROL ]")
        a_frame.pack(fill="x", pady=10, padx=10)
        configs = [("BASE (X)", -180, 180), ("ARM (Y)", 0, 140), ("FOREARM (Z)", 0, 180), ("MG90 (Vector)", 0, 180)]
        
        for i, (name, low, high) in enumerate(configs):
            f = tk.Frame(a_frame, bg="#0A0A0A"); f.pack(fill="x", pady=5)
            tk.Label(f, text=f"{name}:", bg="#0A0A0A", fg="#39FF14", width=18, anchor="w").pack(side="left")
            tk.Entry(f, textvariable=self.angles[i], width=6, bg="#1A1A1A", fg="#39FF14").pack(side="left", padx=5)
            tk.Scale(f, from_=low, to=high, variable=self.angles[i], orient="horizontal", bg="#0A0A0A", fg="#39FF14", troughcolor="#1A1A1A", highlightthickness=0, command=lambda v: self.update_all()).pack(side="left", fill="x", expand=True)

        c_frame = ttk.LabelFrame(main, text="[ INVERSE_KINEMATICS ]")
        c_frame.pack(fill="x", pady=10, padx=10)
        input_f = tk.Frame(c_frame, bg="#0A0A0A"); input_f.pack(fill="x")
        for i, n in enumerate(["X", "Y", "Z"]):
            tk.Label(input_f, text=f"{n}:", bg="#0A0A0A", fg="#39FF14").pack(side="left", padx=5)
            tk.Entry(input_f, textvariable=self.coords[i], width=10, bg="#1A1A1A", fg="#39FF14").pack(side="left", padx=10)
        ttk.Button(c_frame, text="EXECUTE_IK_MOVE", command=self.run_ik).pack(fill="x", pady=10)

        # 歸零按鈕觸發平滑動畫
        ttk.Button(main, text="SMOOTH_SYSTEM_RESET", command=self.animated_reset).pack(fill="x", pady=15)

    def run_ik(self):
        try:
            x, y, z = float(self.coords[0].get()), float(self.coords[1].get()), float(self.coords[2].get())
            theta0 = math.degrees(math.atan2(x, y))
            r = math.sqrt(x**2 + y**2)
            dist_sq = r**2 + z**2
            dist = math.sqrt(dist_sq)
            if dist > (L1 + L2) or dist < abs(L1 - L2): raise ValueError("OUT_OF_REACH")
            cos_t2 = (dist_sq - L1**2 - L2**2) / (2 * L1 * L2)
            t2 = math.degrees(math.acos(max(-1, min(1, cos_t2))))
            t1 = math.degrees(math.atan2(z, r) + math.acos((L1**2 + dist_sq - L2**2) / (2 * L1 * dist)))
            self.angles[0].set(round(theta0, 1))
            self.angles[1].set(round(t1 - 50.0, 1))
            self.angles[2].set(round(100.0 - t2, 1))
            self.update_all()
        except Exception as e: messagebox.showerror("IK ERROR", str(e))

    def update_all(self, *args):
        if self.is_animating: return # 動畫中暫停手動更新
        rate(60) 
        a = [v.get() for v in self.angles]
        self.render_arm(a)
        self.send_serial(a)

    def render_arm(self, a):
        # 核心 3D 渲染邏輯
        r_base, r_arm = math.radians(a[0]), math.radians(50 + a[1])
        r_forearm = math.radians((50 + a[1]) + (100 - a[2])) 
        self.v_link1.axis = vector(L1*math.cos(r_arm)*math.cos(r_base), L1*math.sin(r_arm), L1*math.cos(r_arm)*math.sin(r_base))
        self.v_link2.pos = self.v_link1.pos + self.v_link1.axis
        self.v_link2.axis = vector(L2*math.cos(r_forearm)*math.cos(r_base), L2*math.sin(r_forearm), L2*math.cos(r_forearm)*math.sin(r_base))
        self.v_arrow.pos = self.v_link2.pos + self.v_link2.axis
        phi = math.radians(a[3])
        self.v_arrow.axis = vector(30 * math.sin(phi), 30 * math.cos(phi), 0)

    def send_serial(self, a):
        if self.ser and self.ser.is_open:
            data = f"{a[0]:.1f},{a[1]:.1f},{a[2]:.1f},{a[3]:.1f}\n"
            self.ser.write(data.encode())

    def receive_thread(self):
        while True:
            if self.ser and self.ser.in_waiting:
                try: self.ser.readline()
                except: pass
            time.sleep(0.05)

    def animated_reset(self):
        """啟動平滑歸零動畫執行緒"""
        threading.Thread(target=self._reset_logic, daemon=True).start()

    def _reset_logic(self):
        self.is_animating = True
        steps = 30 # 動畫總步數
        start_vals = [v.get() for v in self.angles]
        target_vals = [0, 0, 0, 90] # 歸零目標角度
        
        for i in range(1, steps + 1):
            curr_vals = []
            for j in range(4):
                # 線性插值計算
                val = start_vals[j] + (target_vals[j] - start_vals[j]) * (i / steps)
                curr_vals.append(val)
                self.angles[j].set(round(val, 1))
            
            # 更新 3D 圖
            self.render_arm(curr_vals)
            # 同步發送串口給實體馬達
            self.send_serial(curr_vals)
            time.sleep(0.02) # 總共約 0.6 秒歸零
            
        self.is_animating = False

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = NTUFRCArm(root)
        root.mainloop()
    except Exception as e:
        print(f"CRITICAL: {e}")
        input("Exit...")
