COMFYUI_SERVERS = [
    "https://tables-pavilion-rise-hall.trycloudflare.com",
    "https://jenny-adjustments-cc-lions.trycloudflare.com",
    "https://wilson-pages-local-testimony.trycloudflare.com"
]

def get_server_by_index(idx) -> str:
    idx = int(idx) 
    return COMFYUI_SERVERS[idx % len(COMFYUI_SERVERS)]

def get_first_server():
    return COMFYUI_SERVERS[0]
