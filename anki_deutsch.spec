# PyInstaller spec: builds a standalone "Anki Deutsch" app (macOS .app / Windows folder with .exe).
# Build with:  pyinstaller anki_deutsch.spec --noconfirm
import sys

from PyInstaller.utils.hooks import collect_all

datas, binaries, hiddenimports = [], [], []
for pkg in (
    "spacy", "de_core_news_sm", "thinc", "srsly", "blis", "cymem", "preshed",
    "murmurhash", "spacy_legacy", "spacy_loggers", "customtkinter", "edge_tts",
    "deep_translator", "certifi",
):
    d, b, h = collect_all(pkg)
    datas += d
    binaries += b
    hiddenimports += h

a = Analysis(
    ["run_app.py"],
    pathex=["."],
    datas=datas,
    binaries=binaries,
    hiddenimports=hiddenimports,
    excludes=["torch", "tensorflow", "matplotlib", "IPython", "pytest"],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Anki Deutsch",
    console=False,
    argv_emulation=False,
)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name="Anki Deutsch")

if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name="Anki Deutsch.app",
        bundle_identifier="local.anki-deutsch",
        info_plist={"NSHighResolutionCapable": True},
    )
