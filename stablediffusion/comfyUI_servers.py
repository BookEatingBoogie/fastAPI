COMFYUI_SERVERS = [
    "https://vatican-royal-speaks-fog.trycloudflare.com",
    "https://olympics-june-glow-wheel.trycloudflare.com",
    "https://councils-tb-excited-diversity.trycloudflare.com"
]

def get_server_by_index(idx) -> str:
    idx = int(idx) 
    return COMFYUI_SERVERS[idx % len(COMFYUI_SERVERS)]

def get_first_server():
    return COMFYUI_SERVERS[0]
