import sublime
import sublime_plugin
import sys
import os
import base64
import json
import threading
import time
import ctypes


# need to dynamic later
package_path = sublime.packages_path()
cache_path = os.path.join(
    package_path, "Sublime_Teradata_Plugin", "metastore", "cache_query.json"
)
sys_path = f"{package_path}\\Sublime_Teradata_Plugin\\lib"
sys_path2 = f"{package_path}\\Sublime_Teradata_Plugin"


if sys_path not in sys.path:
    sys.path.append(sys_path)
    sys.path.append(sys_path2)

import pyodbc
from tabulate import tabulate
from connect import teradata_connect
import sqlparse


def get_connect():
    try:
        global conn
        conn = teradata_connect()
        print(f"Detected username and pw, Conn is set , {conn} ")

    finally:
        pass


def conn_timeout(t1, timeout):
    duration = 0
    while t1.is_alive() and duration < timeout:
        time.sleep(1)
        duration += 1
    if duration >= timeout:
        thread_id = t1.native_id
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
            thread_id, ctypes.py_object(SystemExit)
        )
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            print("Exception raise failure")
        print(f"Successfull stop thread {thread_id}")
        sublime.message_dialog(
            f"Connect to EDW timeout in {timeout} seconds, please check VPN and relaunch sublime"
        )


if os.getenv("TERADATAUSERNAMEENCODED") and os.getenv("TERADATAPWENCODED"):
    if "conn" in globals():
        pass
    else:
        t1 = threading.Thread(
            target=get_connect,
            name="sa_connect",
        )
        t2 = threading.Thread(
            target=conn_timeout,
            args=[t1, 15],
            name=f"sa_timeout_query",
        )
        t1.start()
        t2.start()


def load_cache_dict(cache_path):
    try:
        with open(cache_path, "r") as f:
            file = f.read()
    except FileNotFoundError:
        with open(cache_path, "w") as f:
            f.write("{}")
        with open(cache_path, "r") as f:
            file = f.read()
    return json.loads(file)


def add_result_to_cache(cache_dict, result, number_of_cache_query):
    if len(cache_dict) < number_of_cache_query:
        cache_dict.update(result)
        return cache_dict
    else:
        cache_dict.pop(list(cache_dict.keys())[0])
        cache_dict.update(result)
        return cache_dict


def stop_thread(t1):
    if isinstance(t1, int):
        thread_id = t1
    else:
        thread_id = t1.native_id
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
        thread_id, ctypes.py_object(SystemExit)
    )
    if res > 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
        print("Exception raise failure")
    print(f"Successfull stop thread {thread_id}")


