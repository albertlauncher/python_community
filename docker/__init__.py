"""
Manage your docker containers
"""

from albertv0 import *
import os


__iid__ = "PythonInterface/v0.2"
__prettyname__ = "docker"
__version__ = "1.0"
__trigger__ = "d "
__author__ = "subutux <subutux@gmail.com>"
__dependencies__ = []

error = None

try:
    import docker
except ImportError:
    error = [Item(id="docker-error",
                  text="Please install docker python module",
                  subtext="pip3 install --user docker")]

conn = None
icon_up = "%s/%s.png" % (os.path.dirname(__file__), "docker-up")
icon_down = "%s/%s.png" % (os.path.dirname(__file__), "docker-down")


def buildItem(container, actions=[]):
    text = container.name
    subtext = container.image.attrs['RepoTags'][0]
    cid = container.id
    if container.status == "running":
        iconPath = icon_up
    else:
        iconPath = icon_down
    if not actions:
        if container.status == 'running':
            actions = [FuncAction("Stop", lambda i=cid: stop(i))]
        else:
            actions = [FuncAction("Start", lambda i=cid: start(i))]
    return Item(
        id=cid,
        text=text,
        subtext=subtext,
        icon=iconPath,
        completion=text,
        actions=actions
    )


def stop(containerId):
    global conn
    container = conn.containers.get(containerId)
    container.stop()


def start(containerId):
    global conn
    container = conn.containers.get(containerId)
    container.start()


def initialize():
    global conn
    conn = docker.from_env()


def Filter(name, containers):
    if not name:
        return [buildItem(con) for con in containers]
    name = name.upper()
    return [buildItem(con)
            for con in containers
            if name in con.name.upper()]


def handleQuery(query):
    global conn
    if query.isValid and query.isTriggered:
        if error:
            return error
        return Filter(query.string, conn.containers.list(all=True))

