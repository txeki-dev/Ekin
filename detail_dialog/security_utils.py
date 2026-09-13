"""Utilidades de seguridad para la validación y apertura segura de hipervínculos
y rutas locales en Ekin (prevención de ejecución de código arbitrario y fugas UNC)."""
import os
import re
from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QMessageBox
from PySide6.QtGui import QDesktopServices
from strings import t

_WEB_LINK_SCHEMES = ("http://", "https://", "ftp://", "mailto:", "file://")

_SAFE_WEB_SCHEMES = ("http", "https", "mailto", "ftp")

_SCHEME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")
_DRIVE_RE = re.compile(r"^[a-zA-Z]:[\\/]")

_DANGEROUS_EXTENSIONS = {
    # Binarios y ejecutables de Windows
    ".exe", ".msi", ".msp", ".com", ".scr", ".pif", ".cpl", ".msc",
    # Scripts e intérpretes de comandos
    ".bat", ".cmd", ".ps1", ".psm1", ".psd1", ".vbs", ".vbe", ".js", ".jse",
    ".wsf", ".wsh", ".hta", ".reg",
    # Shells y binarios Unix
    ".sh", ".bash", ".zsh", ".csh", ".bin",
    # Accesos directos y enlaces de ejecución
    ".lnk", ".url", ".inf", ".application", ".gadget",
    # Scripts interpretados con asociación directa en el SO
    ".py", ".pyw", ".jar",
}


def _is_local_link(url: str) -> bool:
    """True si la cadena representa una ruta de archivo local o de red (UNC / relativa / absoluta),
    y False si contiene un esquema de protocolo URI (p. ej. http, https, file, mailto, calc, powershell)."""
    if not url:
        return False
    clean = url.strip()
    if not clean:
        return False
    if _DRIVE_RE.match(clean):
        return True
    if clean.startswith(("/", "\\\\", "//")):
        return True
    if _SCHEME_RE.match(clean):
        return False
    return True


def _is_unc_path(url: str) -> bool:
    r"""True if url targets a network share (UNC path, e.g. \\server\share or //server/share)."""
    if not url:
        return False
    clean = url.strip()
    if clean.startswith(("\\\\", "//")):
        return True
    if clean.lower().startswith("file:"):
        qu = QUrl(clean)
        if qu.isLocalFile() and qu.toLocalFile().startswith(("//", "\\\\")):
            return True
        host = qu.host()
        if host and host.lower() not in ("localhost", "127.0.0.1"):
            return True
    return False


def _get_target_extension(url: str) -> str:
    """Extracts the lowercased file extension from a local path or file URL."""
    clean = url.strip()
    if clean.lower().startswith("file:"):
        qu = QUrl(clean)
        path = qu.toLocalFile() or qu.path()
    else:
        path = clean.split("?")[0].split("#")[0]
    normalized = path.rstrip(". ")
    _, ext = os.path.splitext(normalized)
    return ext.lower()


def confirm_open_untrusted_link(parent, url: str, is_local: bool = None) -> bool:
    """Verifica si el enlace apunta a un recurso compartido UNC, script/ejecutable potencialmente
    peligroso o esquema de URL inseguro, solicitando confirmación explícita al usuario."""
    clean = url.strip()
    if is_local is None or (is_local and _SCHEME_RE.match(clean) and not _DRIVE_RE.match(clean) and not clean.lower().startswith("file:")):
        is_local = _is_local_link(clean)

    is_unc = _is_unc_path(clean)
    is_file_or_local = is_local or clean.lower().startswith("file:")

    ext = ""
    if is_file_or_local:
        ext = _get_target_extension(clean)

    is_executable = ext in _DANGEROUS_EXTENSIONS

    is_unsafe_scheme = False
    scheme = ""
    if not is_file_or_local and not is_unc:
        qu = QUrl(clean)
        scheme = qu.scheme().lower()
        if scheme and scheme not in _SAFE_WEB_SCHEMES:
            is_unsafe_scheme = True

    if not (is_unc or is_executable or is_unsafe_scheme):
        return True

    if is_unc and is_executable:
        msg = t("task_detail.link_security_unc_executable_msg", target=clean, ext=ext)
    elif is_executable:
        msg = t("task_detail.link_security_executable_msg", target=clean, ext=ext)
    elif is_unc:
        msg = t("task_detail.link_security_unc_msg", target=clean)
    else:
        msg = t("task_detail.link_security_scheme_msg", target=clean, scheme=scheme)

    reply = QMessageBox.warning(
        parent,
        t("task_detail.link_security_title"),
        msg,
        QMessageBox.StandardButton.Open | QMessageBox.StandardButton.Cancel,
        QMessageBox.StandardButton.Cancel,
    )
    return reply == QMessageBox.StandardButton.Open


def open_link_safely(parent, url: str, is_local: bool = None) -> bool:
    """Abre de forma segura una URL o ruta local tras verificar su nivel de confianza.
    Muestra un diálogo de confirmación si el destino puede ejecutar código arbitrario o exponer UNC."""
    if not url:
        return False
    clean = url.strip()
    if is_local is None or (is_local and _SCHEME_RE.match(clean) and not _DRIVE_RE.match(clean) and not clean.lower().startswith("file:")):
        is_local = _is_local_link(clean)

    if not confirm_open_untrusted_link(parent, url, is_local):
        return False

    qurl = QUrl.fromLocalFile(url) if is_local else QUrl(url)
    res = QDesktopServices.openUrl(qurl)
    if res is False:
        QMessageBox.warning(
            parent, t("task_detail.link_open_failed_title"), t("task_detail.link_open_failed_msg")
        )
        return False
    return True
