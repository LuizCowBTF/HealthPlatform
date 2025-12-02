import sys
from pathlib import Path

print("=" * 70)
print("🔍 ESTRUTURA REAL DO SEU PROJETO")
print("=" * 70)

PROJECT = Path(__file__).parent
FRONTEND = PROJECT / "app" / "frontend"

print(f"📁 Projeto: {PROJECT}")
print(f"📁 Frontend: {FRONTEND}")

if not FRONTEND.exists():
    print("❌ Frontend não existe!")
    sys.exit(1)

print("\n📂 ESTRUTURA COMPLETA DO frontend/:")
for item in FRONTEND.iterdir():
    if item.is_dir():
        print(f"\n📁 {item.name}/")
        for subitem in item.iterdir():
            if subitem.is_dir():
                print(f"   └─ 📁 {subitem.name}/")
            else:
                print(f"   └─ 📄 {subitem.name}")
    else:
        print(f"📄 {item.name}")

print("\n" + "=" * 70)
print("🎯 VERIFICAÇÃO DE PASTAS CRÍTICAS:")
print("=" * 70)

# Pastas críticas
critical_folders = [
    ("dashboards", FRONTEND / "dashboards"),
    ("pges", FRONTEND / "pges"),
    ("pages", FRONTEND / "pages"),  # Verificar se existe com 'a'
    ("css", FRONTEND / "css"),
    ("js", FRONTEND / "js"),
    ("img", FRONTEND / "img")
]

found_folders = []
for name, path in critical_folders:
    exists = path.exists()
    status = "✅" if exists else "❌"
    print(f"{status} {name}: {path}")
    if exists:
        found_folders.append((name, path))

print("\n" + "=" * 70)
print("📋 RESUMO PARA CONFIGURAÇÃO DO main.py:")
print("=" * 70)

if len(found_folders) > 0:
    print("📝 Adicione ao main.py estas linhas:")
    print()
    for name, path in found_folders:
        mount_name = name if name != "pges" else "pages"
        print(f"app.mount('/{mount_name}', StaticFiles(directory='{path}'), name='{name}')")
else:
    print("⚠️ Nenhuma pasta encontrada - algo está errado")

print("\n" + "=" * 70)