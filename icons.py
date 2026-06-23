"""Inline SVG icons (Feather-style) and a helper to render them as QIcons."""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPainter, QPixmap
from PyQt5.QtSvg import QSvgRenderer

_SVG = {
    "folder": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="2" '
        'stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>'
        '</svg>'
    ),
    "arrow_right": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="2.4" '
        'stroke-linecap="round" stroke-linejoin="round">'
        '<line x1="5" y1="12" x2="19" y2="12"/>'
        '<polyline points="13 6 19 12 13 18"/>'
        '</svg>'
    ),
    "play": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
        'fill="currentColor" stroke="currentColor" stroke-width="1" '
        'stroke-linejoin="round">'
        '<polygon points="7 5 19 12 7 19 7 5"/>'
        '</svg>'
    ),
    "file": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="2" '
        'stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>'
        '<polyline points="14 2 14 8 20 8"/>'
        '</svg>'
    ),
    "globe": (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="2" '
        'stroke-linecap="round" stroke-linejoin="round">'
        '<circle cx="12" cy="12" r="10"/>'
        '<line x1="2" y1="12" x2="22" y2="12"/>'
        '<path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>'
        '</svg>'
    ),
}


def make_icon(name: str, color: str, size: int = 18) -> QIcon:
    """Render an SVG icon from :data:`_SVG` into a :class:`QIcon`."""
    svg = _SVG.get(name, "")
    if not svg:
        return QIcon()
    svg = svg.replace("currentColor", color)
    renderer = QSvgRenderer(svg.encode("utf-8"))
    pixmap = QPixmap(size * 2, size * 2)  # 2x for HiDPI sharpness
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing, True)
    painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
    renderer.render(painter)
    painter.end()
    icon = QIcon()
    icon.addPixmap(pixmap)
    return icon
