from pathlib import Path
import ctypes
import json
import os
import shutil
import socket
import subprocess
import sys
import threading
import time
from unittest.mock import patch
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from markdown_mermaid_tool import app_server
from markdown_mermaid_tool.build_info import BUILD_LABEL, BUILD_DATETIME, BUILD_VERSION


def check_http(url):
    with urlopen(url + '/api/build-info', timeout=5) as response:
        info = json.load(response)
    assert info == {'label': BUILD_LABEL, 'version': BUILD_VERSION, 'built': BUILD_DATETIME}
    with urlopen(url, timeout=5) as response:
        assert 'id="buildIdentity"' in response.read().decode()
    with urlopen(url + '/static/app.js', timeout=5) as response:
        assert '/api/build-info' in response.read().decode()
    return info


if __name__ == '__main__':
    with patch.object(app_server, 'runtime_base_dir', return_value=ROOT):
        context = app_server.AppContext()
    server = app_server._bind_server('127.0.0.1', 0, app_server._make_handler(context))
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    try:
        url = f'http://127.0.0.1:{server.server_port}'
        check_http(url)
        chrome = Path(os.environ['PROGRAMFILES']) / 'Google/Chrome/Application/chrome.exe'
        rendered = subprocess.run([str(chrome), '--headless=new', '--disable-gpu', '--no-first-run',
            '--disable-background-networking', '--disable-sync', '--disable-extensions',
            '--user-data-dir=' + str(ROOT / 'chrome-profile'), '--window-size=1180,850',
            '--virtual-time-budget=3000', '--screenshot=' + str(ROOT / 'header.png'), '--dump-dom', url],
            capture_output=True, text=True, encoding='utf-8', timeout=30)
        assert rendered.returncode == 0
        assert BUILD_LABEL in rendered.stdout
        assert (ROOT / 'header.png').is_file()
    finally:
        server.shutdown(); server.server_close(); worker.join(5)
    if os.environ.get('DISPLAY_PACKAGED_EXE'):
        source = Path(os.environ['DISPLAY_PACKAGED_EXE'])
        target = ROOT / 'build' / source.name
        target.parent.mkdir(exist_ok=True)
        shutil.copy2(source, target)
        with socket.socket() as reservation:
            reservation.bind(('127.0.0.1', 0)); port = reservation.getsockname()[1]
        process = subprocess.Popen([str(target), '--no-open', '--port', str(port)], cwd=ROOT,
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                   creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            deadline = time.monotonic() + 40
            while True:
                try:
                    check_http(f'http://127.0.0.1:{port}'); break
                except OSError:
                    assert process.poll() is None
                    if time.monotonic() > deadline: raise
                    time.sleep(.1)
            version = ctypes.WinDLL('version', use_last_error=True)
            size = version.GetFileVersionInfoSizeW(str(target), None)
            buffer = ctypes.create_string_buffer(size)
            assert version.GetFileVersionInfoW(str(target), 0, size, buffer)
            for key, expected in [('FileVersion', BUILD_VERSION), ('BuildDateTime', BUILD_DATETIME)]:
                pointer = ctypes.c_void_p(); count = ctypes.c_uint()
                assert version.VerQueryValueW(buffer, '\\StringFileInfo\\040904B0\\' + key, ctypes.byref(pointer), ctypes.byref(count))
                assert ctypes.wstring_at(pointer) == expected
        finally:
            if process.poll() is None:
                subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'], capture_output=True, check=False)
            process.wait(timeout=10)
    print('PASS: source HTTP, real browser build label, packaged identity/resources/HTTP when requested')
