import subprocess
import sys
import os
import json
import threading
import glob
import urllib.request
import urllib.parse
import customtkinter as ctk
from PIL import Image, ImageDraw, ImageTk
import minecraft_launcher_lib

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("dark-blue")

CONFIG_FILE = "config.json"

def generate_default_flags():
    os.makedirs("assets", exist_ok=True)
    
    # 1. TÜRKİYE (2400x1800 HD Net Hilal ve Yıldız)
    img_tr = Image.new("RGBA", (2400, 1800), color=(227, 10, 23, 255))
    d_tr = ImageDraw.Draw(img_tr)
    # Beyaz Daire
    d_tr.ellipse([500, 350, 1250, 1450], fill=(255, 255, 255, 255))
    # Kırmızı Daire (Hilal Kesimi)
    d_tr.ellipse([700, 480, 1350, 1320], fill=(227, 10, 23, 255))
    # Yıldız Koordinatları
    star_points = [(1550, 900), (1380, 750), (1440, 970), (1260, 1100), (1500, 1100), (1560, 1320), (1620, 1100), (1860, 1100), (1680, 970), (1740, 750)]
    d_tr.polygon(star_points, fill=(255, 255, 255, 255))
    img_tr.convert("RGB").save(os.path.join("assets", "tr.png"))

    # 2. İNGİLTERE (Union Jack)
    img_gb = Image.new("RGBA", (2400, 1800), color=(1, 33, 105, 255))
    d_gb = ImageDraw.Draw(img_gb)
    d_gb.line([0, 0, 2400, 1800], fill=(255, 255, 255, 255), width=280)
    d_gb.line([2400, 0, 0, 1800], fill=(255, 255, 255, 255), width=280)
    d_gb.line([0, 0, 2400, 1800], fill=(200, 16, 46, 255), width=140)
    d_gb.line([2400, 0, 0, 1800], fill=(200, 16, 46, 255), width=140)
    d_gb.rectangle([950, 0, 1450, 1800], fill=(255, 255, 255, 255))
    d_gb.rectangle([0, 650, 2400, 1150], fill=(255, 255, 255, 255))
    d_gb.rectangle([1050, 0, 1350, 1800], fill=(200, 16, 46, 255))
    d_gb.rectangle([0, 750, 2400, 1050], fill=(200, 16, 46, 255))
    img_gb.convert("RGB").save(os.path.join("assets", "gb.png"))

    # 3. ABD
    img_us = Image.new("RGBA", (2400, 1800), color=(255, 255, 255, 255))
    d_us = ImageDraw.Draw(img_us)
    stripe_h = 1800 / 13
    for i in range(13):
        if i % 2 == 0:
            d_us.rectangle([0, i*stripe_h, 2400, (i+1)*stripe_h], fill=(178, 34, 52, 255))
    d_us.rectangle([0, 0, 960, 7 * stripe_h], fill=(60, 59, 110, 255))
    img_us.convert("RGB").save(os.path.join("assets", "us.png"))

    # 4. FRANSA
    img_fr = Image.new("RGBA", (2400, 1800), color=(255, 255, 255, 255))
    d_fr = ImageDraw.Draw(img_fr)
    d_fr.rectangle([0, 0, 800, 1800], fill=(0, 38, 84, 255))
    d_fr.rectangle([1600, 0, 2400, 1800], fill=(239, 65, 53, 255))
    img_fr.convert("RGB").save(os.path.join("assets", "fr.png"))

    # 5. İTALYA
    img_it = Image.new("RGBA", (2400, 1800), color=(255, 255, 255, 255))
    d_it = ImageDraw.Draw(img_it)
    d_it.rectangle([0, 0, 800, 1800], fill=(0, 146, 70, 255))
    d_it.rectangle([1600, 0, 2400, 1800], fill=(206, 43, 55, 255))
    img_it.convert("RGB").save(os.path.join("assets", "it.png"))

    # 6. AZERBAYCAN
    img_az = Image.new("RGBA", (2400, 1800), color=(255, 255, 255, 255))
    d_az = ImageDraw.Draw(img_az)
    d_az.rectangle([0, 0, 2400, 600], fill=(0, 181, 226, 255))
    d_az.rectangle([0, 600, 2400, 1200], fill=(239, 51, 64, 255))
    d_az.rectangle([0, 1200, 2400, 1800], fill=(0, 152, 116, 255))
    d_az.ellipse([1000, 700, 1350, 1100], fill=(255, 255, 255, 255))
    d_az.ellipse([1070, 740, 1330, 1060], fill=(239, 51, 64, 255))
    img_az.convert("RGB").save(os.path.join("assets", "az.png"))

    # 7. ALMANYA
    img_de = Image.new("RGBA", (2400, 1800), color=(0, 0, 0, 255))
    d_de = ImageDraw.Draw(img_de)
    d_de.rectangle([0, 600, 2400, 1200], fill=(221, 0, 0, 255))
    d_de.rectangle([0, 1200, 2400, 1800], fill=(255, 206, 0, 255))
    img_de.convert("RGB").save(os.path.join("assets", "de.png"))

    # 8. RUSYA
    img_ru = Image.new("RGBA", (2400, 1800), color=(255, 255, 255, 255))
    d_ru = ImageDraw.Draw(img_ru)
    d_ru.rectangle([0, 600, 2400, 1200], fill=(0, 57, 166, 255))
    d_ru.rectangle([0, 1200, 2400, 1800], fill=(213, 43, 30, 255))
    img_ru.convert("RGB").save(os.path.join("assets", "ru.png"))

    # 9. ÇİN
    img_cn = Image.new("RGBA", (2400, 1800), color=(222, 41, 16, 255))
    d_cn = ImageDraw.Draw(img_cn)
    d_cn.ellipse([250, 250, 650, 650], fill=(255, 222, 0, 255))
    img_cn.convert("RGB").save(os.path.join("assets", "cn.png"))

    # 10. JAPONYA
    img_jp = Image.new("RGBA", (2400, 1800), color=(255, 255, 255, 255))
    d_jp = ImageDraw.Draw(img_jp)
    d_jp.ellipse([800, 450, 1600, 1350], fill=(188, 0, 45, 255))
    img_jp.convert("RGB").save(os.path.join("assets", "jp.png"))

