import customtkinter as ctk
import requests
import pyperclip
import socket
import threading

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "Unavailable"

def country_flag(code):
    if len(code) != 2:
        return ""
    return chr(0x1F1E6 + ord(code[0]) - 65) + chr(0x1F1E6 + ord(code[1]) - 65)

def lookup():
    lookup_btn.configure(state="disabled", text="Looking up...")
    for w in value_widgets.values():
        w.configure(text="—")
    window.update()

    def fetch():
        try:
            resp = requests.get(
                "http://ip-api.com/json/?fields=status,message,country,countryCode,"
                "regionName,city,zip,lat,lon,timezone,isp,org,query",
                timeout=7,
            )
            resp.raise_for_status()
            d = resp.json()
            if d.get("status") == "success":
                window.after(0, lambda: update_ui(d))
            else:
                window.after(0, lambda: show_error(d.get("message", "Lookup failed")))
        except requests.RequestException:
            window.after(0, lambda: show_error("Network error"))
        finally:
            window.after(0, lambda: lookup_btn.configure(state="normal", text="⟳  Refresh"))

    threading.Thread(target=fetch, daemon=True).start()

def update_ui(d):
    flag = country_flag(d.get("countryCode", ""))
    value_widgets["public_ip"].configure(text=d.get("query", "—"))
    value_widgets["local_ip"].configure(text=get_local_ip())
    value_widgets["country"].configure(text=f"{flag}  {d.get('country', '—')}  ({d.get('countryCode', '')})")
    value_widgets["city"].configure(text=f"{d.get('city', '—')}, {d.get('regionName', '—')}  {d.get('zip', '')}")
    value_widgets["isp"].configure(text=d.get("isp", "—"))
    value_widgets["org"].configure(text=d.get("org", "—"))
    value_widgets["timezone"].configure(text=d.get("timezone", "—"))
    value_widgets["coords"].configure(text=f"{d.get('lat', '—')},  {d.get('lon', '—')}")
    copy_btn.configure(state="normal")
    window._public_ip = d.get("query", "")

def show_error(msg):
    value_widgets["public_ip"].configure(text=f"Error: {msg}")

def copy_public():
    ip = getattr(window, "_public_ip", None)
    if ip:
        pyperclip.copy(ip)
        copy_btn.configure(text="✓  Copied!")
        window.after(1500, lambda: copy_btn.configure(text="⎘  Copy Public IP"))

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

window = ctk.CTk()
window.title("IP Lookup")
window.geometry("430x580")
window.resizable(False, False)

header = ctk.CTkFrame(window, fg_color="#0d1117", corner_radius=0)
header.pack(fill="x")
ctk.CTkLabel(
    header, text="IP Address Lookup",
    font=ctk.CTkFont(size=22, weight="bold"), text_color="#58a6ff"
).pack(pady=(18, 2))
ctk.CTkLabel(
    header, text="Geolocation · Network · ISP",
    font=ctk.CTkFont(size=12), text_color="#8b949e"
).pack(pady=(0, 14))

ROWS = [
    ("public_ip", "🌐", "Public IP"),
    ("local_ip", "🖥", "Local IP"),
    ("country", "🏴", "Country"),
    ("city", "📍", "City / Region"),
    ("isp", "📡", "ISP"),
    ("org", "🏢", "Organization"),
    ("timezone", "🕐", "Timezone"),
    ("coords", "🗺", "Coordinates"),
]

value_widgets = {}
scroll = ctk.CTkScrollableFrame(window, fg_color="transparent")
scroll.pack(fill="both", expand=True, padx=14, pady=8)

for key, icon, label in ROWS:
    card = ctk.CTkFrame(scroll, fg_color="#161b22", corner_radius=10)
    card.pack(fill="x", pady=4)
    card.columnconfigure(1, weight=1)

    ctk.CTkLabel(card, text=icon, font=ctk.CTkFont(size=18), width=36).grid(
        row=0, column=0, rowspan=2, padx=(12, 6), pady=12
    )
    ctk.CTkLabel(card, text=label, font=ctk.CTkFont(size=11), text_color="#8b949e", anchor="w").grid(
        row=0, column=1, sticky="sw", padx=4, pady=(10, 0)
    )
    val = ctk.CTkLabel(card, text="—", font=ctk.CTkFont(size=14, weight="bold"), anchor="w")
    val.grid(row=1, column=1, sticky="nw", padx=4, pady=(0, 10))
    value_widgets[key] = val

btn_frame = ctk.CTkFrame(window, fg_color="transparent")
btn_frame.pack(fill="x", padx=14, pady=(4, 14))
btn_frame.columnconfigure(0, weight=1)
btn_frame.columnconfigure(1, weight=1)

lookup_btn = ctk.CTkButton(btn_frame, text="⟳  Lookup", command=lookup, height=40)
lookup_btn.grid(row=0, column=0, padx=(0, 6), sticky="ew")

copy_btn = ctk.CTkButton(
    btn_frame, text="⎘  Copy Public IP", command=copy_public,
    state="disabled", height=40, fg_color="#1f6feb", hover_color="#388bfd"
)
copy_btn.grid(row=0, column=1, padx=(6, 0), sticky="ew")

window.mainloop()