class SaRunSqlCmd(sublime_plugin.WindowCommand):
    def run(self, limit, number_of_cache_query, timeout):
        def main_func(self, *args):
            try:
                view = self.window.active_view()
                # currently only takes single cursor query selection
                # conn = teradata_connect()
                print("conn is ", conn)
                cursor = view.sel()[0]
                a = cursor.begin()
                b = cursor.end()
                if a > b:
                    a, b = b, a
                query = view.substr(sublime.Region(a, b))
                query = query.replace(";", "")
                parsed = sqlparse.parse(query)[0]

                if limit:
                    has_limit = True
                else:
                    has_limit = False

                if "top" in query or "sample" in query:
                    has_sample = True
                else:
                    has_sample = False

                # create panel
                panel = self.window.create_output_panel("result")
                panel.set_read_only(False)
                panel.settings().set("word_wrap", False)

                # load cache query
                cache_dict = load_cache_dict(cache_path)
                result = cache_dict.get(query)
                if result is None:
                    is_not_cache = True
                else:
                    to_return = result
                    is_not_cache = False
                    panel.run_command("append", {"characters": f"{to_return}"})
                    panel.run_command(
                        "append",
                        {"characters": "\n\n\nReturn from Cache"},
                    )
                    panel.run_command(
                        "append",
                        {
                            "characters": f"\n{len(cache_dict)}/{number_of_cache_query}  (num of query in cache vs maxium cache)"
                        },
                    )

                # only execute when there is no cache
                if is_not_cache:
                    cursor = conn.cursor
                    start = time.time()
                    try:

                        cursor.execute(query)
                        dur = time.time() - start
                        print("query is ,", query)
                        has_exec_error = False
                    except Exception as e:
                        error = e
                        has_exec_error = True
                        print(error)

                    try:
                        if has_sample:
                            result = cursor.fetchall()
                        else:
                            result = cursor.fetchmany(limit)
                        has_return_msg = True
                    except:
                        dur = time.time() - start
                        if parsed.get_type() != "UNKNOWN":
                            if cursor.rowcount == -1:
                                to_return = f"Successfully run {parsed.get_type().lower()} statement in {round(dur,2)} seconds!"
                            else:
                                to_return = f"Successfully run {parsed.get_type().lower()} statement in {round(dur,2)} seconds!\n{cursor.rowcount} rows impacted "
                        else:
                            to_return = (
                                f"Successfully run statement in {round(dur,2)} seconds!"
                            )

                        has_return_msg = False

                    if not has_exec_error and has_return_msg:
                        cols = [row[0] for row in cursor.description]
                        to_return = tabulate(
                            result, cols, "psql", disable_numparse=True
                        )
                        # write to a cache file
                        new_cache = {query: to_return}
                        cache_dict = add_result_to_cache(
                            cache_dict, new_cache, number_of_cache_query
                        )
                        cache_dict_to_write = json.dumps(cache_dict)

                        with open(cache_path, "w") as f:
                            f.write(cache_dict_to_write)

                        panel.run_command("append", {"characters": f"{to_return}"})
                        panel.run_command(
                            "append",
                            {
                                "characters": f"\n\n\nActual Query retrieve time {round(dur,2)}"
                            },
                        )

                        if has_limit and not has_sample and len(result) == limit:
                            panel.run_command(
                                "append",
                                {
                                    "characters": f"\nOnly showed {limit} record, change this number in limit or explicitly pass sample number"
                                },
                            )

                    elif not has_exec_error and not has_return_msg:
                        panel.run_command("append", {"characters": f"{to_return}"})
                    elif has_exec_error:
                        # to_return = str(error) + "\n\n" + "Query Runned:\n" + query
                        to_return = str(error)
                        panel.run_command("append", {"characters": f"{to_return}"})

                panel.set_read_only(True)
                self.window.run_command("show_panel", {"panel": "output.result"})
            finally:
                pass

        def print_status_msg(self, t1, timeout):

            duration = 0
            while t1.is_alive() and duration < timeout:
                time.sleep(1)
                sublime.status_message(f"Executing SQL query for {duration} seconds...")
                duration += 1
            if duration >= timeout:
                stop_thread(t1)
                # sleep to wait until thread_active show as all stopped
                panel = self.window.create_output_panel("timeout")
                panel.set_read_only(False)
                panel.settings().set("word_wrap", False)
                # why this wierd threading._active.items() mark finished thread as unfinished?
                # All threads: {list(threading._active.items())}
                panel.run_command(
                    "insert",
                    {
                        "characters": f"Execution timeout after {timeout} seconds, thread_number {t1.native_id}.\nCheck VPN or increase timeout in key binding args for run_sql_cmd"
                    },
                )
                panel.set_read_only(True)
                self.window.run_command("show_panel", {"panel": "output.timeout"})

        if os.getenv("TERADATAUSERNAMEENCODED") and os.getenv("TERADATAPWENCODED"):
            t1 = threading.Thread(
                target=main_func,
                args=[self, limit, number_of_cache_query],
                name="sa_run_sql_cmd",
            )
            t2 = threading.Thread(
                target=print_status_msg,
                args=[self, t1, timeout],
                name=f"sa_timeout_query",
            )
            t1.start()
            t2.start()
        else:
            sublime.message_dialog(
                "Teradata username and password do not set\nHit [ctrl+m, ctrl+p] to set credential\nThen relaunch sublime!"
            )


class SaClearCache(sublime_plugin.TextCommand):
    def run(self, edit):
        os.remove(cache_path)
        print("removed cache json")


class SaInterruptQuery(sublime_plugin.WindowCommand):
    def run(self):
        all_thread = threading._active
        to_interrupt = []
        for tid, thread in all_thread.items():
            if (
                thread.name
                in [
                    "sa_run_sql_cmd",
                    "sa_timeout_query",
                    "meta_init",
                    "meta_timeout",
                    "meta_add",
                    "sa_connect",
                ]
                and thread.is_alive()
            ):
                to_interrupt.append(thread)
        if len(to_interrupt) == 0:
            return
        for thread in to_interrupt:
            stop_thread(thread)

        all_names = " , ".join(
            [f"{thread.name} {thread.native_id}" for thread in to_interrupt]
        )
        panel = self.window.create_output_panel("interrupt")
        panel.set_read_only(False)
        panel.settings().set("word_wrap", False)
        panel.run_command(
            "insert",
            {
                "characters": f"Successfully interrupt {all_names}\nAll thread: {list(threading._active.items())}"
            },
        )
        panel.set_read_only(True)
        self.window.run_command("show_panel", {"panel": "output.interrupt"})


class SaAddDotInWordSep(sublime_plugin.WindowCommand):
    def run(self):
        settings = sublime.load_settings("Preferences.sublime-settings")
        sep = settings.get("word_separators")

        if "." not in sep:
            sep = "." + sep
            settings.set("word_separators", sep)
            msg = "Add dot from word_separator"
        elif "." in sep:
            sep = sep.replace(".", "")
            settings.set("word_separators", sep)
            msg = "Remove dot from word_separator"

        sublime.save_settings("Preferences.sublime-settings")

        panel = self.window.create_output_panel("dot")
        panel.set_read_only(False)
        panel.settings().set("word_wrap", False)
        panel.run_command(
            "insert",
            {"characters": msg},
        )
        panel.set_read_only(True)
        self.window.run_command("show_panel", {"panel": "output.dot"})


class SaRestartConnection(sublime_plugin.TextCommand):
    def run(self, edit):
        conn1 = str(conn)
        self.conn1 = conn1

        conn.close()
        self.restart()

    def restart(self):
        global conn
        conn = teradata_connect()
        conn2 = str(conn)
        sublime.message_dialog("Restarted connection!")
        print("Before:", self.conn1, "\n", "After:", conn2)
