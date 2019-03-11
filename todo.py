"""
Manage your todo.txt
"""

import subprocess as sp
from albertv0 import *
import os


__iid__ = "PythonInterface/v0.2"
__prettyname__ = "todo.txt"
__version__ = "1.0"
__trigger__ = "t "
__author__ = "subutux <subutux@gmail.com>"
__dependencies__ = []

error = None
actions = ['add', 'prio']

try:
    import todotxtio
except ImportError:
    error = [Item(id="todotxt-error",
                  text="Please install todotxtio python module",
                  subtext="pip3 install --user todotxtio")]

todo_path = os.path.expanduser("~/.todo/todo.txt")

iconPath = iconLookup('accessories-text-editor')


def buildItem(todo, actions=[]):
    text = todo.text
    if todo.priority:
        text = '(' + todo.priority + ') ' + text
    if todo.completed:
        text = '✔️' + text
    subtext = ''
    if todo.contexts:
        subtext = subtext + 'Contexts: ' + ','.join(
            [f"{p}" for p in todo.contexts]
        )
    if todo.projects:
        subtext = subtext + ' Projects: ' + ','.join(
            [f"{p}" for p in todo.projects]
        )
    for k in todo.tags:
        subtext = subtext + ' ' + k + ': ' + todo.tags[k]
    return Item(
        id=f'todo-{text}',
        text=text,
        subtext=subtext,
        icon=iconPath,
        completion=text,
        actions=actions
    )


def buildNewItem(todo):
    return buildItem(todo, [FuncAction("Save", lambda t=todo: Save(t))])


def toDone(task):
    todos = todotxtio.from_file(todo_path)
    newtodos = list()
    print(task)
    for todo in todos:
        print(todo.__repr__(), task.__repr__())
        if todo.__repr__() == task.__repr__():
            todo.completed = True
        newtodos.append(todo)
    todotxtio.to_file(todo_path, newtodos)


def toPrio(task, p):
    todos = todotxtio.from_file(todo_path)
    newtodos = list()
    print(task)
    for todo in todos:
        print(todo.__repr__(), task.__repr__())
        if todo.__repr__() == task.__repr__():
            todo.priority = p
        newtodos.append(todo)
    todotxtio.to_file(todo_path, newtodos)


def Save(task):
    todos = todotxtio.from_file(todo_path)
    todos.append(task)
    todotxtio.to_file(todo_path, todos)


def Del(task):
    todos = todotxtio.from_file(todo_path)
    newtodos = list()
    for todo in todos:
        print(todo.__repr__(), task.__repr__())
        if todo.__repr__() != task.__repr__():
            newtodos.append(todo)
    todotxtio.to_file(todo_path, newtodos)


def Filter(q):
    todos = todotxtio.from_file(todo_path)
    filtered = list()
    for todo in todos:
        if q.lower() in todo.__repr__().lower():
            filtered.append(todo)
    return filtered


def initialize():
    global todo_path
    SOURCE = '~/.todo/config'
    proc = sp.Popen(['bash', '-c', 'source {} && env'.format(SOURCE)],
                    stdout=sp.PIPE)

    source_env = {
        tup[0].strip(): tup[1].strip() for tup in map(
            lambda s: s.decode("utf-8").strip().split('=', 1),
            proc.stdout.readlines())}
    if 'TODO_DIR' in source_env:
        todo_path = source_env["TODO_DIR"] + "/todo.txt"


def handleQuery(query):
    if query.isValid and query.isTriggered:
        if error:
            return error
        if not query.string:
            todos = todotxtio.from_file(todo_path)
            return [
                buildItem(
                    todo,
                    actions=[FuncAction("Done", lambda t=todo: toDone(t)),
                             FuncAction("Delete", lambda t=todo: Del(t))]
                ) for todo in todos]
        else:
            tokens = query.string.split()
            if tokens[0] not in actions:
                return [
                    buildItem(
                        todo,
                        actions=[FuncAction("Done", lambda t=todo: toDone(t)),
                                 FuncAction("Delete", lambda t=todo: Del(t))]
                    ) for todo in Filter(query.string)]
            if tokens[0] == "add":
                del tokens[0]
                if not tokens:
                    return [Item(text="Add a task", icon=iconPath)]
                else:
                    txt = ' '.join(tokens)
                    return [buildNewItem(todotxtio.from_string(txt)[0])]

            elif tokens[0] == "prio":
                del tokens[0]
                if not tokens:
                    return [
                        Item(text="Set the priority of a task", icon=iconPath)
                    ]
                elif len(tokens[0]) == 1 and 90 >= ord(tokens[0]) >= 65:
                    prio = tokens[0]
                    del tokens[0]
                    q = ' '.join(tokens)
                    return [
                        buildItem(
                            t,
                            actions=[
                                FuncAction(f"Set Prio to {prio}",
                                           lambda t=t: toPrio(t, prio))
                            ]
                        ) for t in Filter(q)
                    ]

