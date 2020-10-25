import os


def integration():
    os.environ['PYTEST_ADDOPTS']="--reruns 3 --reruns-delay 1"
    os.system("pytest integration-tests/test_http.py integration-tests/test_207.py")


def benchmark():
    print("\n\n\n\n----------------\n\n\n\n")


def doctest():
    print("\n\n\n\n----------------\n\n\n\n")
