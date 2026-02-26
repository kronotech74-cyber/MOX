# MOX Browser — Guía de instalación y uso

## Estructura de archivos necesaria

```
mox_browser/
├── mox.py          ← Aplicación principal (este archivo)
└── mox.html        ← Tu interfaz HTML de MOX
```

---

## 1 · Requisitos del sistema

| Requisito | Versión mínima |
|-----------|---------------|
| Python    | **3.11+**     |
| pip       | Incluido con Python |

> ⚠️ **Windows**: Descarga Python desde [python.org](https://python.org). Durante la instalación marca **"Add Python to PATH"**.

---

## 2 · Instalar dependencias

Abre una terminal (CMD o PowerShell) **dentro de la carpeta `mox_browser/`** y ejecuta:

```bash
pip install PyQt6 PyQt6-WebEngine PyInstaller
```

Si tienes varios Python instalados, usa:

```bash
python -m pip install PyQt6 PyQt6-WebEngine PyInstaller
```

### Verificar instalación

```bash
python -c "from PyQt6.QtWebEngineWidgets import QWebEngineView; print('OK')"
```

Si imprime `OK`, está todo listo.

---

## 3 · Ejecutar en modo desarrollo

```bash
python mox.py
```

---

## 4 · Atajos de teclado

| Atajo            | Acción                      |
|------------------|-----------------------------|
| `Ctrl + T`       | Nueva pestaña               |
| `Ctrl + W`       | Cerrar pestaña activa       |
| `Ctrl + L`       | Enfocar barra de URL        |
| `Ctrl + H`       | Ir a inicio (mox.html)      |
| `Ctrl + R` / F5  | Recargar página             |
| `Alt + ←`        | Atrás                       |
| `Alt + →`        | Adelante                    |
| `Ctrl + Tab`     | Siguiente pestaña           |
| `Ctrl+Shift+Tab` | Pestaña anterior            |

---

## 5 · Lógica de navegación inteligente

La barra de búsqueda detecta automáticamente:

| Entrada del usuario     | Acción                              |
|------------------------|-------------------------------------|
| `youtube.com`           | → `https://youtube.com`             |
| `github.com/user/repo`  | → `https://github.com/user/repo`    |
| `https://ejemplo.com`   | → Navega directamente               |
| `inteligencia artificial` | → Busca en Google                |
| `clima en Madrid`       | → Busca en Google                   |

---

## 6 · Compilar a .exe con PyInstaller

### Comando básico (una sola carpeta)

```bash
pyinstaller --noconfirm --onedir --windowed ^
  --name "MOX Browser" ^
  --add-data "mox.html;." ^
  mox.py
```

> En **Mac/Linux** cambia `;` por `:`:
> ```bash
> pyinstaller --noconfirm --onedir --windowed \
>   --name "MOX Browser" \
>   --add-data "mox.html:." \
>   mox.py
> ```

### Comando avanzado (un solo .exe — más lento al arrancar)

```bash
pyinstaller --noconfirm --onefile --windowed ^
  --name "MOX" ^
  --add-data "mox.html;." ^
  mox.py
```

### Resultado

Después de compilar encontrarás el ejecutable en:

```
dist/
└── MOX Browser/        ← carpeta completa (compartir toda la carpeta)
    └── MOX Browser.exe ← ejecutable principal
```
o con `--onefile`:
```
dist/
└── MOX.exe             ← un solo archivo portable
```

---

## 7 · Agregar ícono personalizado (opcional)

1. Convierte tu logo a formato `.ico` (puedes usar [convertio.co](https://convertio.co)).
2. Colócalo como `mox_icon.ico` en la misma carpeta.
3. Agrega `--icon mox_icon.ico` al comando de PyInstaller.

```bash
pyinstaller --noconfirm --onedir --windowed ^
  --name "MOX Browser" ^
  --add-data "mox.html;." ^
  --icon mox_icon.ico ^
  mox.py
```

---

## 8 · Solución de problemas comunes

### Error: `No module named 'PyQt6'`
```bash
pip install PyQt6 PyQt6-WebEngine
```

### Error: `No module named 'PyQt6.QtWebEngineWidgets'`
```bash
pip install PyQt6-WebEngine
```

### La app abre pero la página se ve en blanco
- Asegúrate de que `mox.html` está en la **misma carpeta** que `mox.py`.
- Si usaste `--onefile`, el HTML debe estar junto al `.exe` en la carpeta `dist/`.

### En Linux: error con sandbox de Chromium
Agrega esto antes de iniciar:
```bash
export QTWEBENGINE_CHROMIUM_FLAGS="--no-sandbox"
python mox.py
```

---

## 9 · Personalizar el motor de búsqueda

Abre `mox.py`, busca la función `smart_url` y cambia la URL de búsqueda:

```python
# Google (predeterminado)
return f'https://www.google.com/search?q={quote_plus(text)}'

# DuckDuckGo
return f'https://duckduckgo.com/?q={quote_plus(text)}'

# Bing
return f'https://www.bing.com/search?q={quote_plus(text)}'