# 11 Farklı Dil Destekli Sözlük
LANGUAGES = {
    "Türkçe": {
        "title": "dpLauncher v6",
        "launch": "Oyunu Başlat",
        "home": "Ana Ekran",
        "mods": "Modlar",
        "resources": "Kaynaklar",
        "folder": "Sürüm Klasörü",
        "settings": "Ayarlar",
        "username": "Kullanıcı Adı:",
        "version_sel": "Profil / Sürüm Seç:",
        "status_ready": "Hazır!",
        "profile_mgmt": "Profil & Sürüm Yönetimi",
        "lang_text": "Dil / Language:",
        "ram_text": "RAM Sınırı:",
        "settings_title": "Gelişmiş Ayarlar",
        "snapshot_text": "Snapshot Sürümünü Göster",
        "beta_text": "Alpha / Beta Sürümünü Göster",
        "java_text": "Java Sürümü Seçin:",
        "save_btn": "Kaydet ve Listeyi Yenile",
        "flag_file": "tr.png"
    },
    "English": {
        "title": "dpLauncher v6",
        "launch": "Launch Game",
        "home": "Home",
        "mods": "Mods",
        "resources": "Resources",
        "folder": "Version Folder",
        "settings": "Settings",
        "username": "Username:",
        "version_sel": "Select Profile / Version:",
        "status_ready": "Ready!",
        "profile_mgmt": "Profile & Version Management",
        "lang_text": "Language:",
        "ram_text": "RAM Limit:",
        "settings_title": "Advanced Settings",
        "snapshot_text": "Show Snapshots",
        "beta_text": "Show Alpha / Betas",
        "java_text": "Select Java Version:",
        "save_btn": "Save and Refresh",
        "flag_file": "gb.png"
    },
    "English (US)": {
        "title": "dpLauncher v6",
        "launch": "Launch Game",
        "home": "Home",
        "mods": "Mods",
        "resources": "Resources",
        "folder": "Version Folder",
        "settings": "Settings",
        "username": "Username:",
        "version_sel": "Select Profile / Version:",
        "status_ready": "Ready!",
        "profile_mgmt": "Profile & Version Management",
        "lang_text": "Language:",
        "ram_text": "RAM Limit:",
        "settings_title": "Advanced Settings",
        "snapshot_text": "Show Snapshots",
        "beta_text": "Show Alpha / Betas",
        "java_text": "Select Java Version:",
        "save_btn": "Save and Refresh",
        "flag_file": "us.png"
    },
    "Français": {
        "title": "dpLauncher v6",
        "launch": "Lancer le jeu",
        "home": "Accueil",
        "mods": "Mods",
        "resources": "Ressources",
        "folder": "Dossier de version",
        "settings": "Paramètres",
        "username": "Nom d'utilisateur:",
        "version_sel": "Sélectionner Profil / Version:",
        "status_ready": "Prêt !",
        "profile_mgmt": "Gestion des Profils et Versions",
        "lang_text": "Langue:",
        "ram_text": "Limite RAM:",
        "settings_title": "Paramètres Avancés",
        "snapshot_text": "Afficher les Snapshots",
        "beta_text": "Afficher Alpha / Betas",
        "java_text": "Sélectionner la version Java:",
        "save_btn": "Enregistrer et Actualiser",
        "flag_file": "fr.png"
    },
    "Italiano": {
        "title": "dpLauncher v6",
        "launch": "Avvia Gioco",
        "home": "Home",
        "mods": "Mod",
        "resources": "Risorse",
        "folder": "Cartella Versione",
        "settings": "Impostazioni",
        "username": "Nome utente:",
        "version_sel": "Seleziona Profilo / Versione:",
        "status_ready": "Pronto!",
        "profile_mgmt": "Gestione Profilo e Versione",
        "lang_text": "Lingua:",
        "ram_text": "Limite RAM:",
        "settings_title": "Impostazioni Avanzate",
        "snapshot_text": "Mostra Snapshot",
        "beta_text": "Mostra Alpha / Beta",
        "java_text": "Seleziona versione Java:",
        "save_btn": "Salva e Aggiorna",
        "flag_file": "it.png"
    },
    "Azərbaycan türkcəsi": {
        "title": "dpLauncher v6",
        "launch": "Oyunu Başlat",
        "home": "Ana Səhifə",
        "mods": "Modlar",
        "resources": "Resurslar",
        "folder": "Versiya Qovluğu",
        "settings": "Tənzimləmələr",
        "username": "İstifadəçi adı:",
        "version_sel": "Profil / Versiya Seç:",
        "status_ready": "Hazırdır!",
        "profile_mgmt": "Profil və Versiya İdarəetməsi",
        "lang_text": "Dil:",
        "ram_text": "RAM Həddi:",
        "settings_title": "Ətraflı Tənzimləmələr",
        "snapshot_text": "Snapshot Versiyalarını Göstər",
        "beta_text": "Alpha / Beta Versiyalarını Göstər",
        "java_text": "Java Versiyasını Seç:",
        "save_btn": "Yadda saxla və Yenilə",
        "flag_file": "az.png"
    },
    "Deutsch": {
        "title": "dpLauncher v6",
        "launch": "Spiel starten",
        "home": "Startseite",
        "mods": "Mods",
        "resources": "Ressourcen",
        "folder": "Versionsordner",
        "settings": "Einstellungen",
        "username": "Benutzername:",
        "version_sel": "Profil / Version wählen:",
        "status_ready": "Bereit!",
        "profile_mgmt": "Profil- & Versionsverwaltung",
        "lang_text": "Sprache:",
        "ram_text": "RAM-Limit:",
        "settings_title": "Erweiterte Einstellungen",
        "snapshot_text": "Snapshots anzeigen",
        "beta_text": "Alpha / Betas anzeigen",
        "java_text": "Java-Version auswählen:",
        "save_btn": "Speichern und Aktualisieren",
        "flag_file": "de.png"
    },
    "Русский": {
        "title": "dpLauncher v6",
        "launch": "Запустить игру",
        "home": "Главная",
        "mods": "Моды",
        "resources": "Ресурсы",
        "folder": "Папка версии",
        "settings": "Настройки",
        "username": "Имя пользователя:",
        "version_sel": "Выберите профиль / версию:",
        "status_ready": "Управление профилями и версиями",
        "lang_text": "Язык:",
        "ram_text": "Лимит RAM:",
        "settings_title": "Расширенные настройки",
        "snapshot_text": "Показывать Снапшоты",
        "beta_text": "Показывать Альфа/Бета",
        "java_text": "Выберите версию Java:",
        "save_btn": "Сохранить и обновить",
        "flag_file": "ru.png"
    },
    "中文": {
        "title": "dpLauncher v6",
        "launch": "启动游戏",
        "home": "主页",
        "mods": "模组",
        "resources": "资源",
        "folder": "版本文件夹",
        "settings": "设置",
        "username": "用户名:",
        "version_sel": "选择配置文件 / 版本:",
        "status_ready": "就绪!",
        "profile_mgmt": "配置与版本管理",
        "lang_text": "语言:",
        "ram_text": "RAM 限制:",
        "settings_title": "高级设置",
        "snapshot_text": "显示快照版本",
        "beta_text": "显示 Alpha / Beta 版本",
        "java_text": "选择 Java 版本:",
        "save_btn": "保存并刷新",
        "flag_file": "cn.png"
    },
    "日本語": {
        "title": "dpLauncher v6",
        "launch": "ゲーム起動",
        "home": "ホーム",
        "mods": "Mod",
        "resources": "リソース",
        "folder": "バージョンフォルダ",
        "settings": "設定",
        "username": "ユーザー名:",
        "version_sel": "プロファイル / バージョン選択:",
        "status_ready": "準備完了!",
        "profile_mgmt": "プロファイルとバージョンの管理",
        "lang_text": "言語:",
        "ram_text": "RAM制限:",
        "settings_title": "高度な設定",
        "snapshot_text": "スナップショットを表示",
        "beta_text": "Alpha / Betaを表示",
        "java_text": "Javaバージョンを選択:",
        "save_btn": "保存して更新",
        "flag_file": "jp.png"
    },
    "Diğer Türkçeler": {
        "title": "dpLauncher v6",
        "launch": "Oyunı Başlat",
        "home": "Ana Ekran",
        "mods": "Modlar",
        "resources": "Resurslar",
        "folder": "Versiyoni Papka",
        "settings": "Tenzimlemeler",
        "username": "Kullanıcı Adı:",
        "version_sel": "Profil / Versiyoni Sayla:",
        "status_ready": "Tayyar!",
        "lang_text": "Til / Dil:",
        "ram_text": "RAM Sınırı:",
        "settings_title": "Tenzimlemeler",
        "snapshot_text": "Snapshot Göster",
        "beta_text": "Beta Göster",
        "java_text": "Java Sayla:",
        "save_btn": "Kaydet ve Yenile",
        "flag_file": "tr.png"
    }
}

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
        
        # # # generate_default_flags()

        self.current_lang = "Türkçe"
        self.t = LANGUAGES[self.current_lang]
        
        self.title(self.t["title"])
        self.geometry("920x600")
        self.minsize(840, 540)

        self.show_snapshots = True
        self.show_betas = False
        self.custom_java = ""
        self.saved_username = ""
        self.selected_ram = "4G"
        self.all_versions = []
        self.profiles = {"Varsayılan Profil": {"version": "1.20.4", "loader": "Vanilla (Saf)"}}
        self.current_resource_type = "resourcepack"

        self.load_config()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SOL MENÜ ---
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color=("#f0f0f0", "#18191a"))
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(8, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="dpLauncher v6", font=("Arial", 16, "bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 20))

        self.launch_button = ctk.CTkButton(
            self.sidebar_frame, text=self.t["launch"], command=self.start_launch_thread, 
            width=180, height=40, fg_color="#ffd426", hover_color="#e6be1f", text_color="#111111",
            font=("Arial", 13, "bold"), corner_radius=8
        )
        self.launch_button.grid(row=1, column=0, padx=20, pady=10)

        self.btn_home = ctk.CTkButton(
            self.sidebar_frame, text=self.t["home"], command=self.show_main_screen, 
            width=180, height=35, fg_color=("#e4e4e7", "#2f3136"), hover_color=("#d4d4d8", "#3f4248"),
            text_color=("#111111", "#ffffff"), font=("Arial", 12, "bold"), corner_radius=8
        )
        self.btn_home.grid(row=2, column=0, padx=20, pady=5)

        self.btn_mods = ctk.CTkButton(
            self.sidebar_frame, text=self.t["mods"], command=self.show_mods_screen, 
            width=180, height=35, fg_color=("#e4e4e7", "#2f3136"), hover_color=("#d4d4d8", "#3f4248"),
            text_color=("#111111", "#ffffff"), font=("Arial", 12, "bold"), corner_radius=8
        )
        self.btn_mods.grid(row=3, column=0, padx=20, pady=5)

        self.btn_resources = ctk.CTkButton(
            self.sidebar_frame, text=self.t["resources"], command=self.show_resources_screen, 
            width=180, height=35, fg_color=("#e4e4e7", "#2f3136"), hover_color=("#d4d4d8", "#3f4248"),
            text_color=("#111111", "#ffffff"), font=("Arial", 12, "bold"), corner_radius=8
        )
        self.btn_resources.grid(row=4, column=0, padx=20, pady=5)

        self.folder_button = ctk.CTkButton(
            self.sidebar_frame, text=self.t["folder"], command=self.open_version_folder, 
            width=180, height=35, fg_color=("#e4e4e7", "#2f3136"), hover_color=("#d4d4d8", "#3f4248"),
            text_color=("#111111", "#ffffff"), corner_radius=8
        )
        self.folder_button.grid(row=5, column=0, padx=20, pady=5)

        self.settings_button = ctk.CTkButton(
            self.sidebar_frame, text=self.t["settings"], command=self.show_settings_screen, 
            width=180, height=35, fg_color=("#e4e4e7", "#2f3136"), hover_color=("#d4d4d8", "#3f4248"),
            text_color=("#111111", "#ffffff"), corner_radius=8
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

        self.lang_top_frame = ctk.CTkFrame(self.main_screen_frame, fg_color="transparent")
        self.lang_top_frame.grid(row=0, column=0, padx=30, pady=(20, 0), sticky="ew")
        
        self.lang_label = ctk.CTkLabel(self.lang_top_frame, text=self.t["lang_text"], font=("Arial", 12, "bold"))
        self.lang_label.pack(side="left", padx=(0, 10))
        
        lang_list = [
            "Türkçe", "English", "English (US)", "Français", 
            "Italiano", "Azərbaycan türkcəsi", "Deutsch", 
            "Русский", "中文", "日本語", "Diğer Türkçeler"
        ]
        self.lang_menu = ctk.CTkOptionMenu(
            self.lang_top_frame, values=lang_list, command=self.change_language,
            width=180, fg_color="#ffd426", button_color="#e6be1f", button_hover_color="#d4aa12", text_color="#111111"
        )
        self.lang_menu.set(self.current_lang)
        self.lang_menu.pack(side="left")

        # Jilet gibi keskin HD bayrak simgesi
        self.flag_label = ctk.CTkLabel(self.lang_top_frame, text="")
        self.flag_label.pack(side="left", padx=(12, 0))
        self.update_flag_icon(self.current_lang)

        self.label = ctk.CTkLabel(self.main_screen_frame, text=self.t.get("profile_mgmt", "Profil & Sürüm Yönetimi"), font=("Arial", 20, "bold"))
        self.label.grid(row=1, column=0, padx=30, pady=(15, 15), sticky="w")

        BOX_WIDTH = 300

        self.card_user = ctk.CTkFrame(self.main_screen_frame, fg_color=("#e4e4e7", "#2f3136"), corner_radius=12, height=75)
        self.card_user.grid(row=2, column=0, padx=30, pady=8, sticky="ew")
        self.user_title_lbl = ctk.CTkLabel(self.card_user, text=self.t["username"], font=("Arial", 12, "bold"))
        self.user_title_lbl.place(x=20, y=25)
        self.username_entry = ctk.CTkEntry(self.card_user, placeholder_text="Kullanıcı Adı Girin", width=BOX_WIDTH, height=35, fg_color=("#ffffff", "#40444b"), border_color="#ffd426", corner_radius=8)
        self.username_entry.place(relx=1.0, x=-20, y=20, anchor="ne")
        if self.saved_username:
            self.username_entry.insert(0, self.saved_username)

        self.card_version = ctk.CTkFrame(self.main_screen_frame, fg_color=("#e4e4e7", "#2f3136"), corner_radius=12, height=75)
        self.card_version.grid(row=3, column=0, padx=30, pady=8, sticky="ew")
        self.ver_title_lbl = ctk.CTkLabel(self.card_version, text=self.t["version_sel"], font=("Arial", 12, "bold"))
        self.ver_title_lbl.place(x=20, y=25)
        
        display_list = ["+ Yeni Sürüm Oluştur"] + [f"{name} ({info['version']} - {info['loader']})" for name, info in self.profiles.items()]
        self.version_menu = ctk.CTkOptionMenu(self.card_version, values=display_list, width=BOX_WIDTH, height=35, fg_color="#ffd426", button_color="#e6be1f", button_hover_color="#d4aa12", text_color="#111111", corner_radius=8, command=self.on_profile_or_new_selected)
        self.version_menu.place(relx=1.0, x=-20, y=20, anchor="ne")

        self.status_label = ctk.CTkLabel(self.main_screen_frame, text="Sürümler internetten yükleniyor...", font=("Arial", 11), text_color="#888888")
        self.status_label.grid(row=4, column=0, padx=30, pady=(15, 30), sticky="w")

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
            self.mods_screen_frame, text="Mod Ara", command=lambda: threading.Thread(target=self.search_mods, daemon=True).start(), 
            fg_color="#ffd426", hover_color="#e6be1f", text_color="#111111", font=("Arial", 12, "bold"), width=120, height=35, corner_radius=8
        )
        self.search_mod_btn.grid(row=1, column=0, padx=(390, 30), pady=5, sticky="w")

        self.mod_results_frame = ctk.CTkScrollableFrame(self.mods_screen_frame, width=540, height=320, fg_color=("#e4e4e7", "#2f3136"), corner_radius=12)
        self.mod_results_frame.grid(row=2, column=0, padx=30, pady=15, sticky="w")

        self.mod_status_label = ctk.CTkLabel(self.mods_screen_frame, text="Aramak istediğiniz modu yazın ve arayın.", font=("Arial", 11), text_color="#888888")
        self.mod_status_label.grid(row=3, column=0, padx=30, pady=(0, 20), sticky="w")

        # 3. KAYNAKLAR EKRANI
        self.resources_screen_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.resources_screen_frame.grid(row=0, column=0, sticky="nsew")
        self.resources_screen_frame.grid_columnconfigure(0, weight=1)

        self.res_top_frame = ctk.CTkFrame(self.resources_screen_frame, fg_color="transparent")
        self.res_top_frame.grid(row=0, column=0, padx=30, pady=(30, 10), sticky="ew")
        self.res_top_frame.grid_columnconfigure(2, weight=1)

        ctk.CTkLabel(self.res_top_frame, text="Kaynak & Gölgelendirici Merkezi", font=("Arial", 20, "bold")).grid(row=0, column=0, sticky="w")
        
        self.btn_res_pack = ctk.CTkButton(self.res_top_frame, text="Kaynak Paketi", command=lambda: self.switch_resource_type("resourcepack"), width=120, height=30, fg_color="#ffd426", text_color="#111111", font=("Arial", 11, "bold"))
        self.btn_res_pack.grid(row=0, column=1, padx=(20, 10), sticky="w")

        self.btn_shader = ctk.CTkButton(self.res_top_frame, text="Gölgelendirici (Shader)", command=lambda: self.switch_resource_type("shader"), width=150, height=30, fg_color=("#e4e4e7", "#2f3136"), text_color=("#111111", "#ffffff"), font=("Arial", 11, "bold"))
        self.btn_shader.grid(row=0, column=2, padx=5, sticky="w")

        self.res_profile_menu = ctk.CTkOptionMenu(self.res_top_frame, values=profile_names, width=180, height=30, fg_color="#ffd426", button_color="#e6be1f", button_hover_color="#d4aa12", text_color="#111111")
        self.res_profile_menu.grid(row=0, column=3, sticky="e")

        self.res_search_entry = ctk.CTkEntry(self.resources_screen_frame, placeholder_text="Kaynak veya Shader ara...", width=350, height=35, fg_color=("#ffffff", "#40444b"), border_color="#ffd426", corner_radius=8)
        self.res_search_entry.grid(row=1, column=0, padx=30, pady=5, sticky="w")

        self.search_res_btn = ctk.CTkButton(
            self.resources_screen_frame, text="Ara", command=lambda: threading.Thread(target=self.search_resources, daemon=True).start(), 
            fg_color="#ffd426", hover_color="#e6be1f", text_color="#111111", font=("Arial", 12, "bold"), width=120, height=35, corner_radius=8
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

        self.settings_title_lbl = ctk.CTkLabel(self.settings_screen_frame, text=self.t["settings_title"], font=("Arial", 20, "bold"))
        self.settings_title_lbl.grid(row=0, column=0, padx=30, pady=(30, 20), sticky="w")

        self.snapshot_switch = ctk.CTkSwitch(self.settings_screen_frame, text=self.t["snapshot_text"], progress_color="#ffd426")
        if self.show_snapshots:
            self.snapshot_switch.select()
        self.snapshot_switch.grid(row=1, column=0, padx=30, pady=10, sticky="w")

        self.beta_switch = ctk.CTkSwitch(self.settings_screen_frame, text=self.t["beta_text"], progress_color="#ffd426")
        if self.show_betas:
            self.beta_switch.select()
        self.beta_switch.grid(row=2, column=0, padx=30, pady=10, sticky="w")

        self.ram_title_lbl = ctk.CTkLabel(self.settings_screen_frame, text=self.t["ram_text"], font=("Arial", 12, "bold"))
        self.ram_title_lbl.grid(row=3, column=0, padx=30, pady=(15, 5), sticky="w")
        
        ram_options = ["2 GB (2G)", "4 GB (4G)", "6 GB (6G)", "8 GB (8G)", "12 GB (12G)"]
        self.ram_menu = ctk.CTkOptionMenu(self.settings_screen_frame, values=ram_options, width=BOX_WIDTH, height=35, fg_color="#ffd426", button_color="#e6be1f", button_hover_color="#d4aa12", text_color="#111111")
        for opt in ram_options:
            if self.selected_ram in opt:
                self.ram_menu.set(opt)
                break
        self.ram_menu.grid(row=4, column=0, padx=30, pady=5, sticky="w")

        self.java_title_lbl = ctk.CTkLabel(self.settings_screen_frame, text=self.t["java_text"], font=("Arial", 12, "bold"))
        self.java_title_lbl.grid(row=5, column=0, padx=30, pady=(15, 5), sticky="w")
        
        self.java_dict = detect_java_versions()
        java_names = list(self.java_dict.keys())
        
        current_java_name = java_names[0]
        for name, path in self.java_dict.items():
            if path == self.custom_java:
                current_java_name = name
                break

        self.java_menu = ctk.CTkOptionMenu(self.settings_screen_frame, values=java_names, width=BOX_WIDTH, height=35, fg_color="#ffd426", button_color="#e6be1f", button_hover_color="#d4aa12", text_color="#111111")
        self.java_menu.set(current_java_name)
        self.java_menu.grid(row=6, column=0, padx=30, pady=5, sticky="w")

        self.save_settings_btn = ctk.CTkButton(
            self.settings_screen_frame, text=self.t["save_btn"], command=self.apply_and_close_settings, 
            fg_color="#ffd426", hover_color="#e6be1f", text_color="#111111", font=("Arial", 12, "bold"), width=BOX_WIDTH, height=38, corner_radius=8
        )
        self.save_settings_btn.grid(row=7, column=0, padx=30, pady=25, sticky="w")

        self.show_main_screen()
        threading.Thread(target=self.load_versions, daemon=True).start()

    def update_flag_icon(self, lang_name):
        """Yüksek çözünürlüklü bayrak görselini arayüze kusursuz boyutta yansıtır"""
        try:
            flag_filename = LANGUAGES[lang_name]["flag_file"]
            flag_path = os.path.join("assets", flag_filename)
            
            if os.path.exists(flag_path):
                img = Image.open(flag_path)
                # Retina ekran uyumlu yüksek kaliteli ölçeklendirme
                self.flag_image = ctk.CTkImage(light_image=img, dark_image=img, size=(30, 20))
                self.flag_label.configure(image=self.flag_image, text="")
            else:
                self.flag_label.configure(image="", text="🚩")
        except Exception as e:
            print("Bayrak yüklenemedi:", e)
            self.flag_label.configure(image="", text="🚩")

    def change_language(self, selected_lang):
        """Seçilen dile göre arayüzü ve bayrağı günceller"""
        self.current_lang = selected_lang
        self.t = LANGUAGES[selected_lang]
        
        self.update_flag_icon(selected_lang)
        
        self.title(self.t["title"])
        self.logo_label.configure(text=self.t["title"])
        self.launch_button.configure(text=self.t["launch"])
        self.btn_home.configure(text=self.t["home"])
        self.btn_mods.configure(text=self.t["mods"])
        self.btn_resources.configure(text=self.t["resources"])
        self.folder_button.configure(text=self.t["folder"])
        self.settings_button.configure(text=self.t["settings"])
        self.lang_label.configure(text=self.t["lang_text"])
        self.label.configure(text=self.t.get("profile_mgmt", "Profil & Sürüm Yönetimi"))
        self.user_title_lbl.configure(text=self.t["username"])
        self.ver_title_lbl.configure(text=self.t["version_sel"])
        self.settings_title_lbl.configure(text=self.t["settings_title"])
        self.snapshot_switch.configure(text=self.t["snapshot_text"])
        self.beta_switch.configure(text=self.t["beta_text"])
        self.ram_title_lbl.configure(text=self.t["ram_text"])
        self.java_title_lbl.configure(text=self.t["java_text"])
        self.save_settings_btn.configure(text=self.t["save_btn"])

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
            self.res_search_entry.configure(placeholder_text="Kaynak paketi ara...")
        else:
            self.btn_shader.configure(fg_color="#ffd426", text_color="#111111")
            self.btn_res_pack.configure(fg_color=("#e4e4e7", "#2f3136"), text_color=("#111111", "#ffffff"))
            self.res_search_entry.configure(placeholder_text="Shader / Gölgelendirici ara...")

    def apply_and_close_settings(self):
        self.show_snapshots = True if self.snapshot_switch.get() == 1 else False
        self.show_betas = True if self.beta_switch.get() == 1 else False
        
        selected_ram_str = self.ram_menu.get()
        if "(" in selected_ram_str:
            self.selected_ram = selected_ram_str.split("(")[1].replace(")", "").strip()
        else:
            self.selected_ram = "4G"

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
                    self.selected_ram = data.get("ram", "4G")
                    loaded_profiles = data.get("profiles", None)
                    if isinstance(loaded_profiles, dict):
                        self.profiles = loaded_profiles
            except Exception as e:
                print("Config okunamadı:", e)

    def save_config(self):
        data = {
            "username": self.username_entry.get().strip(),
            "show_snapshots": self.show_snapshots,
            "show_betas": self.show_betas,
            "custom_java": self.custom_java,
            "ram": self.selected_ram,
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
            self.status_label.configure(text=self.t["status_ready"])

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
        name_entry.insert(0, "YeniProfilim")

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
            params = urllib.parse.urlencode({'query': query, 'facets': '[["project_type:mod"]]'})
            url = f"https://api.modrinth.com/v2/search?{params}"
            req = urllib.request.Request(url, headers={'User-Agent': 'dpLauncher/6.0 (doruk@launcher.app)'})
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
                ctk.CTkLabel(card, text=name, font=("Arial", 12, "bold"), text_color=("#111111", "#ffffff")).pack(anchor="w", padx=10, pady=(8, 2))
                ctk.CTkLabel(card, text=desc, font=("Arial", 10), text_color=("#666666", "#aaaaaa"), wraplength=450, justify="left").pack(anchor="w", padx=10, pady=2)
                ctk.CTkButton(card, text="Bu Profile İndir (+Bağımlılıklar)", command=lambda pid=project_id, mname=name: self.download_mod_with_dependencies(pid, mname), fg_color="#ffd426", hover_color="#e6be1f", text_color="#111111", font=("Arial", 10, "bold"), width=180, height=28, corner_radius=6).pack(anchor="e", padx=10, pady=(5, 8))
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
                req = urllib.request.Request(versions_url, headers={'User-Agent': 'dpLauncher/6.0 (doruk@launcher.app)'})
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
                for dep in target_version_obj.get("dependencies", []):
                    if dep.get("dependency_type") == "required":
                        dep_project_id = dep.get("project_id")
                        if dep_project_id:
                            try:
                                proj_url = f"https://api.modrinth.com/v2/project/{dep_project_id}"
                                preq = urllib.request.Request(proj_url, headers={'User-Agent': 'dpLauncher/6.0 (doruk@launcher.app)'})
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
            facet_type = "resourcepack" if self.current_resource_type == "resourcepack" else "shader"
            params = urllib.parse.urlencode({'query': query, 'facets': f'[["project_type:{facet_type}"]]'})
            url = f"https://api.modrinth.com/v2/search?{params}"
            req = urllib.request.Request(url, headers={'User-Agent': 'dpLauncher/6.0 (doruk@launcher.app)'})
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
                ctk.CTkLabel(card, text=name, font=("Arial", 12, "bold"), text_color=("#111111", "#ffffff")).pack(anchor="w", padx=10, pady=(8, 2))
                ctk.CTkLabel(card, text=desc, font=("Arial", 10), text_color=("#666666", "#aaaaaa"), wraplength=450, justify="left").pack(anchor="w", padx=10, pady=2)
                ctk.CTkButton(card, text="Bu Profile İndir", command=lambda pid=project_id, mname=name: self.download_resource_file(pid, mname), fg_color="#ffd426", hover_color="#e6be1f", text_color="#111111", font=("Arial", 10, "bold"), width=130, height=28, corner_radius=6).pack(anchor="e", padx=10, pady=(5, 8))
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
                req = urllib.request.Request(versions_url, headers={'User-Agent': 'dpLauncher/6.0 (doruk@launcher.app)'})
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
                "jvmArguments": ["-XstartOnFirstThread", f"-Xmx{self.selected_ram}", f"-Xms2G"],
                "gameDirectory": custom_game_directory
            }
            if self.custom_java:
                options["executablePath"] = self.custom_java

            minecraft_command = minecraft_launcher_lib.command.get_minecraft_command(target_version, minecraft_directory, options)
            cleaned_command = [arg for arg in minecraft_command if "-Djava.system.class.loader" not in arg]
            self.status_label.configure(text="İyi oyunlar!")
            subprocess.call(cleaned_command)
        except Exception as e:
            self.status_label.configure(text=f"Hata oluştu: {str(e)}")
            print(e)
        finally:
            self.launch_button.configure(state="normal")

if __name__ == "__main__":
    app = MinecraftLauncher()
    app.mainloop()
