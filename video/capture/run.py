"""Yakalama giriş noktası. Her sahne ayrı süreçte, kendi temiz verisiyle çekilir.

Kullanım:  python video/capture/run.py [--scene fikir_proje]
"""
from __future__ import annotations

import argparse
import logging
import os
import shutil
import subprocess
import sys
import tempfile
import traceback
from collections.abc import Callable
from datetime import date
from pathlib import Path
from typing import Any

VIDEO_DIR = Path(__file__).resolve().parents[1]
FRAMES_DIR = VIDEO_DIR / "frames"
logger = logging.getLogger("demo.capture")


def capture_scene(scene_id: str, out_dir: Path) -> int:
    """Uygulamayı geçici verilerle açar ve tek sahneyi kaydeder."""
    import isolation

    workdir = Path(tempfile.mkdtemp(prefix=f"demo_{scene_id}_"))
    # Qt bu değişkenleri QApplication kurulurken bir kez okur.
    os.environ.update(QT_SCALE_FACTOR="3", QSG_RENDER_LOOP="basic", QSG_FIXED_ANIMATION_STEP="yes")
    isolation.prepare(workdir)
    try:
        return _run_app(scene_id, out_dir)
    finally:
        logging.shutdown()
        shutil.rmtree(workdir, ignore_errors=True)


def _run_app(scene_id: str, out_dir: Path) -> int:
    import seed

    import main_qml
    from app.di_container import DIContainer

    container = DIContainer.instance()
    container.bootstrap()
    seed.seed_database(container.services, container.db, date.today())
    failed = _hook_director(lambda: _record(scene_id, out_dir))
    code = int(main_qml.run_qml_app())
    container.db.engine.dispose()  # Açık SQLite bağlantısı geçici klasörün silinmesini engeller.
    if failed:
        sys.stderr.write(failed[0])
        return 1
    return code


def _hook_director(action: Callable[[], None]) -> list[str]:
    """Uygulama kodunu değiştirmeden, kurulum bittikten sonra `action` çalıştırır.

    Dönen liste, `action` hata verirse hata dökümünü taşır.
    """
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication

    original_exec = QApplication.exec
    failed: list[str] = []

    def direct() -> None:
        try:
            action()
        except Exception:  # Qt geri çağrısından istisna sızarsa süreç başarılı görünür.
            failed.append(traceback.format_exc())
        finally:
            QApplication.quit()

    def patched_exec() -> int:
        QTimer.singleShot(1000, direct)
        return int(original_exec())

    QApplication.exec = staticmethod(patched_exec)  # type: ignore[method-assign]  # PySide imzası statik
    return failed


def _record(scene_id: str, out_dir: Path) -> None:
    from driver import Driver
    from PySide6.QtQuick import QQuickWindow
    from PySide6.QtWidgets import QApplication
    from recorder import Recorder
    from scenes import SCENES

    app: Any = QApplication.instance()  # Köprü nesneleri main_qml içinde uygulamaya iliştirilir.
    window = next(w for w in app.topLevelWindows() if isinstance(w, QQuickWindow))
    recorder = Recorder(window, out_dir, scene_id)
    recorder.pin_window()
    driver = Driver(recorder)
    _keep_toasts(app, driver.toast())
    recorder.settle(10)
    app._nav_bridge.setSidebarCollapsed(False)  # Küçük mantıksal ekran çubuğu daraltıyor.
    recorder.settle()
    try:
        SCENES[scene_id](driver, app)
    finally:
        recorder.close()
    logger.info("%s: %d kare", scene_id, recorder.frame_count)


def _keep_toasts(app: Any, toast: Any) -> None:
    """Bildirim gerçek saatle gizlenir; kare kare çekim yavaş olduğundan videoda erken kaybolur.

    Süre uzatılır; sahne gerektiğinde `Driver.dismiss_toast` ile kapatır.
    """
    # QML bağlantısı önce kurulduğu için bu çağrı onun ayarladığı süreyi ezer.
    app._nav_bridge.toastRequested.connect(lambda *_: toast.setProperty("duration", 600_000))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scene")
    parser.add_argument("--out", type=Path, default=FRAMES_DIR)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(name)s %(message)s")
    sys.path.insert(0, str(Path(__file__).parent))

    if args.scene:
        return capture_scene(args.scene, args.out)

    from scenes import SCENES

    for scene_id in SCENES:
        command = [sys.executable, __file__, "--scene", scene_id, "--out", str(args.out)]
        if subprocess.run(command, check=False).returncode != 0:
            logger.error("Sahne başarısız: %s", scene_id)
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
