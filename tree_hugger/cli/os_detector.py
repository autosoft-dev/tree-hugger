import platform


def _which_os():
    return platform.system().lower()