from __future__ import annotations

import ctypes
import time
from collections import deque
from ctypes import wintypes
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


FILE_LIST_DIRECTORY = 0x0001
FILE_SHARE_READ = 0x00000001
FILE_SHARE_WRITE = 0x00000002
FILE_SHARE_DELETE = 0x00000004
OPEN_EXISTING = 3
FILE_FLAG_BACKUP_SEMANTICS = 0x02000000
FILE_NOTIFY_CHANGE_FILE_NAME = 0x00000001
FILE_NOTIFY_CHANGE_DIR_NAME = 0x00000002
FILE_NOTIFY_CHANGE_ATTRIBUTES = 0x00000004
FILE_NOTIFY_CHANGE_SIZE = 0x00000008
FILE_NOTIFY_CHANGE_LAST_WRITE = 0x00000010
FILE_NOTIFY_CHANGE_CREATION = 0x00000040


ACTION_MAP = {
    1: "create",
    2: "delete",
    3: "modify",
    4: "rename_old",
    5: "move",
}


@dataclass(slots=True)
class WatchEvent:
    event_type: str
    source_path: str
    watch_fallback: bool = False


def _kernel32():
    return ctypes.windll.kernel32


def _open_directory(path: str):
    handle = _kernel32().CreateFileW(
        path,
        FILE_LIST_DIRECTORY,
        FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
        None,
        OPEN_EXISTING,
        FILE_FLAG_BACKUP_SEMANTICS,
        None,
    )
    if handle == wintypes.HANDLE(-1).value:
        raise OSError(f"could not watch directory: {path}")
    return handle


def _read_changes(handle, buffer_size: int = 65536) -> bytes:
    buffer = ctypes.create_string_buffer(buffer_size)
    bytes_returned = wintypes.DWORD()
    ok = _kernel32().ReadDirectoryChangesW(
        handle,
        ctypes.byref(buffer),
        buffer_size,
        True,
        FILE_NOTIFY_CHANGE_FILE_NAME
        | FILE_NOTIFY_CHANGE_DIR_NAME
        | FILE_NOTIFY_CHANGE_ATTRIBUTES
        | FILE_NOTIFY_CHANGE_SIZE
        | FILE_NOTIFY_CHANGE_LAST_WRITE
        | FILE_NOTIFY_CHANGE_CREATION,
        ctypes.byref(bytes_returned),
        None,
        None,
    )
    if not ok:
        raise OSError("ReadDirectoryChangesW failed")
    return buffer.raw[: bytes_returned.value]


def _parse_notifications(blob: bytes) -> list[tuple[int, str]]:
    notifications: list[tuple[int, str]] = []
    offset = 0
    while offset < len(blob):
        next_offset = int.from_bytes(blob[offset : offset + 4], "little")
        action = int.from_bytes(blob[offset + 4 : offset + 8], "little")
        name_len = int.from_bytes(blob[offset + 8 : offset + 12], "little")
        name = blob[offset + 12 : offset + 12 + name_len].decode("utf-16le", errors="ignore")
        notifications.append((action, name))
        if next_offset == 0:
            break
        offset += next_offset
    return notifications


def _snapshot(root: Path) -> dict[str, tuple[int, float]]:
    result: dict[str, tuple[int, float]] = {}
    for path in root.rglob("*"):
        if path.is_file():
            stat = path.stat()
            result[str(path)] = (stat.st_size, stat.st_mtime)
    return result


def _reconcile(previous: dict[str, tuple[int, float]], current: dict[str, tuple[int, float]]) -> list[WatchEvent]:
    events: list[WatchEvent] = []
    old_paths = set(previous)
    new_paths = set(current)
    for path in sorted(new_paths - old_paths):
        events.append(WatchEvent("create", path, True))
    for path in sorted(old_paths - new_paths):
        events.append(WatchEvent("delete", path, True))
    for path in sorted(old_paths & new_paths):
        if previous[path] != current[path]:
            events.append(WatchEvent("modify", path, True))
    return events


def _dedupe_signature(event: WatchEvent) -> str:
    return f"{event.event_type}|{event.source_path}"


def _is_probable_directory_event(path: str) -> bool:
    candidate = Path(path)
    if candidate.exists() and candidate.is_dir():
        return True
    return not candidate.suffix


def watch_loop(
    *,
    root: Path,
    dedupe_window_ms: int,
    reconcile_seconds: int,
    on_event: Callable[[WatchEvent], None],
) -> None:
    handle = _open_directory(str(root))
    recent: deque[tuple[float, str]] = deque()
    recent_by_path: dict[str, tuple[str, float]] = {}
    last_snapshot = _snapshot(root)
    last_reconcile = time.monotonic()
    pending_rename_old: str | None = None
    try:
        while True:
            blob = _read_changes(handle)
            for action, relative_name in _parse_notifications(blob):
                source_path = str(root / relative_name)
                event_type = ACTION_MAP.get(action, "modify")
                if event_type == "rename_old":
                    pending_rename_old = source_path
                    continue
                if event_type == "move" and pending_rename_old:
                    pending_rename_old = None
                event = WatchEvent(event_type, source_path, False)
                if _is_probable_directory_event(event.source_path):
                    continue
                now = time.monotonic()
                while recent and now - recent[0][0] > dedupe_window_ms / 1000.0:
                    recent.popleft()
                prior = recent_by_path.get(event.source_path)
                if prior:
                    prior_type, prior_ts = prior
                    if now - prior_ts <= dedupe_window_ms / 1000.0:
                        if event.event_type == "modify" and prior_type in {"create", "move"}:
                            continue
                        if event.event_type == prior_type:
                            continue
                signature = _dedupe_signature(event)
                if any(sig == signature for _, sig in recent):
                    continue
                recent.append((now, signature))
                recent_by_path[event.source_path] = (event.event_type, now)
                on_event(event)
            if time.monotonic() - last_reconcile >= reconcile_seconds:
                current_snapshot = _snapshot(root)
                for event in _reconcile(last_snapshot, current_snapshot):
                    if _is_probable_directory_event(event.source_path):
                        continue
                    signature = _dedupe_signature(event)
                    if any(sig == signature for _, sig in recent):
                        continue
                    now = time.monotonic()
                    prior = recent_by_path.get(event.source_path)
                    if prior:
                        prior_type, prior_ts = prior
                        if now - prior_ts <= dedupe_window_ms / 1000.0:
                            if event.event_type == "modify" and prior_type in {"create", "move"}:
                                continue
                            if event.event_type == prior_type:
                                continue
                    recent.append((now, signature))
                    recent_by_path[event.source_path] = (event.event_type, now)
                    on_event(event)
                last_snapshot = current_snapshot
                last_reconcile = time.monotonic()
    finally:
        _kernel32().CloseHandle(handle)
