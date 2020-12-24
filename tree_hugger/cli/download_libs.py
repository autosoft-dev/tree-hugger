from argparse import ArgumentParser
import logging
import requests
from tree_hugger.exceptions import OSNotSupported
import tree_hugger.setup_logging
from tree_hugger.cli.os_detector import _which_os

ALLOWED_OS = ["linux", "darwin", "windows"]
ALLOWED_OS_HUMAN_READABLE = {"linux": "Linux", "darwin": "MacOS", "windows":"Windows"}

is_in_allowed_os = lambda x: x in ALLOWED_OS

LIB_NAME = {"linux": "py_php_js_cpp_java_linux_64.so",
            "darwin": "py_php_js_cpp_java_darwin_64.so",
            "windows":"py_php_js_cpp_java_windows_32.dll"}

BASE_URL = "https://tree-hugger-libs.s3.amazonaws.com/"


def _download_lib_to_local(os_type, local_file_name):
    url = f"{BASE_URL}{LIB_NAME[os_type]}"

    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        block_size = 1024 #1 Kbyte
        with open(local_file_name, 'wb') as f:
            for chunk in r.iter_content(block_size):
                f.write(chunk)
    return True


def main():
    paser = ArgumentParser()
    paser.add_argument("--local_file_name", type=str, default="my-languages.so",
                       help="The local file where you want to save the library. Default - my-languages.so")

    args = paser.parse_args()

    if _which_os()=="windows":
        args.local_file_name = args.local_file_name.split(".")[0] + ".dll"

    logging.info(f"Downloading .{args.local_file_name.split('.')[1]} files for '{ALLOWED_OS_HUMAN_READABLE[_which_os()]}' version")
    _download_lib_to_local(_which_os(), args.local_file_name)
    logging.info(f".{args.local_file_name.split('.')[1]} library saved to {args.local_file_name}.")
