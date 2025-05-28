COMFYUI_SERVERS = [
    "https://adrian-promises-eye-blame.trycloudflare.com",
    "https://lightbox-pounds-thumbnail-create.trycloudflare.com",
    "https://istanbul-wrong-looked-minnesota.trycloudflare.com"
]

def get_server_by_index(idx) -> str:
    idx = int(idx) 
    return COMFYUI_SERVERS[idx % len(COMFYUI_SERVERS)]

def get_first_server():
    return COMFYUI_SERVERS[0]
