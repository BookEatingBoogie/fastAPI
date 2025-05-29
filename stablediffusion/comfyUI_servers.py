COMFYUI_SERVERS = [
    "https://measures-hon-oem-focus.trycloudflare.com",
    "https://bed-totals-insight-abroad.trycloudflare.com",
    "https://ya-nottingham-airfare-db.trycloudflare.com"
]

def get_server_by_index(idx) -> str:
    idx = int(idx) 
    return COMFYUI_SERVERS[idx % len(COMFYUI_SERVERS)]

def get_first_server():
    return COMFYUI_SERVERS[0]
