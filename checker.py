#!/usr/bin/env python3
import os
import sys
import subprocess
from subprocess import PIPE


POINTS_PER_TEST = 5
SRCFILE = "main.py"
TESTDIR = "tests"
POINTS_FOR_PARSE = 0.5
POINTS_FOR_TDA = 1.0
POINTS_FOR_RAW = 1.5
TEST_TIMEOUT = 8  # seconds

# [(regex, in-file, ref-file)]
TESTS = [
    ("a", "test1"),
    ("ab", "test1"),
    ("a|b", "test1"),
    (".", "test1"),
    ("a?b", "test1"),
    ("ab*", "test1"),
    ("ab+", "test1"),
    ("(a)", "test1"),
    ("a{4}", "test1"),
    ("a{,4}", "test1"),
    ("a{4,}", "test1"),
    ("a{1,4}", "test1"),
    ("[abc]", "test1"),
    ("[0-9]", "test1"),
    ("[O-Y]", "test1"),
    ("[abc0-9]", "test1"),
    ("[0-9abc]", "test1"),
    ("[A-Z0-9]", "test1"),
    ("[A-Zabc0-9]", "test1"),
    ("[aA-Zb0-9c]", "test1"),
    ("aa|ca", "test1"),
    ("(a|c)a", "test1"),
    ("a(a|c)a", "test1"),
    ("a|b*", "test1"),
    ("(aa)a", "test1"),
    ("a(aa)", "test1"),
    ("(a*)*", "test1"),
    ("(a+)*", "test1"),
    ("(a?)*", "test1"),
    ("(a*)+", "test1"),
    ("(a+)+", "test1"),
    ("(a?)+", "test1"),
    ("(a*)?", "test1"),
    ("(a+)?", "test1"),
    ("(a?)?", "test1"),
    ("(aa)*", "test1"),
    ("(a|b)*", "test1"),
    ("(aa|ab)*", "test1"),
    ("(0|a)(aa(b|a))+", "test1"),
    ("a{4}", "test1"),
    ("a{,4}", "test1"),
    ("a{4,}", "test1"),
    ("a{1,4}", "test1"),
    ("[A-Z]*", "test2"),
    ("[a-z]*", "test2"),
    ("[0-9]*", "test2"),
]


def run_test(method, i, test):
    regex, in_name = test
    infile = os.path.join(TESTDIR, "in", in_name)
    outfile = os.path.join(TESTDIR, "out", "out_{}".format(i))
    reffile = os.path.join(TESTDIR, "ref", "ref_{}".format(i))
    tdafile = os.path.join(TESTDIR, "tda", "tda_{}".format(i))
    strfile = os.path.join(TESTDIR, "str", "str_{}".format(i))

    if method == "PARSE":
        with open(strfile, "r") as fin:
            refcont = fin.read()

        cmd = "python3 '{}' '{}' '{}'".format(SRCFILE, method, regex)
    else:
        with open(reffile, "rb") as fin:
            refcont = fin.read().decode("utf-8")

        if method == "RAW":
            cmd = "python3 '{}' '{}' '{}' '{}'".format(SRCFILE, method, regex,
                                                       infile)
        else:
            cmd = "python3 '{}' '{}' '{}' '{}'".format(SRCFILE, method,
                                                   tdafile, infile)

    timeout_cmd = "timeout -k {0} {0} {1}".format(TEST_TIMEOUT, cmd)
    cp = subprocess.run(timeout_cmd, shell=True, stdout=PIPE, stderr=PIPE)
    if cp.returncode == 124:
        return 0

    with open(outfile, "wb") as fout:
        fout.write(cp.stdout)

    outcont = cp.stdout.decode("utf-8")

    def normalize(s):
        return s.strip()

    return normalize(outcont) == normalize(refcont)


def run_all_tests(method, passed_tests=set()):
    total = 0
    nr_tests = len(TESTS)
    max_points = nr_tests * POINTS_PER_TEST

    header = " Running {} tests: ".format(method)
    print("{:=^65}".format(header))
    print("{} {: >40} {: >8} {: >8}\n".format("TEST #", "",
                                              "STATUS", "POINTS"))

    for i, test in enumerate(TESTS):
        status = (i in passed_tests) or run_test(method, i + 1, test)
        if status:
            passed_tests.add(i)

        crt_points = POINTS_PER_TEST if status else 0
        total += crt_points
        str_status = "PASSED" if status else "FAILED"
        str_points = "[{}/{}]".format(crt_points, POINTS_PER_TEST)
        print("{: >6} {:.>40} {: >8} {: >8}".format(i + 1, "", str_status,
                                                    str_points))

    print("\nTOTAL: {}/{}\n".format(total, max_points))
    return total / max_points, passed_tests


if __name__ == "__main__":
    if not (os.path.isfile(SRCFILE) and os.access(SRCFILE, os.R_OK)):
        sys.stderr.write("{} unavailable or unreadable!\n".format(SRCFILE))
        sys.exit(1)

    raw_total, passed_tests = run_all_tests("RAW")
    pp_raw = raw_total * POINTS_FOR_RAW

    parse_total, _ = run_all_tests("PARSE", passed_tests.copy())
    pp_parse = parse_total * POINTS_FOR_PARSE

    tda_total, _ = run_all_tests("TDA", passed_tests.copy())
    pp_tda = tda_total * POINTS_FOR_TDA

    grand_total = max(pp_raw, pp_tda + pp_parse)
    print("Punctaj din teste: {:.2f}".format(grand_total))
