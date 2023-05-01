import platform


def get_platform():
    return platform.platform()


def is_os_mac():
    if 'macos' in get_platform().lower():
        return True
    return False


def is_os_linux():
    if 'linux' in get_platform().lower():
        return True
    return False


