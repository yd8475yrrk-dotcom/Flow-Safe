import customtkinter as ctk # type: ignore
import threading
import time
import sys
import os
import json
from PIL import Image, ImageDraw # type: ignore
import pystray # type: ignore
import pygetwindow as gw # type: ignore

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

class SplashScreen(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("")
        self.overrideredirect(True)
        self.configure(fg_color="#1e1e2e")
        
        width, height = 400, 280
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)
        
        self.icon_frame = ctk.CTkFrame(self, width=60, height=60, corner_radius=30, fg_color="#252538", border_width=2, border_color="#a6e3a1")
        self.icon_frame.grid(row=0, column=0, pady=(30, 0))
        self.icon_frame.grid_propagate(False)
        
        self.icon_text = ctk.CTkLabel(self.icon_frame, text="OK", font=("Segoe UI", 16, "bold"), text_color="#a6e3a1")
        self.icon_text.place(relx=0.5, rely=0.5, anchor="center")
        
        self.title_label = ctk.CTkLabel(self, text="FLOW-SAFE", font=("Segoe UI", 26, "bold"), text_color="#a6e3a1")
        self.title_label.grid(row=1, column=0, pady=(10, 5))
        
        self.subtitle_label = ctk.CTkLabel(self, text="Güvenli Odak Asistanı Başlatılıyor...", font=("Segoe UI", 12), text_color="#cdd6f4")
        self.subtitle_label.grid(row=2, column=0, pady=(0, 5))
        
        self.progress = ctk.CTkProgressBar(self, width=280, mode="indeterminate", progress_color="#a6e3a1")
        self.progress.grid(row=3, column=0, pady=(0, 30))
        self.progress.start()
        
        self.after(3000, self.finish_loading)

    def finish_loading(self):
        self.progress.stop()
        self.destroy()
        if self.parent.winfo_exists():
            self.parent.deiconify()
            self.parent.update()


class CustomBreakDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("MOLA ZAMANI!")
        self.overrideredirect(True) 
        self.attributes('-topmost', True) 
        
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}+0+0")
        self.configure(fg_color="#11111b")
        
        try: self.grab_set()
        except: pass
        
        self.remaining_time = 30
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        self.label = ctk.CTkLabel(self, text="⌛ GÖZLERİNİ DİNLENDİR!", font=("Segoe UI", 32, "bold"), text_color="#f38ba8")
        self.label.grid(row=0, column=0, pady=(100, 10), sticky="s")
        
        self.info = ctk.CTkLabel(self, text="45 dakikadır aralıksız çalışıyorsun.\nLütfen ayağa kalk, esne ve uzağa bak.", font=("Segoe UI", 18), text_color="#cdd6f4")
        self.info.grid(row=1, column=0, pady=20, sticky="n")
        
        self.close_btn = ctk.CTkButton(self, text=f"Lütfen Bekleyin ({self.remaining_time})", font=("Segoe UI", 16, "bold"), 
                                       fg_color="#313244", state="disabled", width=250, height=50, corner_radius=10, text_color_disabled="#6c7086")
        self.close_btn.grid(row=2, column=0, pady=(0, 100))
        
        self.countdown()

    def countdown(self):
        if self.remaining_time > 0:
            self.remaining_time -= 1
            self.close_btn.configure(text=f"Lütfen Bekleyin ({self.remaining_time})")
            self.after(1000, self.countdown)
        else:
            self.close_btn.configure(state="normal", text="Çalışmaya Devam Et 🚀", fg_color="#a6e3a1", text_color="#11111b", command=self.close_dialog)

    def close_dialog(self):
        try: self.grab_release()
        except: pass
        self.destroy()


