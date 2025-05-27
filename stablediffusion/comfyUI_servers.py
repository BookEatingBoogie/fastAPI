COMFYUI_SERVERS = [
    "https://additions-both-described-intended.trycloudflare.com",
    "https://ability-acres-donors-pictures.trycloudflare.com",
    "https://modes-letter-supporters-wires.trycloudflare.com"
]

def get_server_by_index(idx: int) -> str:
    return COMFYUI_SERVERS[idx % len(COMFYUI_SERVERS)]
def get_first_server():
    return COMFYUI_SERVERS[0]
