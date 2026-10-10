import subprocess
import sys
import os
import json
import threading
import glob
import customtkinter as ctk
import minecraft_launcher_lib

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("dark-blue")

CONFIG_FILE = "config.json"

def detect_java_versions():
    java_paths = {}
    search_pattern = "/Library/Java/JavaVirtualMachines/*/Contents/Home/bin/java"
    for java_path in glob.glob(search_pattern):
        try:
            folder_name = java_path.split("/")[-5]
            display_name = folder_name.replace(".jdk", "").replace("-", " ").title()
            java_paths[display_name] = java_path
        except Exception:
            pass
            
    if not java_paths:
        java_paths["Varsayılan Sistem Java"] = "java"
        
    return java_paths

class MinecraftLauncher(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("dpLauncher")
        self.geometry("820x520")
        self.minsize(750, 480)

        self.show_snapshots = True
        self.show_betas = False
        self.custom_java = ""
        self.saved_username = ""
        self.all_versions = []

        self.load_config()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SOL MENÜ ---
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color=("#f0f0f0", "#18191a"))
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="dpLauncher", font=("Arial", 16, "bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 20))

        self.launch_button = ctk.CTkButton(
            self.sidebar_frame, 
            text="Oyunu Başlat", 
            command=self.start_launch_thread, 
            width=180, 
            height=40,
            fg_color="#ffd426",
            hover_color="#e6be1f",
            text_color="#111111",
            font=("Arial", 13, "bold"),
            corner_radius=8
        )
        self.launch_button.grid(row=1, column=0, padx=20, pady=10)

        self.btn_home = ctk.CTkButton(
            self.sidebar_frame, 
            text="Ana Ekran", 
            command=self.show_main_screen, 
            width=180, 
            height=35, 
            fg_color=("#e4e4e7", "#2f3136"),
            hover_color=("#d4d4d8", "#3f4248"),
            text_color=("#111111", "#ffffff"),
            font=("Arial", 12, "bold"),
            corner_radius=8
        )
        self.btn_home.grid(row=2, column=0, padx=20, pady=5)

        self.folder_button = ctk.CTkButton(
            self.sidebar_frame, 
            text="Sürüm Klasörü", 
            command=self.open_version_folder, 
            width=180, 
            height=35, 
            fg_color=("#e4e4e7", "#2f3136"), 
            hover_color=("#d4d4d8", "#3f4248"),
            text_color=("#111111", "#ffffff"),
            corner_radius=8
        )
        self.folder_button.grid(row=3, column=0, padx=20, pady=5)

        self.settings_button = ctk.CTkButton(
            self.sidebar_frame, 
            text="Ayarlar", 
            command=self.show_settings_screen, 
            width=180, 
            height=35, 
            fg_color=("#e4e4e7", "#2f3136"), 
            hover_color=("#d4d4d8", "#3f4248"),
            text_color=("#111111", "#ffffff"),
            corner_radius=8
        )
        self.settings_button.grid(row=4, column=0, padx=20, pady=5)

        # --- SAĞ İÇERİK ALANI ---
        self.content_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=("#ffffff", "#202225"))
        self.content_frame.grid(row=0, column=1, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)

        # 1. ANA EKRAN
        self.main_screen_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.main_screen_frame.grid(row=0, column=0, sticky="nsew")
        self.main_screen_frame.grid_columnconfigure(0, weight=1)

        self.label = ctk.CTkLabel(self.main_screen_frame, text="Profil & Sürüm Yönetimi", font=("Arial", 20, "bold"))
        self.label.grid(row=0, column=0, padx=30, pady=(30, 15), sticky="w")

        BOX_WIDTH = 300

        self.card_user = ctk.CTkFrame(self.main_screen_frame, fg_color=("#e4e4e7", "#2f3136"), corner_radius=12, height=75)
        self.card_user.grid(row=1, column=0, padx=30, pady=8, sticky="ew")
        ctk.CTkLabel(self.card_user, text="Kullanıcı Adı:", font=("Arial", 12, "bold")).place(x=20, y=25)
        self.username_entry = ctk.CTkEntry(self.card_user, placeholder_text="Kullanıcı Adı Girin", width=BOX_WIDTH, height=35, fg_color=("#ffffff", "#40444b"), border_color="#ffd426", corner_radius=8)
        self.username_entry.place(relx=1.0, x=-20, y=20, anchor="ne")
        if self.saved_username:
            self.username_entry.insert(0, self.saved_username)

        self.card_loader = ctk.CTkFrame(self.main_screen_frame, fg_color=("#e4e4e7", "#2f3136"), corner_radius=12, height=75)
        self.card_loader.grid(row=2, column=0, padx=30, pady=8, sticky="ew")
        ctk.CTkLabel(self.card_loader, text="Mod Loader:", font=("Arial", 12, "bold")).place(x=20, y=25)
        self.loader_menu = ctk.CTkOptionMenu(self.card_loader, values=["Vanilla (Saf)", "Fabric", "Forge"], width=BOX_WIDTH, height=35, fg_color="#ffd426", button_color="#e6be1f", button_hover_color="#d4aa12", text_color="#111111", corner_radius=8)
        self.loader_menu.place(relx=1.0, x=-20, y=20, anchor="ne")

        self.card_version = ctk.CTkFrame(self.main_screen_frame, fg_color=("#e4e4e7", "#2f3136"), corner_radius=12, height=75)
        self.card_version.grid(row=3, column=0, padx=30, pady=8, sticky="ew")
        ctk.CTkLabel(self.card_version, text="Oyun Sürümü:", font=("Arial", 12, "bold")).place(x=20, y=25)
        self.version_menu = ctk.CTkOptionMenu(self.card_version, values=["Yükleniyor..."], width=BOX_WIDTH, height=35, fg_color="#ffd426", button_color="#e6be1f", button_hover_color="#d4aa12", text_color="#111111", corner_radius=8)
        self.version_menu.place(relx=1.0, x=-20, y=20, anchor="ne")

        self.status_label = ctk.CTkLabel(self.main_screen_frame, text="Sürümler internetten yükleniyor...", font=("Arial", 11), text_color="#888888")
        self.status_label.grid(row=4, column=0, padx=30, pady=(15, 30), sticky="w")

        # 2. AYARLAR EKRANI
        self.settings_screen_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.settings_screen_frame.grid(row=0, column=0, sticky="nsew")
        self.settings_screen_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.settings_screen_frame, text="Gelişmiş Ayarlar", font=("Arial", 20, "bold")).grid(row=0, column=0, padx=30, pady=(30, 20), sticky="w")

        self.snapshot_switch = ctk.CTkSwitch(self.settings_screen_frame, text="Snapshot Sürümünü Göster", progress_color="#ffd426")
        if self.show_snapshots:
            self.snapshot_switch.select()
        self.snapshot_switch.grid(row=1, column=0, padx=30, pady=10, sticky="w")

        self.beta_switch = ctk.CTkSwitch(self.settings_screen_frame, text="Alpha / Beta Sürümünü Göster", progress_color="#ffd426")
        if self.show_betas:
            self.beta_switch.select()
        self.beta_switch.grid(row=2, column=0, padx=30, pady=10, sticky="w")

        ctk.CTkLabel(self.settings_screen_frame, text="Java Sürümü Seçin:", font=("Arial", 12, "bold")).grid(row=3, column=0, padx=30, pady=(20, 5), sticky="w")
        
        self.java_dict = detect_java_versions()
        java_names = list(self.java_dict.keys())
        
        current_java_name = java_names[0]
        for name, path in self.java_dict.items():
            if path == self.custom_java:
                current_java_name = name
                break

        self.java_menu = ctk.CTkOptionMenu(self.settings_screen_frame, values=java_names, width=BOX_WIDTH, height=35, fg_color="#ffd426", button_color="#e6be1f", button_hover_color="#d4aa12", text_color="#111111")
        self.java_menu.set(current_java_name)
        self.java_menu.grid(row=4, column=0, padx=30, pady=5, sticky="w")

        self.save_settings_btn = ctk.CTkButton(
            self.settings_screen_frame, 
            text="Kaydet ve Listeyi Yenile", 
            command=self.apply_and_close_settings, 
            fg_color="#ffd426", 
            hover_color="#e6be1f", 
            text_color="#111111", 
            font=("Arial", 12, "bold"), 
            width=BOX_WIDTH, 
            height=38, 
            corner_radius=8
        )
        self.save_settings_btn.grid(row=5, column=0, padx=30, pady=25, sticky="w")

        self.show_main_screen()
        threading.Thread(target=self.load_versions, daemon=True).start()

    def show_main_screen(self):
        self.settings_screen_frame.grid_remove()
        self.main_screen_frame.grid()

    def show_settings_screen(self):
        self.main_screen_frame.grid_remove()
        self.settings_screen_frame.grid()

    def apply_and_close_settings(self):
        self.show_snapshots = True if self.snapshot_switch.get() == 1 else False
        self.show_betas = True if self.beta_switch.get() == 1 else False
        
        selected_java_name = self.java_menu.get()
        self.custom_java = self.java_dict.get(selected_java_name, "java")
        
        self.save_config()
        threading.Thread(target=self.load_versions, daemon=True).start()
        self.show_main_screen()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.saved_username = data.get("username", "")
                    self.show_snapshots = data.get("show_snapshots", True)
                    self.show_betas = data.get("show_betas", False)
                    self.custom_java = data.get("custom_java", "")
            except Exception as e:
                print("Config okunamadı:", e)

    def save_config(self):
        data = {
            "username": self.username_entry.get().strip(),
            "show_snapshots": self.show_snapshots,
            "show_betas": self.show_betas,
            "custom_java": self.custom_java
        }
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print("Config kaydedilemedi:", e)

    def open_version_folder(self):
        version = self.version_menu.get()
        loader = self.loader_menu.get()
        
        if version in ["Yükleniyor...", "Seçime uygun sürüm yok", ""]:
            self.status_label.configure(text="Önce geçerli bir sürüm seçin!")
            return

        profile_name = f"{version}_{loader.lower().split()[0]}"
        profiles_dir = os.path.expanduser("~/Library/Application Support/minecraft_profiles")
        version_dir = os.path.join(profiles_dir, profile_name)
        
        os.makedirs(os.path.join(version_dir, "mods"), exist_ok=True)
        os.makedirs(os.path.join(version_dir, "resourcepacks"), exist_ok=True)
        
        subprocess.run(["open", version_dir])
        self.status_label.configure(text=f"{profile_name} klasörü açıldı.")

    def load_versions(self):
        try:
            self.status_label.configure(text="Sürümler filtreleniyor...")
            versions = minecraft_launcher_lib.utils.get_version_list()
            self.all_versions = versions
            self.filter_and_update_menu()
        except Exception as e:
            self.status_label.configure(text="Sürümler yüklenemedi!")
            print(e)

    def filter_and_update_menu(self):
        filtered_ids = []
        for v in self.all_versions:
            v_type = v.get("type")
            if v_type == "snapshot" and not self.show_snapshots:
                continue
            if (v_type == "old_alpha" or v_type == "old_beta") and not self.show_betas:
                continue
            filtered_ids.append(v["id"])

        if filtered_ids:
            self.version_menu.configure(values=filtered_ids)
            self.version_menu.set(filtered_ids[0])
            self.status_label.configure(text="Hazır!")
        else:
            self.version_menu.configure(values=["Seçime uygun sürüm yok"])
            self.status_label.configure(text="Filtreye uygun sürüm bulunamadı.")

    def start_launch_thread(self):
        threading.Thread(target=self.launch_game, daemon=True).start()

    def launch_game(self):
        username = self.username_entry.get().strip()
        version = self.version_menu.get()
        loader = self.loader_menu.get()

        if not username:
            self.status_label.configure(text="Lütfen bir kullanıcı adı girin!")
            return

        if version in ["Yükleniyor...", "Seçime uygun sürüm yok", ""]:
            self.status_label.configure(text="Geçerli bir sürüm seçin!")
            return

        self.save_config()

        self.launch_button.configure(state="disabled")
        self.status_label.configure(text="Minecraft ana dizini kontrol ediliyor...")

        minecraft_directory = os.path.expanduser("~/Library/Application Support/minecraft")

        profile_name = f"{version}_{loader.lower().split()[0]}"
        custom_game_directory = os.path.expanduser(f"~/Library/Application Support/minecraft_profiles/{profile_name}")
        os.makedirs(os.path.join(custom_game_directory, "mods"), exist_ok=True)

        try:
            target_version = version
            if loader == "Fabric":
                self.status_label.configure(text=f"Fabric ({version}) kuruluyor...")
                try:
                    minecraft_launcher_lib.fabric.install_fabric(version, minecraft_directory)
                    installed_versions = minecraft_launcher_lib.utils.get_installed_versions(minecraft_directory)
                    target_version = next((v["id"] for v in installed_versions if f"fabric-loader" in v["id"] and version in v["id"]), version)
                except Exception as fe:
                    print("Fabric kurulamadı:", fe)
            elif loader == "Forge":
                self.status_label.configure(text=f"Forge ({version}) kuruluyor...")
                try:
                    minecraft_launcher_lib.forge.install_forge_version(version, minecraft_directory)
                except Exception as foe:
                    print("Forge kurulamadı:", foe)

            version_path = os.path.join(minecraft_directory, "versions", target_version)
            if not os.path.exists(version_path):
                self.status_label.configure(text=f"{target_version} indiriliyor, lütfen bekleyin...")
                minecraft_launcher_lib.install.install_minecraft_version(target_version, minecraft_directory)
            
            self.status_label.configure(text="Oyun başlatılıyor...")

            options = {
                "username": username,
                "uuid": "11111111-1111-1111-1111-111111111111",
                "token": "",
                "jvmArguments": ["-XstartOnFirstThread"],
                "gameDirectory": custom_game_directory
            }

            if self.custom_java:
                options["executablePath"] = self.custom_java

            minecraft_command = minecraft_launcher_lib.command.get_minecraft_command(target_version, minecraft_directory, options)
            
            # --- KRİTİK FİLTRE: Hatalı sınıf yükleyici argümanını komut listesinden tamamen temizle ---
            cleaned_command = []
            skip_next = False
            for arg in minecraft_command:
                if skip_next:
                    skip_next = False
                    continue
                if "-Djava.system.class.loader=" in arg:
                    continue
                if arg == "-Djava.system.class.loader":
                    skip_next = True
                    continue
                cleaned_command.append(arg)
            minecraft_command = cleaned_command

            self.status_label.configure(text="İyi oyunlar!")
            subprocess.call(minecraft_command)

        except Exception as e:
            self.status_label.configure(text=f"Hata oluştu: {str(e)}")
            print(e)
        
        finally:
            self.launch_button.configure(state="normal")

if __name__ == "__main__":
    app = MinecraftLauncher()
    app.mainloop()
