#!/usr/bin/env fbpython
# (c) Meta Platforms, Inc. and affiliates. Confidential and proprietary.
import argparse
import os
import subprocess
import sys
import tempfile
from typing import Optional

PERFETTO_UI_ROOT_URL = (
    "https://interncache-all.fbcdn.net/manifold/perfetto-artifacts/tree/ui/index.html"
)
MANIFOLD_FOLDER = "perfetto_internal_traces/tree/shared_trace"
DEFAULT_TTL_SEC = 28 * 24 * 60 * 60


def upload_trace_file(local_path: str, overwrite: bool = False) -> Optional[str]:
    file_name = os.path.basename(local_path)
    manifold_path = os.path.join(MANIFOLD_FOLDER, f"{os.getlogin()}_{file_name}")
    cmd = [
        "manifold",
        "put",
        local_path,
        manifold_path,
        "--ttl",
        str(DEFAULT_TTL_SEC),
        "--userData",
        "false",
    ]
    ret = subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
    )
    if ret.returncode == 0:
        print("Upload trace successfully.")
        return manifold_path
    else:
        print("[ERROR] Upload failed, maybe the trace file exists.")
        return None


def print_perfetto_ui_url(manifold_path: str) -> None:
    url = (
        PERFETTO_UI_ROOT_URL
        + "#!/?url=https://interncache-all.fbcdn.net/manifold/"
        + manifold_path
    )
    print(f"The trace is accessible at: {url}")


def trace_handler(prof) -> None:
    with tempfile.NamedTemporaryFile() as f:
        prof.export_chrome_trace(f.name)
        manifold_path = upload_trace_file(f.name)
        if manifold_path:
            print_perfetto_ui_url(manifold_path)


def main(argv) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "local_path", help="The local path for the trace file to upload."
    )
    args = parser.parse_args()
    if not os.path.exists(args.local_path):
        print(f"[ERROR] The trace file doesn't exist: {args.local_path}")
        return 1
    manifold_path = upload_trace_file(args.local_path)
    if manifold_path:
        print_perfetto_ui_url(manifold_path)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
