COMFYUI_SERVERS = [
    "https://soundtrack-tip-clients-poll.trycloudflare.com",
    "https://relationship-peoples-fork-singh.trycloudflare.com",
    "https://married-soundtrack-blair-venture.trycloudflare.com"
]

def get_server_by_index(idx: int) -> str:
    return COMFYUI_SERVERS[idx % len(COMFYUI_SERVERS)]
def get_first_server():
    return COMFYUI_SERVERS[0]
