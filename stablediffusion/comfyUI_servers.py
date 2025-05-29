COMFYUI_SERVERS = [
    "https://impaired-americas-suspected-shannon.trycloudflare.com",
    "https://autos-usa-biggest-again.trycloudflare.com",
    "https://moisture-follow-halo-intelligent.trycloudflare.com"
]

def get_server_by_index(idx) -> str:
    idx = int(idx) 
    return COMFYUI_SERVERS[idx % len(COMFYUI_SERVERS)]

def get_first_server():
    return COMFYUI_SERVERS[0]
