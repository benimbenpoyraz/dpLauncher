import subprocess
import sys
import os
import json
import threading
import glob
import urllib.request
import urllib.parse
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
        self.title("dpLauncher v4")
        self.geometry("920x600")
        self.minsize(840, 540)

        self.show_snapshots = True
        self.show_betas = False
        self.custom_java = ""
        self.saved_username = ""
        self.all_versions = []
        self.profiles = {"Varsayılan Profil": {"version": "1.20.4", "loader": "Vanilla (Saf)"}}
        self.current_resource_type = "resourcepack" # 'resourcepack' veya 'shader'

        self.load_config()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SOL MENÜ ---
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color=("#f0f0f0", "#18191a"))
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(8, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="dpLauncher v4", font=("Arial", 16, "bold"))
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

        self.btn_mods = ctk.CTkButton(
            self.sidebar_frame, 
            text="Modlar", 
            command=self.show_mods_screen, 
            width=180, 
            height=35, 
            fg_color=("#e4e4e7", "#2f3136"),
            hover_color=("#d4d4d8", "#3f4248"),
            text_color=("#111111", "#ffffff"),
            font=("Arial", 12, "bold"),
            corner_radius=8
        )
        self.btn_mods.grid(row=3, column=0, padx=20, pady=5)

        self.btn_resources = ctk.CTkButton(
            self.sidebar_frame, 
            text="Kaynaklar", 
            command=self.show_resources_screen, 
            width=180, 
            height=35, 
            fg_color=("#e4e4e7", "#2f3136"),
            hover_color=("#d4d4d8", "#3f4248"),
            text_color=("#111111", "#ffffff"),
            font=("Arial", 12, "bold"),
            corner_radius=8
        )
        self.btn_resources.grid(row=4, column=0, padx=20, pady=5)

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
        self.folder_button.grid(row=5, column=0, padx=20, pady=5)

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
        self.settings_button.grid(row=6, column=0, padx=20, pady=5)

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

        self.card_version = ctk.CTkFrame(self.main_screen_frame, fg_color=("#e4e4e7", "#2f3136"), corner_radius=12, height=75)
        self.card_version.grid(row=2, column=0, padx=30, pady=8, sticky="ew")
        ctk.CTkLabel(self.card_version, text="Profil / Sürüm Seç:", font=("Arial", 12, "bold")).place(x=20, y=25)
        
        display_list = ["+ Yeni Sürüm Oluştur"] + [f"{name} ({info['version']} - {info['loader']})" for name, info in self.profiles.items()]
        self.version_menu = ctk.CTkOptionMenu(self.card_version, values=display_list, width=BOX_WIDTH, height=35, fg_color="#ffd426", button_color="#e6be1f", button_hover_color="#d4aa12", text_color="#111111", corner_radius=8, command=self.on_profile_or_new_selected)
        self.version_menu.place(relx=1.0, x=-20, y=20, anchor="ne")

        self.status_label = ctk.CTkLabel(self.main_screen_frame, text="Sürümler internetten yükleniyor...", font=("Arial", 11), text_color="#888888")
        self.status_label.grid(row=3, column=0, padx=30, pady=(15, 30), sticky="w")

        # 2. MODLAR EKRANI
        self.mods_screen_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.mods_screen_frame.grid(row=0, column=0, sticky="nsew")
        self.mods_screen_frame.grid_columnconfigure(0, weight=1)

        self.mods_top_frame = ctk.CTkFrame(self.mods_screen_frame, fg_color="transparent")
        self.mods_top_frame.grid(row=0, column=0, padx=30, pady=(30, 10), sticky="ew")
        self.mods_top_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.mods_top_frame, text="Modrinth Mod Merkezi", font=("Arial", 20, "bold")).grid(row=0, column=0, sticky="w")
        
        profile_names = list(self.profiles.keys())
        self.mods_profile_menu = ctk.CTkOptionMenu(self.mods_top_frame, values=profile_names, width=220, height=30, fg_color="#ffd426", button_color="#e6be1f", button_hover_color="#d4aa12", text_color="#111111")
        self.mods_profile_menu.grid(row=0, column=1, sticky="e")

        self.mod_search_entry = ctk.CTkEntry(self.mods_screen_frame, placeholder_text="Mod adı arayın (örn: sodium, JEI)...", width=350, height=35, fg_color=("#ffffff", "#40444b"), border_color="#ffd426", corner_radius=8)
        self.mod_search_entry.grid(row=1, column=0, padx=30, pady=5, sticky="w")

        self.search_mod_btn = ctk.CTkButton(
            self.mods_screen_frame, 
            text="Mod Ara", 
            command=lambda: threading.Thread(target=self.search_mods, daemon=True).start(), 
            fg_color="#ffd426", 
            hover_color="#e6be1f", 
            text_color="#111111", 
            font=("Arial", 12, "bold"), 
            width=120, 
            height=35, 
            corner_radius=8
        )
        self.search_mod_btn.grid(row=1, column=0, padx=(390, 30), pady=5, sticky="w")

        self.mod_results_frame = ctk.CTkScrollableFrame(self.mods_screen_frame, width=540, height=320, fg_color=("#e4e4e7", "#2f3136"), corner_radius=12)
        self.mod_results_frame.grid(row=2, column=0, padx=30, pady=15, sticky="w")

        self.mod_status_label = ctk.CTkLabel(self.mods_screen_frame, text="Aramak istediğiniz modu yazın ve arayın.", font=("Arial", 11), text_color="#888888")
        self.mod_status_label.grid(row=3, column=0, padx=30, pady=(0, 20), sticky="w")

        # 3. KAYNAKLAR EKRANI (Yeni Eklenen Bölme)
        self.resources_screen_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.resources_screen_frame.grid(row=0, column=0, sticky="nsew")
        self.resources_screen_frame.grid_columnconfigure(0, weight=1)

        self.res_top_frame = ctk.CTkFrame(self.resources_screen_frame, fg_color="transparent")
        self.res_top_frame.grid(row=0, column=0, padx=30, pady=(30, 10), sticky="ew")
        self.res_top_frame.grid_columnconfigure(2, weight=1)

        ctk.CTkLabel(self.res_top_frame, text="Kaynak & Gölgelendirici Merkezi", font=("Arial", 20, "bold")).grid(row=0, column=0, sticky="w")
        
        # Kaynak Paketi / Gölgelendirici değiştirme butonları
        self.btn_res_pack = ctk.CTkButton(self.res_top_frame, text="Kaynak Paketi", command=lambda: self.switch_resource_type("resourcepack"), width=120, height=30, fg_color="#ffd426", text_color="#111111", font=("Arial", 11, "bold"))
        self.btn_res_pack.grid(row=0, column=1, padx=(20, 10), sticky="w")

        self.btn_shader = ctk.CTkButton(self.res_top_frame, text="Gölgelendirici (Shader)", command=lambda: self.switch_resource_type("shader"), width=150, height=30, fg_color=("#e4e4e7", "#2f3136"), text_color=("#111111", "#ffffff"), font=("Arial", 11, "bold"))
        self.btn_shader.grid(row=0, column=2, padx=5, sticky="w")

        # Kaynaklar ekranı profil seçicisi (sağ üst)
        self.res_profile_menu = ctk.CTkOptionMenu(self.res_top_frame, values=profile_names, width=180, height=30, fg_color="#ffd426", button_color="#e6be1f", button_hover_color="#d4aa12", text_color="#111111")
        self.res_profile_menu.grid(row=0, column=3, sticky="e")

        self.res_search_entry = ctk.CTkEntry(self.resources_screen_frame, placeholder_text="Kaynak veya Shader ara (örn: faithful, complementary)...", width=350, height=35, fg_color=("#ffffff", "#40444b"), border_color="#ffd426", corner_radius=8)
        self.res_search_entry.grid(row=1, column=0, padx=30, pady=5, sticky="w")

        self.search_res_btn = ctk.CTkButton(
            self.resources_screen_frame, 
            text="Ara", 
            command=lambda: threading.Thread(target=self.search_resources, daemon=True).start(), 
            fg_color="#ffd426", 
            hover_color="#e6be1f", 
            text_color="#111111", 
            font=("Arial", 12, "bold"), 
            width=120, 
            height=35, 
            corner_radius=8
        )
        self.search_res_btn.grid(row=1, column=0, padx=(390, 30), pady=5, sticky="w")

        self.res_results_frame = ctk.CTkScrollableFrame(self.resources_screen_frame, width=540, height=320, fg_color=("#e4e4e7", "#2f3136"), corner_radius=12)
        self.res_results_frame.grid(row=2, column=0, padx=30, pady=15, sticky="w")

        self.res_status_label = ctk.CTkLabel(self.resources_screen_frame, text="Paket türünü seçin ve arama yapın.", font=("Arial", 11), text_color="#888888")
        self.res_status_label.grid(row=3, column=0, padx=30, pady=(0, 20), sticky="w")

        # 4. AYARLAR EKRANI
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
        self.mods_screen_frame.grid_remove()
        self.resources_screen_frame.grid_remove()
        self.settings_screen_frame.grid_remove()
        self.main_screen_frame.grid()

    def show_mods_screen(self):
        self.main_screen_frame.grid_remove()
        self.resources_screen_frame.grid_remove()
        self.settings_screen_frame.grid_remove()
        self.mods_screen_frame.grid()

    def show_resources_screen(self):
        self.main_screen_frame.grid_remove()
        self.mods_screen_frame.grid_remove()
        self.settings_screen_frame.grid_remove()
        self.resources_screen_frame.grid()

    def show_settings_screen(self):
        self.main_screen_frame.grid_remove()
        self.mods_screen_frame.grid_remove()
        self.resources_screen_frame.grid_remove()
        self.settings_screen_frame.grid()

    def switch_resource_type(self, r_type):
        self.current_resource_type = r_type
        if r_type == "resourcepack":
            self.btn_res_pack.configure(fg_color="#ffd426", text_color="#111111")
            self.btn_shader.configure(fg_color=("#e4e4e7", "#2f3136"), text_color=("#111111", "#ffffff"))
            self.res_search_entry.configure(placeholder_text="Kaynak paketi ara (örn: faithful, default dark)...")
        else:
            self.btn_shader.configure(fg_color="#ffd426", text_color="#111111")
            self.btn_res_pack.configure(fg_color=("#e4e4e7", "#2f3136"), text_color=("#111111", "#ffffff"))
            self.res_search_entry.configure(placeholder_text="Shader / Gölgelendirici ara (örn: complementary, bsl)...")

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
                    loaded_profiles = data.get("profiles", None)
                    if isinstance(loaded_profiles, dict):
                        self.profiles = loaded_profiles
                    elif isinstance(loaded_profiles, list):
                        self.profiles = {p: {"version": "1.20.4", "loader": "Vanilla (Saf)"} for p in loaded_profiles}
            except Exception as e:
                print("Config okunamadı:", e)

    def save_config(self):
        data = {
            "username": self.username_entry.get().strip(),
            "show_snapshots": self.show_snapshots,
            "show_betas": self.show_betas,
            "custom_java": self.custom_java,
            "profiles": self.profiles
        }
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print("Config kaydedilemedi:", e)

    def open_version_folder(self):
        current_selection = self.version_menu.get()
        if current_selection in ["Yükleniyor...", "Seçime uygun sürüm yok", "+ Yeni Sürüm Oluştur", ""]:
            self.status_label.configure(text="Önce geçerli bir profil seçin!")
            return

        profile_name = current_selection.split(" (")[0]
        profiles_dir = os.path.expanduser("~/Library/Application Support/minecraft_profiles")
        version_dir = os.path.join(profiles_dir, profile_name)
        
        os.makedirs(os.path.join(version_dir, "mods"), exist_ok=True)
        os.makedirs(os.path.join(version_dir, "resourcepacks"), exist_ok=True)
        os.makedirs(os.path.join(version_dir, "shaderpacks"), exist_ok=True)
        
        subprocess.run(["open", version_dir])
        self.status_label.configure(text=f"{profile_name} klasörü açıldı.")

    def load_versions(self):
        try:
            self.status_label.configure(text="Sürümler filtreleniyor...")
            versions = minecraft_launcher_lib.utils.get_version_list()
            self.all_versions = versions
            self.update_menus()
        except Exception as e:
            self.status_label.configure(text="Sürümler yüklenemedi!")
            print(e)

    def update_menus(self):
        if self.profiles:
            display_list = ["+ Yeni Sürüm Oluştur"] + [f"{name} ({info['version']} - {info['loader']})" for name, info in self.profiles.items()]
            self.version_menu.configure(values=display_list)
            self.version_menu.set(display_list[1])
            
            profile_names = list(self.profiles.keys())
            self.mods_profile_menu.configure(values=profile_names)
            self.mods_profile_menu.set(profile_names[0])
            self.res_profile_menu.configure(values=profile_names)
            self.res_profile_menu.set(profile_names[0])

            self.status_label.configure(text="Hazır!")
        else:
            self.version_menu.configure(values=["Seçime uygun sürüm yok"])

    def on_profile_or_new_selected(self, choice):
        if choice == "+ Yeni Sürüm Oluştur":
            self.open_new_profile_window()

    def open_new_profile_window(self):
        top = ctk.CTkToplevel(self)
        top.title("Yeni Profil Oluştur")
        top.geometry("380x320")
        top.resizable(False, False)
        top.grab_set()

        ctk.CTkLabel(top, text="Profil Adı:", font=("Arial", 12, "bold")).pack(padx=20, pady=(20, 5), anchor="w")
        name_entry = ctk.CTkEntry(top, width=340, height=35, fg_color=("#ffffff", "#40444b"), border_color="#ffd426", corner_radius=8)
        name_entry.pack(padx=20, pady=5)
        name_entry.insert(0, "Deneme1Nasılsın")

        ctk.CTkLabel(top, text="Oyun Sürümü:", font=("Arial", 12, "bold")).pack(padx=20, pady=(10, 5), anchor="w")
        filtered_ids = [v["id"] for v in self.all_versions] if self.all_versions else ["1.20.4"]
        version_menu = ctk.CTkOptionMenu(top, values=filtered_ids, width=340, height=35, fg_color="#ffd426", button_color="#e6be1f", button_hover_color="#d4aa12", text_color="#111111")
        version_menu.pack(padx=20, pady=5)

        ctk.CTkLabel(top, text="Mod Loader:", font=("Arial", 12, "bold")).pack(padx=20, pady=(10, 5), anchor="w")
        loader_menu = ctk.CTkOptionMenu(top, values=["Vanilla (Saf)", "Fabric", "Forge"], width=340, height=35, fg_color="#ffd426", button_color="#e6be1f", button_hover_color="#d4aa12", text_color="#111111")
        loader_menu.pack(padx=20, pady=5)

        def save_new_profile():
            p_name = name_entry.get().strip()
            p_ver = version_menu.get()
            p_loader = loader_menu.get()

            if not p_name:
                return

            self.profiles[p_name] = {"version": p_ver, "loader": p_loader}
            self.save_config()
            self.update_menus()
            
            target_str = f"{p_name} ({p_ver} - {p_loader})"
            self.version_menu.set(target_str)
            self.mods_profile_menu.set(p_name)
            self.res_profile_menu.set(p_name)
            
            self.status_label.configure(text=f"'{p_name}' profili başarıyla oluşturuldu!")
            top.destroy()

        save_btn = ctk.CTkButton(top, text="Profili Kaydet", command=save_new_profile, fg_color="#ffd426", hover_color="#e6be1f", text_color="#111111", font=("Arial", 12, "bold"), width=340, height=38, corner_radius=8)
        save_btn.pack(padx=20, pady=(20, 20))

    def search_mods(self):
        query = self.mod_search_entry.get().strip()
        if not query:
            self.mod_status_label.configure(text="Lütfen aranacak mod adını yazın.")
            return

        self.mod_status_label.configure(text="Modlar aranıyor...")
        for widget in self.mod_results_frame.winfo_children():
            widget.destroy()

        try:
            params = urllib.parse.urlencode({
                'query': query,
                'facets': '[["project_type:mod"]]'
            })
            url = f"https://api.modrinth.com/v2/search?{params}"
            
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'dpLauncher/4.0 (doruk@launcher.app)'}
            )
            
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                hits = data.get("hits", [])

            if not hits:
                self.mod_status_label.configure(text="Eşleşen mod bulunamadı.")
                return

            for mod in hits[:15]:
                name = mod.get("title", "İsimsiz Mod")
                desc = mod.get("description", "Açıklama yok.")
                project_id = mod.get("project_id")
                
                card = ctk.CTkFrame(self.mod_results_frame, fg_color=("#ffffff", "#40444b"), corner_radius=8)
                card.pack(fill="x", padx=5, pady=5)
                
                title_lbl = ctk.CTkLabel(card, text=name, font=("Arial", 12, "bold"), text_color=("#111111", "#ffffff"))
                title_lbl.pack(anchor="w", padx=10, pady=(8, 2))
                
                desc_lbl = ctk.CTkLabel(card, text=desc, font=("Arial", 10), text_color=("#666666", "#aaaaaa"), wraplength=450, justify="left")
                desc_lbl.pack(anchor="w", padx=10, pady=2)
                
                dl_btn = ctk.CTkButton(
                    card, 
                    text="Bu Profile İndir (+Bağımlılıklar)", 
                    command=lambda pid=project_id, mname=name: self.download_mod_with_dependencies(pid, mname), 
                    fg_color="#ffd426", 
                    hover_color="#e6be1f", 
                    text_color="#111111", 
                    font=("Arial", 10, "bold"), 
                    width=180, 
                    height=28, 
                    corner_radius=6
                )
                dl_btn.pack(anchor="e", padx=10, pady=(5, 8))

            self.mod_status_label.configure(text=f"{len(hits)} mod bulundu.")
        except Exception as e:
            self.mod_status_label.configure(text="Mod araması başarısız oldu.")
            print("Arama Hatası:", e)

    def download_mod_with_dependencies(self, project_id, mod_name):
        selected_profile = self.mods_profile_menu.get()
        profile_info = self.profiles.get(selected_profile, {"version": "1.20.4", "loader": "Vanilla (Saf)"})
        
        version = profile_info["version"]
        loader = profile_info["loader"].lower().split()[0]

        self.mod_status_label.configure(text=f"{mod_name} ve bağımlılıkları aranıyor/indiriliyor...")

        def _download_recursive(pid, m_name):
            try:
                versions_url = f"https://api.modrinth.com/v2/project/{pid}/version"
                req = urllib.request.Request(versions_url, headers={'User-Agent': 'dpLauncher/4.0 (doruk@launcher.app)'})
                with urllib.request.urlopen(req) as response:
                    versions_data = json.loads(response.read().decode())

                target_version_obj = None
                for v in versions_data:
                    game_versions = v.get("game_versions", [])
                    loaders = v.get("loaders", [])
                    if version in game_versions and (loader == "vanilla" or loader in loaders or not loaders):
                        target_version_obj = v
                        break
                
                if not target_version_obj and versions_data:
                    target_version_obj = versions_data[0]

                if not target_version_obj:
                    return

                files = target_version_obj.get("files", [])
                if not files:
                    return
                
                target_version_file = files[0].get("url")
                mods_dir = os.path.expanduser(f"~/Library/Application Support/minecraft_profiles/{selected_profile}/mods")
                os.makedirs(mods_dir, exist_ok=True)

                file_name = target_version_file.split("/")[-1]
                file_path = os.path.join(mods_dir, file_name)

                if not os.path.exists(file_path):
                    urllib.request.urlretrieve(target_version_file, file_path)

                dependencies = target_version_obj.get("dependencies", [])
                for dep in dependencies:
                    if dep.get("dependency_type") == "required":
                        dep_project_id = dep.get("project_id")
                        if dep_project_id:
                            try:
                                proj_url = f"https://api.modrinth.com/v2/project/{dep_project_id}"
                                preq = urllib.request.Request(proj_url, headers={'User-Agent': 'dpLauncher/4.0 (doruk@launcher.app)'})
                                with urllib.request.urlopen(preq) as presp:
                                    proj_data = json.loads(presp.read().decode())
                                    dep_name = proj_data.get("title", "Bağımlılık Mod")
                                _download_recursive(dep_project_id, dep_name)
                            except Exception as de:
                                print("Bağımlılık indirme hatası:", de)
            except Exception as e:
                print(f"{m_name} indirilemedi:", e)

        def _worker():
            _download_recursive(project_id, mod_name)
            self.mod_status_label.configure(text=f"{mod_name} ve tüm bağımlılıkları [{selected_profile}] profiline indirildi!")

        threading.Thread(target=_worker, daemon=True).start()

    def search_resources(self):
        query = self.res_search_entry.get().strip()
        if not query:
            self.res_status_label.configure(text="Lütfen aranacak paket adını yazın.")
            return

        self.res_status_label.configure(text="Paketler aranıyor...")
        for widget in self.res_results_frame.winfo_children():
            widget.destroy()

        try:
            # project_type olarak resourcepack veya shader arıyoruz
            facet_type = "resourcepack" if self.current_resource_type == "resourcepack" else "shader"
            params = urllib.parse.urlencode({
                'query': query,
                'facets': f'[["project_type:{facet_type}"]]'
            })
            url = f"https://api.modrinth.com/v2/search?{params}"
            
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'dpLauncher/4.0 (doruk@launcher.app)'}
            )
            
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                hits = data.get("hits", [])

            if not hits:
                self.res_status_label.configure(text="Eşleşen paket bulunamadı.")
                return

            for item in hits[:15]:
                name = item.get("title", "İsimsiz Paket")
                desc = item.get("description", "Açıklama yok.")
                project_id = item.get("project_id")
                
                card = ctk.CTkFrame(self.res_results_frame, fg_color=("#ffffff", "#40444b"), corner_radius=8)
                card.pack(fill="x", padx=5, pady=5)
                
                title_lbl = ctk.CTkLabel(card, text=name, font=("Arial", 12, "bold"), text_color=("#111111", "#ffffff"))
                title_lbl.pack(anchor="w", padx=10, pady=(8, 2))
                
                desc_lbl = ctk.CTkLabel(card, text=desc, font=("Arial", 10), text_color=("#666666", "#aaaaaa"), wraplength=450, justify="left")
                desc_lbl.pack(anchor="w", padx=10, pady=2)
                
                dl_btn = ctk.CTkButton(
                    card, 
                    text="Bu Profile İndir", 
                    command=lambda pid=project_id, mname=name: self.download_resource_file(pid, mname), 
                    fg_color="#ffd426", 
                    hover_color="#e6be1f", 
                    text_color="#111111", 
                    font=("Arial", 10, "bold"), 
                    width=130, 
                    height=28, 
                    corner_radius=6
                )
                dl_btn.pack(anchor="e", padx=10, pady=(5, 8))

            self.res_status_label.configure(text=f"{len(hits)} paket bulundu.")
        except Exception as e:
            self.res_status_label.configure(text="Arama başarısız oldu.")
            print("Kaynak Arama Hatası:", e)

    def download_resource_file(self, project_id, item_name):
        selected_profile = self.res_profile_menu.get()
        profile_info = self.profiles.get(selected_profile, {"version": "1.20.4", "loader": "Vanilla (Saf)"})
        version = profile_info["version"]
        
        target_folder = "resourcepacks" if self.current_resource_type == "resourcepack" else "shaderpacks"
        self.res_status_label.configure(text=f"{item_name} [{selected_profile}] profiline indiriliyor...")

        def _download():
            try:
                versions_url = f"https://api.modrinth.com/v2/project/{project_id}/version"
                req = urllib.request.Request(versions_url, headers={'User-Agent': 'dpLauncher/4.0 (doruk@launcher.app)'})
                with urllib.request.urlopen(req) as response:
                    versions_data = json.loads(response.read().decode())

                target_version_file = None
                for v in versions_data:
                    game_versions = v.get("game_versions", [])
                    if version in game_versions:
                        files = v.get("files", [])
                        if files:
                            target_version_file = files[0].get("url")
                            break
                
                if not target_version_file and versions_data:
                    target_version_file = versions_data[0].get("files", [])[0].get("url")

                if not target_version_file:
                    self.res_status_label.configure(text=f"{item_name} için uygun dosya bulunamadı.")
                    return

                res_dir = os.path.expanduser(f"~/Library/Application Support/minecraft_profiles/{selected_profile}/{target_folder}")
                os.makedirs(res_dir, exist_ok=True)

                file_name = target_version_file.split("/")[-1]
                file_path = os.path.join(res_dir, file_name)

                urllib.request.urlretrieve(target_version_file, file_path)
                self.res_status_label.configure(text=f"{item_name} başarıyla [{selected_profile}] -> {target_folder} klasörüne indirildi!")
            except Exception as e:
                self.res_status_label.configure(text=f"{item_name} indirilemedi!")
                print("Kaynak İndirme Hatası:", e)

        threading.Thread(target=_download, daemon=True).start()

    def start_launch_thread(self):
        threading.Thread(target=self.launch_game, daemon=True).start()

    def launch_game(self):
        username = self.username_entry.get().strip()
        current_selection = self.version_menu.get()

        if not username:
            self.status_label.configure(text="Lütfen bir kullanıcı adı girin!")
            return

        if current_selection in ["Yükleniyor...", "Seçime uygun sürüm yok", "+ Yeni Sürüm Oluştur", ""]:
            self.status_label.configure(text="Geçerli bir profil seçin!")
            return

        profile_name = current_selection.split(" (")[0]
        profile_info = self.profiles.get(profile_name, {"version": "1.20.4", "loader": "Vanilla (Saf)"})
        version = profile_info["version"]
        loader = profile_info["loader"]

        self.save_config()

        self.launch_button.configure(state="disabled")
        self.status_label.configure(text="Minecraft ana dizini kontrol ediliyor...")

        minecraft_directory = os.path.expanduser("~/Library/Application Support/minecraft")
        custom_game_directory = os.path.expanduser(f"~/Library/Application Support/minecraft_profiles/{profile_name}")
        os.makedirs(os.path.join(custom_game_directory, "mods"), exist_ok=True)
        os.makedirs(os.path.join(custom_game_directory, "resourcepacks"), exist_ok=True)
        os.makedirs(os.path.join(custom_game_directory, "shaderpacks"), exist_ok=True)

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
