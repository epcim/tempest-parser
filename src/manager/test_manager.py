import src.manager.structs as structs
import os
import time
from copy import deepcopy


class TestsManager:
    def __init__(self):
        # structure
        self.tests_list = deepcopy(structs._tests_template)
        self.required_execution_name = "required"

    def add_required(self, all_tests_filepath, path=None):
        # on init we should either load the full set of tests
        # ... or load supplied ones
        _tests_list_filename = os.path.join("res", all_tests_filepath)
        _date = time.strftime("%d/%m/%Y %H:%M", time.gmtime(
            os.path.getctime(_tests_list_filename)))

        if path is not None and not os.path.isfile(path):
            # if this is a folder, load files into sections
            self.tests_list["tests"] = self._load_from_folder(path)
        elif path is not None and os.path.isfile(path):
            # if file, load contents to just one section
            self.tests_list["tests"] = self._all_tests_file_preload(path)
        elif path is None:
            # if there is no tests supplied, use save all tests set
            # self.all_tests_list = read_file_as_lines(path)

            self.tests_list["tests"] = self._all_tests_file_preload(
                _tests_list_filename)
        self.add_execution(
            dict(execution_name=self.required_execution_name,
                 execution_date=_date, summary=dict(time="0s")))

    def _load_from_folder(self, folder):
        _tests = {}

        _folder_content = os.listdir(folder)

        for _file in _folder_content:
            _tests_in_file = {}
            # check extension
            if _file.endswith(".list"):
                _tests_in_file = self._all_tests_file_preload(
                    os.path.join(
                        folder,
                        _file
                    )
                )
            _tests = dict(_tests.items() + _tests_in_file.items())

        return _tests

    # In case we'll need to list all of the tests in tempest and mark which ones was executed,
    # we have this list of all tests
    # It produced by ./run_tempest.sh -- --list >tests.list
    def _all_tests_file_preload(self, resource_file):
        _tests = {}

        # load all tests file
        with open(resource_file) as tests_file:
            for line in tests_file:
                _search_res = line.partition('[')

                _class_name, _test_name, _test_options = self.split_test_name(
                    line.replace("\n", ""))

                self._test_item = deepcopy(structs._template_test_item)
                self._test_item["test_name"] = _test_name
                self._test_item["set_name"] = _search_res[1].replace("\n", "") + \
                    _search_res[2].partition(']')[0].replace("\n", "") + "]"
                self._test_item["results"][
                    self.required_execution_name] = dict(result="R", time='0s')

                self._test_item["test_options"] = _test_options

                if _class_name not in _tests:
                    _tests[_class_name] = []
                _tests[_class_name].append(self._test_item)
        return _tests

    @staticmethod
    def split_test_name(full_test_name):
        if full_test_name.startswith("setUpClass") or \
                full_test_name.startswith("tearDownClass"):
            return (
                full_test_name.split(" ")[0],
                full_test_name.split("(")[1][:-1],
                ""
            )

        elif full_test_name.startswith("tempest."):
            _class = full_test_name.rsplit(".", 1)[0]
            _test = full_test_name.rsplit(".", 1)[1].split('[')[0]
            _tmp = full_test_name.rsplit(".", 1)[1].split(']')
            _options = ""
            if _tmp.__len__() >= 2:
                if _tmp[1].__len__() > 0:
                    _options = _tmp[1]
            return (
                _class,
                _test,
                _options
            )
        return None, None, None

    @staticmethod
    def split_test_name_from_speed(full_test_name):
        _class = full_test_name.rsplit(".", 2)[0]
        _test = full_test_name.rsplit(".", 2)[1].split('[')[0]
        _tmp = full_test_name.split(" ")[0].rsplit(".", 1)[1].split(']')
        _options = ""
        if _tmp.__len__() >= 2:
            if _tmp[1].__len__() > 0:
                _options = _tmp[1]
        return (
            _class,
            _test,
            _options
        )

    def test_name_lookup(self, class_name, test_name, set_name, test_options):
        _index = -1
        _tests = self.tests_list["tests"]

        if class_name in _tests:
            for _test_index in range(0, _tests[class_name].__len__()):
                if _tests[class_name][_test_index]["test_name"] == test_name \
                        and _tests[class_name][_test_index]["test_options"] == test_options:
                    if set_name == '' or _tests[class_name][_test_index]["set_name"] == '':
                        _index = _test_index
                        break
                    elif _tests[class_name][_test_index]["set_name"] == set_name:
                        _index = _test_index
                        break

        return _index

    def test_name_lookup_bare(self, class_name, test_name):
        _index = -1
        _tests = self.tests_list["tests"]

        if class_name in _tests:
            for _test_index in range(0, _tests[class_name].__len__()):
                if _tests[class_name][_test_index]["test_name"] == test_name:
                    _index = _test_index
                    break

        return _index

    def partial_class_name_lookup(self, class_name_short, test_name, set_name=None, test_options=None):
        _list = []
        _full_class_name = ""
        _class_names = self.tests_list["tests"].keys()
        for _class_name in _class_names:
            if _class_name.endswith(class_name_short):
                _index = self.test_name_lookup(_class_name, test_name, set_name, test_options)
                if _index > -1:
                    _full_class_name = _class_name
                    _list.append(_full_class_name)
        if _list.__len__() > 0:
            return _list[0]
        else:
            return None

    def add_execution(self, _execution):
        # time = float(_execution["summary"]["time"][:-1])
        date = _execution["execution_date"]
        _name = _execution["execution_name"]
        self.tests_list["executions"][_name] = date

    def mark_slowest_test_in_execution_by_name(self, execution_name,
                                               class_name, test_name, set_name=None,
                                               test_options=None):
        _index = self.test_name_lookup(class_name, test_name, set_name, test_options)
        if _index > -1:
            # mark slowest tests
            self.tests_list["tests"][class_name][_index]["results"][
                execution_name]["slowest"] = True
        else:
            print(
                "WARNING: Parsed slowest test not found in list: {0}, {1}, {2}".format(
                    execution_name,
                    class_name,
                    test_name
                ))

    def add_fail_data_for_test(self, execution_name, class_name, test_name,
                               test_options, trace, message,
                               class_name_short=False, set_name=None):
        if class_name == "setUpClass" or \
                        class_name == "tearDownClass":
            # if this is a setUpClass situation, mark all tests with this result
            _tests = self.tests_list["tests"]
            if test_name in _tests:
                for _test_index in range(0, _tests[test_name].__len__()):
                    _tests[test_name][_test_index]["results"][execution_name][
                        "trace"] = trace
                    _tests[test_name][_test_index]["results"][execution_name][
                        "message"] = message
                    break
        else:
            # lookup test in the list
            if class_name_short:
                _full_class_name = self.partial_class_name_lookup(class_name,
                                                                  test_name)
                if _full_class_name is None:
                    _full_class_name = class_name
            else:
                _full_class_name = class_name
            _index = self.test_name_lookup(
                _full_class_name,
                test_name,
                set_name,
                test_options
            )
            if _index > -1:
                # this matches one already in the list, copy
                self.tests_list["tests"][_full_class_name][_index]["results"][
                    execution_name]["trace"] = trace
                self.tests_list["tests"][_full_class_name][_index]["results"][
                    execution_name]["message"] = message
            else:
                print("WARNING: Test NOT found: {0}, {1}\nfor message: {2}".format(
                    _full_class_name,
                    test_name,
                    message
                ))

    def add_result_for_test(self, execution_name, class_name, test_name, tags,
                            test_options, result, running_time,
                            message='', trace='', class_name_short=False, test_name_bare=False):
        _result = deepcopy(structs._template_test_result)
        _result["result"] = result
        _result["time"] = running_time
        _result["message"] = message
        _result["trace"] = trace
        if class_name == "setUpClass" or class_name == "tearDownClass":
            # if this is a setUpClass situation,
            # mark all tests with this result
            _tests = self.tests_list["tests"]

            if test_name in _tests:
                for _test_index in range(0, _tests[test_name].__len__()):
                    _result["setup_fail"] = True
                    _tests[test_name][_test_index]["results"][
                        execution_name] = _result
                    break
        else:
            # if this is a normal class and test name -> look it up
            # lookup test in the list
            if class_name_short:
                _full_class_name = self.partial_class_name_lookup(class_name,
                                                                  test_name)
                if _full_class_name is None:
                    _full_class_name = class_name
            else:
                _full_class_name = class_name
            if test_name_bare:
                _index = self.test_name_lookup_bare(
                    _full_class_name,
                    test_name
                )
            else:
                _index = self.test_name_lookup(
                    _full_class_name,
                    test_name,
                    tags,
                    test_options
                )
            if _index > -1:
                # this matches one already in the list, copy

                self.tests_list["tests"][_full_class_name][_index]["results"][
                    execution_name] = _result
                pass
            else:
                # the test is not there, add it
                _test_item = deepcopy(structs._template_test_item)
                _test_item["test_name"] = test_name
                _test_item["results"][execution_name] = _result

                if _full_class_name not in self.tests_list["tests"]:
                    # there is no class name key, add it
                    self.tests_list["tests"][_full_class_name] = []
                self.tests_list["tests"][_full_class_name].append(_test_item)

    def get_tests_for_class(self, class_name):
        if class_name in self.tests_list["tests"]:
            return self.tests_list["tests"][class_name]
        else:
            return []

    def get_tests_list(self):
        return self.tests_list

    def is_class_has_errors(self, class_name):
        if class_name in self.tests_list["tests"]:
            for test in self.tests_list["tests"][class_name]:
                _executions = test["results"].keys()
                for _execution in _executions:
                    if test["results"][_execution]["result"] == "FAIL":
                        return True
        else:
            return False

    def is_test_has_errors(self, class_name, test_name):
        if class_name in self.tests_list["tests"]:
            for test in self.tests_list["tests"][class_name]:
                _executions = test["results"].keys()
                for _execution in _executions:
                    if test["results"][_execution]["result"] == "FAIL":
                        return True
        else:
            return False

    def get_executions(self):
        return self.tests_list["executions"].keys()

    def get_test_classes(self):
        return self.tests_list["tests"].keys()

    def get_time_for_class(self, class_name):
        _time_str = ""
        _executions = self.tests_list["executions"].keys()
        if class_name in self.tests_list["tests"]:
            for _execution in _executions:
                running_time = 0
                for test in self.tests_list["tests"][class_name]:
                    if _execution in test["results"]:
                        if test["results"][_execution]["time"].__len__() > 0:
                            running_time += float(
                                test["results"][_execution]["time"][:-1])
                _time_str += "{0}s ".format(running_time)
        return _time_str

    def get_totals_as_string_for_class(self, class_name):
        _totals_str = ""
        _executions = self.tests_list["executions"].keys()
        if class_name in self.tests_list["tests"]:
            for _execution in _executions:
                total = 0
                fail = 0
                for test in self.tests_list["tests"][class_name]:
                    if _execution in test["results"]:
                        if test["results"][_execution]["result"] == "FAIL":
                            fail += 1
                        total += 1
                _totals_str += "{0}/{1}, ".format(total, fail)
        return _totals_str

    def get_summary_for_execution(self, execution_name):
        # calculate summary
        running_time = 0
        total = 0
        ok = 0
        fail = 0
        skip = 0

        _classes = self.tests_list["tests"].keys()
        for _class in _classes:
            for test in self.tests_list["tests"][_class]:
                if execution_name in test["results"]:
                    total += 1
                    if test["results"][execution_name]["time"].__len__() > 0:
                        running_time += float(
                            test["results"][execution_name]["time"][:-1])
                    if test["results"][execution_name]["result"] == "OK":
                        ok += 1
                    elif test["results"][execution_name]["result"] == "FAIL":
                        fail += 1
                    elif test["results"][execution_name]["result"] == "SKIP":
                        skip += 1

        return running_time, total, ok, fail, skip

    def print_summary_for_execution(self, _execution_name):
        # throw a quick summary
        running_time, total, ok, fail, skip = self.get_summary_for_execution(
            _execution_name)

        print(
            "Tempest testrun {0}: {1} executed: {2} passed, {3} failed, {4} skipped\n".format(
                _execution_name,
                total,
                ok,
                fail,
                skip
            )
        )
