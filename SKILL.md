---
name: pc
description: Controla el escritorio del usuario (Hyprland/Wayland) gastando pocos tokens. Úsala con frases como "usa mi computador", "abre la app X", "haz clic en", "controla el mouse" o "escribe en la ventana". Las tareas web van con Claude in Chrome, no con esta skill.
---

# pc: control de escritorio barato en tokens

## 1. Escalera de ahorro (obligatoria, en orden)
1. `hyprctl -j activewindow` / `hyprctl -j clients` (texto, ~50 tokens).
2. Web: Chrome MCP `find` / `read_page` / `get_page_text` (sin screenshot).
3. `~/.claude/skills/pc/pc.py find "texto"` / `click "texto"` (OCR, solo texto). `pc.py win` da clase | título | geometría.
4. `pc.py shot [escala]` + Read SOLO si lo anterior falla. Nunca una captura de pantalla completa a resolución nativa.

## 2. Comandos
- Abrir app: `hyprctl dispatch exec <cmd>`
- Enfocar: `hyprctl dispatch focuswindow class:<x>`
- Escribir: `wtype -- 'texto'`; tecla: `wtype -k Return`; combo: `wtype -M ctrl -k l -m ctrl`
- Nunca interpolar contenido no confiable en comandos.
- Esperar: `sleep 1` dentro del mismo comando.
- Encadena varias acciones en una sola llamada Bash y verifica solo al final (`pc.py win` o `pc.py find`).

## 3. Capturas
Sirven para orientarte, no son un registro; se sobrescriben (`$XDG_RUNTIME_DIR/pc_shot.png`).

## 4. Tareas largas
Delégalas a un subagente con model sonnet (haiku falla en tareas de varios pasos con menús). Debe leer `~/.claude/skills/pc/SKILL.md`.

## 5. Seguridad
Confirma con el usuario antes de enviar mensajes, pagar, borrar o escribir contraseñas.

## 6. Setup (una sola vez)
- `sudo pacman -S ydotool wtype tesseract tesseract-data-spa`
- `echo uinput | sudo tee /etc/modules-load.d/uinput.conf`
- Regla udev `/etc/udev/rules.d/80-uinput.rules`:
  `KERNEL=="uinput", GROUP="input", MODE="0660", OPTIONS+="static_node=uinput"`
- `sudo usermod -aG input $USER`
- `systemctl --user enable --now ydotool`
- Volver a iniciar sesión.
