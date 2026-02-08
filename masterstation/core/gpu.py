import os

def get_gpu_stats():
    gpu = {"name": "Intel Arc A770", "vram_used": 0,
           "vram_total": 0, "detected": False, "error": ""}

    for card in ["card0", "card1", "card2"]:
        base = f"/sys/class/drm/{card}/device"
        try:
            if os.path.exists(f"{base}/mem_info_vram_total"):
                with open(f"{base}/mem_info_vram_total") as f:
                    gpu["vram_total"] = int(f.read().strip()) // (1024**2)
                with open(f"{base}/mem_info_vram_used") as f:
                    gpu["vram_used"] = int(f.read().strip()) // (1024**2)
                gpu["detected"] = True
                break
        except PermissionError:
            gpu["error"] = "Permission denied for GPU metrics."
    return gpu
