import os
from uuid import uuid4
import subprocess

def is_travis_secure_vars_available():
    if os.environ['TRAVIS_SECURE_ENV_VARS']:
        return 0
    else:
        print("[WARNING] TRAVIS_SECURE_ENV_VARS={} (but should be true)".format(os.environ['TRAVIS_SECURE_ENV_VARS']))
        return 1


def benchmark():
    if not is_travis_secure_vars_available:
        return 0
    os.environ['PYTEST_ADDOPTS'] = "--reruns 3 --reruns-delay 1"
    SO_S3_URL = os.environ['SO_S3_URL'] + uuid4()

    commit_hash = subprocess.run(['git', 'rev-parse', 'HEAD'], stdout=subprocess.PIPE)
    os.system("pytest integration-tests/test_s3.py --benchmark-save={}".format(commit_hash))

    os.system("aws s3 cp .benchmarks/*/*.json s3://{0}/{1}".format(os.environ['SO_BUCKET'],os.environ['SO_RESULT_KEY']))

def integration():
    os.environ['PYTEST_ADDOPTS']="--reruns 3 --reruns-delay 1"
    os.system("pytest integration-tests/test_http.py integration-tests/test_207.py")
    if is_travis_secure_vars_available():
        return 0
    os.system("pytest integration-tests/test_s3_ported.py")


def dependencies():
    pass


def doctest():
    if is_travis_secure_vars_available():
        return 0

    os.system("python -m doctest README.rst -v;")

def enable_moto_server():
    pass
    #os.system(" moto_server -p5000 2>/dev/null&") #!!!!!!!!!!!!!!!!!!!!!

def disable_moto_server():
    pass