class StatsWindow(ctk.CTkToplevel):
    def __init__(self, parent, focus, fun, idle):
        super().__init__(parent)
        self.title("Günlük Üretkenlik Raporu")
        self.geometry("420x350")
        self.resizable(False, False)
        self.configure(fg_color="#1e1e2e")
        self.attributes('-topmost', True)

        self.title_label = ctk.CTkLabel(self, text="📊 Bugün Zamanını Nasıl Geçirdin?", font=("Segoe UI", 16, "bold"), text_color="#cdd6f4")
        self.title_label.pack(pady=20)

        total = focus + fun + idle
        if total == 0:
            self.no_data = ctk.CTkLabel(self, text="Henüz istatistik verisi birikmedi.\nBiraz çalıştıktan sonra tekrar açın.", font=("Segoe UI", 13), text_color="#a6e3a1")
            self.no_data.pack(pady=80)
            return

        p_focus = focus / total
        p_fun = fun / total
        p_idle = idle / total

        def create_bar(label_text, percentage, color):
            frame = ctk.CTkFrame(self, fg_color="transparent")
            frame.pack(fill="x", padx=30, pady=10)
            
            lbl = ctk.CTkLabel(frame, text=f"{label_text} (%{int(percentage*100)}):", font=("Segoe UI", 12, "bold"), width=120, anchor="w", text_color="#cdd6f4")
            lbl.pack(side="left")
            
            progress = ctk.CTkProgressBar(frame, width=200, height=15, progress_color=color, fg_color="#313244")
            progress.pack(side="left", padx=10)
            progress.set(percentage)

        create_bar("🟢 Odaklanma", p_focus, "#a6e3a1")
        create_bar("🟡 Eğlence/Mola", p_fun, "#f9e2af")
        create_bar("🔴 Hareketsizlik", p_idle, "#f38ba8")


class FlowSafeApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        import ctypes
        try:
            myappid = 'flowsafe.premium.asistan.1'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except: pass
            
        self.withdraw() 
        self.title("Flow-Safe Premium")
        
        try: self.iconbitmap("logo.ico")
        except: pass
        
        self.attributes('-topmost', True)

        # Standart ve Mini Mod Boyutları
        self.normal_width, self.normal_height = 450, 470
        self.mini_width, self.mini_height = 200, 80
        self.is_mini_mode = False  # Başlangıçta tam modda açılır

        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()
        
        # Konumlandırma fonksiyonunu çağır
        self.adjust_window_position()

        self.db_file = "flow_safe_data.json"
        self.load_statistics()

        self.activity_score = 0
        self.total_focus_time = 0
        self.is_user_active = False
        self.running = True
        self.tray_icon = None 

        self.splash = SplashScreen(self)

        # --- MOD DEĞİŞTİRME BUTONU (Üst Bölüm) ---
        self.mode_btn = ctk.CTkButton(self, text="⇄ Mini Sayaç Modu", font=("Segoe UI", 11, "bold"),
                                       fg_color="#313244", hover_color="#45475a", text_color="#a6e3a1", 
                                       height=26, width=120, command=self.toggle_mode)
        self.mode_btn.pack(pady=(10, 0))

        # Ana Tasarım Kartı
        self.card_frame = ctk.CTkFrame(self, fg_color="#252538", corner_radius=15)
        self.card_frame.pack(pady=(10, 10), padx=20, fill="both", expand=True)

        self.status_label = ctk.CTkLabel(self.card_frame, text="Durum: Analiz Ediliyor...", font=("Segoe UI", 15, "bold"), text_color="#f9e2af")
        self.status_label.pack(pady=(10, 2))

        self.time_label = ctk.CTkLabel(self.card_frame, text="00:00:00", font=("Segoe UI", 44, "bold"), text_color="#cdd6f4")
        self.time_label.pack(pady=2)

        # Alt Bölüm Elemanları (Kompakt modda gizlenecekler)
        self.dnd_var = ctk.StringVar(value="off")
        self.dnd_switch = ctk.CTkSwitch(self, text="Akıllı Rahatsız Etme Modu (Oyun/Film Algılama)", 
                                        font=("Segoe UI", 12), variable=self.dnd_var, onvalue="on", offvalue="off", progress_color="#a6e3a1")
        self.dnd_switch.pack(pady=5)

        self.stats_btn = ctk.CTkButton(self, text="📊 Günlük İstatistik Raporu", font=("Segoe UI", 13, "bold"),
                                       fg_color="#313244", hover_color="#45475a", text_color="#cdd6f4", command=self.open_stats)
        self.stats_btn.pack(pady=5)

        self.info_label = ctk.CTkLabel(self, text="Uygulama üzerindeki hareketleriniz takip ediliyor.", font=("Segoe UI", 12), text_color="#bac2de")
        self.info_label.pack(pady=5)

        self.privacy_badge = ctk.CTkLabel(self, text="🔒 %100 İZİNSİZ VE GÜVENLİ MİMARİ", font=("Segoe UI", 10, "bold"), text_color="#6c7086")
        self.privacy_badge.pack(pady=(0, 10))

        self.bind_all("<Any-KeyPress>", self.on_activity)
        self.bind_all("<Motion>", self.on_activity)
        self.bind_all("<Button-1>", self.on_activity)

        self.tracking_thread = threading.Thread(target=self.core_loop, daemon=True)
        self.tracking_thread.start()

        self.protocol("WM_DELETE_WINDOW", self.hide_to_tray)

    def adjust_window_position(self):
        """Pencerenin o anki modunun boyutuna göre sağ alt köşeye yerleşmesini sağlar."""
        if self.is_mini_mode:
            w, h = self.mini_width, self.mini_height
        else:
            w, h = self.normal_width, self.normal_height
            
        x = self.screen_width - w - 20
        y = self.screen_height - h - 60 
        self.geometry(f"{w}x{h}+{x}+{y}")

    # --- YENİ ELEMAN: MİNİ/TAM MOD GEÇİŞ MOTORU ---
    def toggle_mode(self):
        if not self.is_mini_mode:
            # Mini Sayaç Moduna Geçiş
            self.is_mini_mode = True
            self.mode_btn.configure(text="⇄ Tam Mod")
            
            # Ana ekrandaki diğer elemanları gizle, sadece sayacı bırak
            self.status_label.pack_forget()
            self.dnd_switch.pack_forget()
            self.stats_btn.pack_forget()
            self.info_label.pack_forget()
            self.privacy_badge.pack_forget()
            
            # Kart yapısının boşluklarını daralt
            self.card_frame.pack_configure(pady=5, padx=5)
            self.time_label.configure(font=("Segoe UI", 28, "bold"))
            
            # Pencereyi küçült ve sağ alta sabitle
            self.adjust_window_position()
        else:
            # Tam Moda Geri Dönüş
            self.is_mini_mode = False
            self.mode_btn.configure(text="⇄ Mini Sayaç Modu")
            
            # Tüm elemanları eski yerleşim düzenine göre geri getir
            self.card_frame.pack_forget()
            self.time_label.pack_forget()
            
            # Yeniden inşa et
            self.card_frame.pack(pady=(10, 10), padx=20, fill="both", expand=True)
            self.status_label.pack(pady=(10, 2))
            self.time_label.pack(pady=2)
            self.time_label.configure(font=("Segoe UI", 44, "bold"))
            
            self.dnd_switch.pack(pady=5)
            self.stats_btn.pack(pady=5)
            self.info_label.pack(pady=5)
            self.privacy_badge.pack(pady=(0, 10))
            
            # Pencereyi eski büyük boyutuna getir ve konumlandır
            self.adjust_window_position()

    def on_activity(self, event=None):
        if self.running:
            self.activity_score += 1
            self.is_user_active = True

    def open_stats(self):
        StatsWindow(self, self.stat_focus_time, self.stat_fun_time, self.stat_idle_time)

    def load_statistics(self):
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, "r") as f:
                    data = json.load(f)
                    self.stat_focus_time = data.get("focus", 0)
                    self.stat_fun_time = data.get("fun", 0)
                    self.stat_idle_time = data.get("idle", 0)
            except:
                self.stat_focus_time = 0
                self.stat_fun_time = 0
                self.stat_idle_time = 0
        else:
            self.stat_focus_time = 0
            self.stat_fun_time = 0
            self.stat_idle_time = 0

    def save_statistics(self):
        try:
            data = {
                "focus": self.stat_focus_time,
                "fun": self.stat_fun_time,
                "idle": self.stat_idle_time
            }
            with open(self.db_file, "w") as f:
                json.dump(data, f)
        except:
            pass

    def core_loop(self):
        inactivity_counter = 0
        work_keywords = ["code", "visual studio", "word", "excel", "pdf", "notepad", "not defteri", "python", "studio", "flow-safe"]
        save_counter = 0

        while self.running:
            time.sleep(1)
            if not self.running: break
            
            try: active_window_title = gw.getActiveWindow().title.lower()
            except: active_window_title = ""

            is_working_app = any(keyword in active_window_title for keyword in work_keywords)

            if self.activity_score == 0:
                inactivity_counter += 1
            else:
                inactivity_counter = 0
                self.activity_score = 0

            if inactivity_counter >= 10:
                self.is_user_active = False
                self.stat_idle_time += 1
                try: self.status_label.configure(text="Durum: Masada Kimse Yok 💤", text_color="#f38ba8")
                except: pass
            
            elif self.dnd_var.get() == "on" and not is_working_app and active_window_title != "":
                self.is_user_active = True
                self.stat_fun_time += 1
                try: self.status_label.configure(text="Durum: Eğlence Modu (Sayaç Durduruldu) 🎮", text_color="#f9e2af")
                except: pass
            
            else:
                self.is_user_active = True
                self.stat_focus_time += 1
                try:
                    self.status_label.configure(text="Durum: Odaklanıldı 🚀", text_color="#a6e3a1")
                    self.total_focus_time += 1
                    self.update_time_display()
                except: pass

            save_counter += 1
            if save_counter >= 60:
                self.save_statistics()
                save_counter = 0

            if self.total_focus_time >= 2700:
                self.after(0, self.trigger_break_dialog)

    def update_time_display(self):
        hours = self.total_focus_time // 3600
        minutes = (self.total_focus_time % 3600) // 60
        seconds = self.total_focus_time % 60
        try: self.time_label.configure(text=f"{hours:02d}:{minutes:02d}:{seconds:02d}")
        except: pass

    def trigger_break_dialog(self):
        if self.running:
            self.total_focus_time = 0
            self.update_time_display()
            self.save_statistics() 
            CustomBreakDialog(self)

    def create_tray_icon(self):
        image = Image.new('RGB', (64, 64), color="#1e1e2e")
        dc = ImageDraw.Draw(image)
        dc.rectangle((16, 16, 48, 48), fill="#a6e3a1")
        return image

    def hide_to_tray(self):
        self.save_statistics() 
        self.withdraw()
        
        def start_tray():
            menu = pystray.Menu(
                pystray.MenuItem("Göster", self.show_from_tray),
                pystray.MenuItem("Tamamen Çıkış", self.safe_exit)
            )
            try: icon_img = Image.open("logo.ico")
            except: icon_img = self.create_tray_icon()
            
            self.tray_icon = pystray.Icon("FlowSafe", icon_img, "Flow-Safe Premium", menu)
            self.tray_icon.run()

        threading.Thread(target=start_tray, daemon=True).start()

    def show_from_tray(self, icon=None, item=None):
        if self.tray_icon:
            self.tray_icon.stop()
            self.tray_icon = None
        self.after(100, self.deiconify)
        self.after(100, self.update)

    def safe_exit(self, icon=None, item=None):
        self.running = False
        self.save_statistics() 
        if self.tray_icon: 
            self.tray_icon.stop()
        try: self.destroy()
        except: pass
        sys.exit(0)

if __name__ == "__main__":
    app = FlowSafeApp()
    try: app.mainloop()
    except KeyboardInterrupt: app.safe_exit()