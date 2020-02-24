import traceback


def write_versionfile(ver):
    """
    写入版本信息
    """
    try:
        with open("vers.txt", "wb") as fd:
            fd.write(ver)
    except Exception as e:
        print("%s %s", e, traceback)
        # logger.error("%s %s", e, traceback)