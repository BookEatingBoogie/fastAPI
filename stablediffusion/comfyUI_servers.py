COMFYUI_SERVERS = [
    "https://retail-licenses-meanwhile-decrease.trycloudflare.com",
    "https://reef-adequate-smoking-phase.trycloudflare.com",
    "https://computer-share-th-occupied.trycloudflare.com"
]

def get_server_by_index(idx: int) -> str:
    return COMFYUI_SERVERS[idx % len(COMFYUI_SERVERS)]
def get_first_server():
    return COMFYUI_SERVERS[0]
