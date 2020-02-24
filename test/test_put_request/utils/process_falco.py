import traceback


def reload_falco():
    """
    重启falco
    """
    res = False
    try:
        # logger.info("reloadFalco ...")
        print("reloadFalco")
        client = docker.DockerClient(base_url='unix://var/run/docker.sock')
        logger.info("get Falco container ...")
        conlist = client.containers.list()
        falco = None
        for f in conlist:
            if f.name.find('falco') != -1:
                falco = f
                # logger.info('find falco %s', f.name)
                break
        if falco is None:
            # logger.error("can't find falco")
            return res

        # logger.info("sigal SIGHUP to falco ...")
        falco.kill("SIGHUP")
        # logger.info("sigal SIGHUP to falco [OK]")
        client.close()
        res = True
    except Exception as e:
        # logger.error("%s %s ", e, traceback.format_exc())
        print("%s %s ", e, traceback.format_exc())
    return res