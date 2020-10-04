from argparse import ArgumentParser
import platform
import logging

import requests

from tree_hugger.exceptions import OSNotSupported
import tree_hugger.setup_logging

ALLOWED_OS = ["linux", "darwin"]

is_in_allowed_os = lambda x: x in ALLOWED_OS

LIB_NAME = {"linux": "py_php_js_cpp_java_linux_64.so",
            "darwin": "py_php_js_cpp_java_darwin_64.so"}

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



def _which_os():
    return platform.system().lower()


def main():
    paser = ArgumentParser()
    paser.add_argument("--local_file_name", type=str, default="my-languages.so",
                       help="The local file where you want to save the library. Default - my-languages.so")

    args = paser.parse_args()

    if not is_in_allowed_os(_which_os()):
        raise OSNotSupported(f"Sorry! Your OS '{_which_os()}' is not supported yet.")

    logging.info(f"Downloading .so files for '{_which_os()}' version")
    _download_lib_to_local(_which_os(), args.local_file_name)
    logging.info(f".so library saved to {args.local_file_name}.")
