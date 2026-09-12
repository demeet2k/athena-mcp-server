"""An owned database path with no competing open temporary-file handle."""
from pathlib import Path
import tempfile


class TemporaryDatabasePath:
    def __init__(self):
        self.directory = tempfile.TemporaryDirectory(prefix="athena-test-db-")
        self.name = str(Path(self.directory.name) / "state.db")

    def close(self):
        # Callers must close their SQLite connections first. Cleanup errors
        # intentionally expose leaked handles rather than hiding them.
        self.directory.cleanup()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
