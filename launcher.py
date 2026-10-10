import subprocess
import sys
import os
import json
import threading
import glob
import customtkinter as ctk
import minecraft_launcher_lib

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

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

class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Launcher Ayarları")
        self.geometry("420x400")
        self.resizable(False, False)
        self.parent = parent

        self.grab_set()

        ctk.CTkLabel(self, text="Gelişmiş Ayarlar", font=("Arial", 18, "bold")).pack(pady=20)

        self.snapshot_switch = ctk.CTkSwitch(self, text="Snapshot Sürümünü Göster")
        if parent.show_snapshots:
            self.snapshot_switch.select()
        self.snapshot_switch.pack(pady=10, anchor="w", padx=40)

        self.beta_switch = ctk.CTkSwitch(self, text="Alpha / Beta Sürümünü Göster")
        if parent.show_betas:
            self.beta_switch.select()
        self.beta_switch.pack(pady=10, anchor="w", padx=40)

        ctk.CTkLabel(self, text="Java Sürümü Seçin:", font=("Arial", 12, "bold")).pack(pady=(15, 0), anchor="w", padx=40)
        
        self.java_dict = detect_java_versions()
        java_names = list(self.java_dict.keys())
        
        current_java_name = java_names[0]
        for name, path in self.java_dict.items():
            if path == parent.custom_java:
                current_java_name = name
                break

        self.java_menu = ctk.CTkOptionMenu(self, values=java_names, width=330, height=35)
        self.java_menu.set(current_java_name)
        self.java_menu.pack(pady=5)

        ctk.CTkButton(self, text="Kaydet ve Listeyi Yenile", command=self.apply_and_close, fg_color="#2fa572", hover_color="#106a43", width=330, height=35).pack(pady=20)

    def apply_and_close(self):
        self.parent.show_snapshots = True if self.snapshot_switch.get() == 1 else False
        self.parent.show_betas = True if self.beta_switch.get() == 1 else False
        
        selected_java_name = self.java_menu.get()
        self.parent.custom_java = self.java_dict.get(selected_java_name, "java")
        
        self.parent.save_config()
        threading.Thread(target=self.parent.load_versions, daemon=True).start()
        self.destroy()

class MinecraftLauncher(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Özel Minecraft Launcher")
        self.geometry("450x550")
        self.resizable(False, False)

        self.show_snapshots = True
        self.show_betas = False
        self.custom_java = ""
        self.saved_username = ""
        self.all_versions = []

        self.load_config()

        self.label = ctk.CTkLabel(self, text="Minecraft Launcher", font=("Arial", 22, "bold"))
        self.label.pack(pady=15)

        self.username_entry = ctk.CTkEntry(self, placeholder_text="Kullanıcı Adı Girin", width=300, height=40)
        self.username_entry.pack(pady=5)
        if self.saved_username:
            self.username_entry.insert(0, self.saved_username)

        ctk.CTkLabel(self, text="Mod Loader / Sürüm Türü:", font=("Arial", 11, "bold")).pack(anchor="w", padx=75, pady=(5, 0))
        self.loader_menu = ctk.CTkOptionMenu(self, values=["Vanilla (Saf)", "Fabric", "Forge"], width=300, height=35)
        self.loader_menu.pack(pady=5)

        self.status_label = ctk.CTkLabel(self, text="Sürümler internetten yükleniyor...", font=("Arial", 11))
        self.status_label.pack(pady=2)

        self.version_menu = ctk.CTkOptionMenu(self, values=["Yükleniyor..."], width=300, height=40)
        self.version_menu.pack(pady=5)

        self.launch_button = ctk.CTkButton(
            self, 
            text="Oyunu Başlat", 
            command=self.start_launch_thread, 
            width=300, 
            height=40,
            fg_color="#2fa572",
            hover_color="#106a43"
        )
        self.launch_button.pack(pady=10)

        # Seçilen Sürümün/Profilin Klasörünü Aç Butonu
        self.folder_button = ctk.CTkButton(
            self, 
            text="Seçilen Sürümün Klasörünü Aç", 
            command=self.open_version_folder, 
            width=300, 
            height=35, 
            fg_color="#1f6aa5", 
            hover_color="#14486c"
        )
        self.folder_button.pack(pady=5)

        self.settings_button = ctk.CTkButton(
            self, 
            text="Ayarlar", 
            command=self.open_settings, 
            width=300, 
            height=35, 
            fg_color="gray", 
            hover_color="#555555"
        )
        self.settings_button.pack(pady=5)

        threading.Thread(target=self.load_versions, daemon=True).start()

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

    def open_settings(self):
        SettingsWindow(self)

    def open_version_folder(self):
        version = self.version_menu.get()
        loader = self.loader_menu.get()
        
        if version in ["Yükleniyor...", "Seçime uygun sürüm yok", ""]:
            self.status_label.configure(text="Önce geçerli bir sürüm seçin!")
            return

        # Her sürüm için ayrı bir profil klasörü adı oluşturalım
        profile_name = f"{version}_{loader.lower().split()[0]}"
        profiles_dir = os.path.expanduser("~/Library/Application Support/minecraft_profiles")
        version_dir = os.path.join(profiles_dir, profile_name)
        
        # Klasörleri yoksa oluştur
        os.makedirs(os.path.join(version_dir, "mods"), exist_ok=True)
        os.makedirs(os.path.join(version_dir, "resourcepacks"), exist_ok=True)
        
        # Finder'da aç
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

        # Temel ortak oyun dosyaları (jar, kütüphaneler vb. ortak indirilir ki her sürüm için tekrar GB'larca indirme yapmasın)
        minecraft_directory = os.path.expanduser("~/Library/Application Support/minecraft")

        # Fakat modlar, dünyalar ve ayarlar tamamen bu sürüme özel bir alt klasörde tutulacak!
        profile_name = f"{version}_{loader.lower().split()[0]}"
        custom_game_directory = os.path.expanduser(f"~/Library/Application Support/minecraft_profiles/{profile_name}")
        os.makedirs(os.path.join(custom_game_directory, "mods"), exist_ok=True)

        try:
            # Mod loader kurulumu
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
                "gameDirectory": custom_game_directory  # İŞTE BURASI: Modların ve dünyaların karışmamasını sağlayan izole klasör!
            }

            if self.custom_java:
                options["executablePath"] = self.custom_java

            minecraft_command = minecraft_launcher_lib.command.get_minecraft_command(target_version, minecraft_directory, options)
            
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
