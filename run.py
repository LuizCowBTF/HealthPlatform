#!/usr/bin/env python3
# run.py - Ponto de entrada principal
import sys
from pathlib import Path

# Adicionar ao path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "app" / "backend" / "src"))

from app.backend.src.main import app
import uvicorn

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🏥 HEALTH PLATFORM - INICIANDO SISTEMA")
    print("=" * 60)
    
    uvicorn.run(
        "app.backend.src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )