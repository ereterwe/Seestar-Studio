"""Interactive local-time resource timeline. No network or execution adapter."""
from .i18n import source as ui_text, tr
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from PySide6.QtCore import Qt, QRectF, Signal, QDate
from .i18n import locale
from .telemetry import number
from PySide6.QtGui import QPainter, QColor, QPen, QImage
from PySide6.QtWidgets import QWidget, QMenu, QToolTip
from .timezones import local_text

SOLAR_LABELS = {'sunrise': ui_text('solar.sunrise'), 'sunset': ui_text('solar.sunset'),
                'night_start': ui_text('solar.night_start'), 'night_end': ui_text('solar.night_end')}

class Timeline(QWidget):
    changed = Signal(str, str, int)
    edit_requested = Signal(str)
    delete_requested = Signal(str)
    duplicate_requested = Signal(str)

    def __init__(self):
        super().__init__()
        self.rows = []; self.targets = {}
        self.devices = {}
        self.zone = 'UTC'
        self.setup = 5
        self.base = datetime.now(timezone.utc).replace(hour=12, minute=0, second=0, microsecond=0)
        self.end = self.base + timedelta(days=1)
        self.pixels_hour = 70
        self.selected = None
        self.drag = None
        self.preview_x = None
        self.rects = {}
        self.solar = None
        self.solar_image = QImage()
        self.event_rects = []
        self.setMouseTracking(True)
        self.resize_timeline()

    def set_rows(self, rows, devices=None, zone=None, base=None, setup=None):
        self.rows = rows
        if devices is not None:
            self.devices = devices
        if zone:
            self.zone = zone
        if setup is not None:
            self.setup = setup
        if base:
            local = base.astimezone(ZoneInfo(self.zone))
            day = (local - timedelta(days=1)).date() if local.hour < 12 else local.date()
            self.base = datetime.combine(day, datetime.min.time(), ZoneInfo(self.zone)).replace(hour=12).astimezone(timezone.utc)
            self.end = datetime.combine(day + timedelta(days=1), datetime.min.time(), ZoneInfo(self.zone)).replace(hour=12).astimezone(timezone.utc)
            # Imported/fixed observations may span several nights. Cover every
            # block, using real local noons (23/25-hour nights remain intact).
            if rows:
                first = min(self.base, min(r.start for r in rows)).astimezone(ZoneInfo(self.zone))
                first_day = first.date() - timedelta(days=1 if first.hour < 12 else 0)
                self.base = datetime.combine(first_day, datetime.min.time(), ZoneInfo(self.zone)).replace(hour=12).astimezone(timezone.utc)
                last = max(self.end, max(r.end for r in rows)).astimezone(ZoneInfo(self.zone))
                noon = last.replace(hour=12, minute=0, second=0, microsecond=0)
                if last > noon: noon += timedelta(days=1)
                self.end = noon.astimezone(timezone.utc)
        self.resize_timeline()
        self.update()

    def device_ids(self):
        return list(dict.fromkeys([*self.devices, *(r.entry.telescope for r in self.rows)]))

    def resize_timeline(self):
        self.setMinimumSize(int(190 + (self.end - self.base).total_seconds() / 3600 * self.pixels_hour), max(300, 130 + len(self.device_ids()) * 100))

    def x(self, value):
        return 180 + (value - self.base).total_seconds() / 3600 * self.pixels_hour

    def rectangle(self, row):
        return QRectF(self.x(row.start), 105 + self.device_ids().index(row.entry.telescope) * 100, (row.end - row.start).total_seconds() / 3600 * self.pixels_hour, 60)

    def set_solar(self, profile):
        if profile is self.solar: return
        self.solar = profile
        self.solar_image = (QImage(profile.colors, len(profile.times), 1, len(profile.times)*4,
                           QImage.Format.Format_RGBA8888).copy() if profile else QImage())
        self.update()

    def paint_solar(self, p):
        self.event_rects = []
        if not self.solar or self.solar.start != self.base or self.solar.end != self.end:
            return
        p.save()
        p.setClipRect(QRectF(self.x(self.base), 62, self.x(self.end)-self.x(self.base), self.height()-62))
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        # Pixel centres correspond to sampled instants, including both endpoints.
        half = (self.x(self.end)-self.x(self.base))/(len(self.solar.times)-1)/2
        p.drawImage(QRectF(self.x(self.base)-half, 62, self.x(self.end)-self.x(self.base)+2*half, self.height()-62), self.solar_image)
        p.restore()

    def paint_solar_events(self, p, clip):
        if not self.solar or self.solar.start != self.base or self.solar.end != self.end: return
        right_edges = [-float('inf'), -float('inf')]
        for event in self.solar.events:
            x = self.x(event.time)
            if event.kind not in ('sunrise', 'sunset', 'night_start', 'night_end'): continue
            title = tr(SOLAR_LABELS[event.kind]) + ' ' + local_text(event.time, self.zone)
            self.event_rects.append((x, title))
            if x < clip.left()-250 or x > clip.right()+250: continue
            p.setPen(QPen(QColor('#a2aabb'), 1, Qt.PenStyle.DashLine))
            p.drawLine(int(x), 62, int(x), self.height())
            short = tr(SOLAR_LABELS[event.kind])+' '+event.time.astimezone(ZoneInfo(self.zone)).strftime('%H:%M')
            width = p.fontMetrics().horizontalAdvance(short)+8
            left = max(180., min(x+4, self.x(self.end)-width))
            lane = next((i for i,right in enumerate(right_edges) if left > right+6), None)
            if lane is not None:
                rect = QRectF(left, 63+lane*18, width, 17)
                p.fillRect(rect, QColor('#101923'))
                p.setPen(QColor('#e4e9ee'))
                p.drawText(rect.adjusted(4,0,-4,0), Qt.AlignmentFlag.AlignVCenter, short)
                right_edges[lane] = rect.right()

    def zoom(self, factor):
        self.pixels_hour = min(600, max(30, self.pixels_hour * factor))
        self.resize_timeline()
        self.update()

    def wheelEvent(self, event):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.zoom(1.2 if event.angleDelta().y() > 0 else 1 / 1.2)
            event.accept()
        else:
            event.ignore()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.fillRect(self.rect(), QColor('#111a24'))
        for i, device in enumerate(self.device_ids()):
            y = 105 + i * 100
            p.fillRect(QRectF(0, y - 6, self.width(), 88), QColor('#162330' if i % 2 == 0 else '#131e29'))
            p.setPen(QColor('#cedae7'))
            p.drawText(QRectF(6, y, 166, 60), Qt.AlignmentFlag.AlignVCenter | Qt.TextFlag.TextWordWrap, tr(self.devices.get(device, device)))
        self.paint_solar(p)
        t = self.base
        while t <= self.end:
            x = self.x(t)
            local = t.astimezone(ZoneInfo(self.zone))
            p.setPen(QColor('#42576b' if local.hour == 0 else '#26394b'))
            p.drawLine(int(x), 50, int(x), self.height())
            p.setPen(QColor('#a9bdcf'))
            from .i18n import LANGUAGE
            date_text=locale().toString(QDate(local.year,local.month,local.day),'dd.MM.' if LANGUAGE=='de' else 'MMM d')
            p.drawText(QRectF(x + 3, 2, self.pixels_hour - 3, 60), Qt.TextFlag.TextWordWrap, date_text+'\n'+local.strftime('%H:%M\n%z'))
            t += timedelta(hours=1)
        self.paint_solar_events(p, event.rect())
        self.rects = {}
        for row in self.rows:
            if self.drag and row.entry.id == self.drag[0].entry.id and (self.preview_x is not None):
                start, minutes = self.proposed(self.preview_x)
                row = replace(row, entry=replace(row.entry, minutes=minutes), start=start, end=start + timedelta(minutes=minutes))
            rect = self.rectangle(row)
            self.rects[row.entry.id] = rect
            transition = QRectF(rect.right(), rect.top() + 10, self.setup / 60 * self.pixels_hour, 40)
            p.fillRect(transition, QColor('#4a5265'))
            conflict = any((ui_text('m0427') in s for s in row.issues))
            unknown = any((ui_text('m0243') in s or ui_text('m0244') in s for s in row.issues))
            color = '#8a3449' if conflict else '#354960' if unknown else '#67502e' if row.issues else '#1d6251'
            p.setBrush(QColor(color))
            p.setPen(QPen(QColor('#ffffff' if row.entry.id == self.selected else '#587389'), 2 if row.entry.id == self.selected else 1))
            p.drawRoundedRect(rect, 4, 4)
            p.save()
            p.setClipRect(rect.adjusted(3, 2, -3, -2))
            p.setPen(QColor('#edf5ff'))
            status=ui_text('timeline.conflict') if conflict else ui_text('timeline.unknown') if unknown else ui_text('timeline.unfavorable') if row.issues else ui_text('timeline.checked')
            lines = [tr(self.targets.get(row.entry.target, row.entry.target)),
                     f'{row.start.astimezone(ZoneInfo(self.zone)):%H:%M}–{row.end.astimezone(ZoneInfo(self.zone)):%H:%M}',
                     f'{row.entry.minutes} min · {tr(status)}']
            for index, text in enumerate(lines):
                shortened = p.fontMetrics().elidedText(text, Qt.TextElideMode.ElideRight, max(0, int(rect.width()-14)))
                p.drawText(QRectF(rect.left()+7, rect.top()+3+index*18, rect.width()-14, 18), Qt.AlignmentFlag.AlignVCenter, shortened)
            p.restore()
            p.setPen(QColor('#a9bdcf'))
            p.drawLine(int(rect.right() - 5), int(rect.top() + 18), int(rect.right() - 5), int(rect.bottom() - 18))
        now = datetime.now(timezone.utc)
        if self.base <= now <= self.end:
            p.setPen(QPen(QColor('#f2b467'), 2))
            p.drawLine(int(self.x(now)), 45, int(self.x(now)), self.height())

    def hit(self, point):
        return next((r for r in reversed(self.rows) if self.rectangle(r).contains(point)), None)

    def mousePressEvent(self, event):
        row = self.hit(event.position())
        if row and event.button() == Qt.MouseButton.LeftButton:
            self.selected = row.entry.id
            self.drag = (row, event.position().x(), abs(self.rectangle(row).right() - event.position().x()) < 10)
            self.preview_x = event.position().x()
            self.update()
            event.accept()
        else:
            super().mousePressEvent(event)

    def proposed(self, x):
        row, origin, resize = self.drag
        if abs(x-origin)<3:return row.start,row.entry.minutes
        minutes = round((x - origin) / self.pixels_hour * 60 / 5) * 5
        if resize:
            return (row.start, max(5, min(720, round((row.entry.minutes + minutes)/5)*5)))
        proposed=row.start + timedelta(minutes=minutes)
        snapped=datetime.fromtimestamp(round(proposed.timestamp()/300)*300,timezone.utc)
        return (snapped, row.entry.minutes)

    def mouseMoveEvent(self, event):
        if self.drag:
            self.preview_x = event.position().x()
            self.update()
            start, minutes = self.proposed(event.position().x())
            QToolTip.showText(event.globalPosition().toPoint(), f'{local_text(start, self.zone)} · {minutes} min', self)
            return
        row = self.hit(event.position())
        if row:
            details = row.astronomy
            text = f'{row.entry.target}\n{local_text(row.start, self.zone)} — {local_text(row.end, self.zone)}\n{row.entry.minutes} min\n' + ('; '.join(row.issues) or ui_text('m0242'))
            if details:
                text += f"\nAlt {number(details['altitude'], '°', 1)} · Az {number(details['azimuth'], '°', 1)}"
                for key in ('rise', 'set'):
                    title = ui_text('timeline.rise') if key == 'rise' else ui_text('timeline.set')
                    text += '\n' + tr(title) + ': ' + ', '.join((local_text(datetime.fromisoformat(t), self.zone) for t in details[key]))
            self.setToolTip(tr(text))
            self.setCursor(Qt.CursorShape.SizeHorCursor if abs(self.rectangle(row).right() - event.position().x()) < 10 else Qt.CursorShape.OpenHandCursor)
        else:
            self.setToolTip(next((text for x,text in self.event_rects if abs(event.position().x()-x)<6), ''))
            self.unsetCursor()

    def mouseReleaseEvent(self, event):
        if self.drag:
            row = self.drag[0]
            start, minutes = self.proposed(event.position().x())
            self.drag = None
            self.changed.emit(row.entry.id, start.isoformat(), minutes)
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        row = self.hit(event.position())
        self.drag = None
        if row:
            self.selected = row.entry.id
            self.edit_requested.emit(row.entry.id)

    def contextMenuEvent(self, event):
        row = self.hit(event.pos())
        if not row:
            return
        self.selected = row.entry.id
        menu = QMenu(self)
        edit = menu.addAction(tr(ui_text('m0157')))
        duplicate = menu.addAction(tr(ui_text('m0240')))
        delete = menu.addAction(tr(ui_text('m0241')))
        action = menu.exec(event.globalPos())
        if action == edit:
            self.edit_requested.emit(row.entry.id)
        elif action == duplicate:
            self.duplicate_requested.emit(row.entry.id)
        elif action == delete:
            self.delete_requested.emit(row.entry.id)
