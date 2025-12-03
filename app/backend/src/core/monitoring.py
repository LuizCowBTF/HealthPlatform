from datetime import datetime
import psutil

class SystemMonitor:
    @staticmethod
    async def get_system_health():
        """Retorna saúde do sistema"""
        return {
            "timestamp": datetime.now().isoformat(),
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent,
            "uptime": datetime.now() - datetime.fromtimestamp(psutil.boot_time())
        }