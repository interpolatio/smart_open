# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 Radim Rehurek <me@radimrehurek.com>
#
# This code is distributed under the terms and conditions
# from the MIT License (MIT).
#

from __future__ import unicode_literals
import io
import os
import subprocess
import uuid

import smart_open

_S3_BUCKET_NAME = os.environ.get('SO_BUCKET_NAME')
assert _S3_BUCKET_NAME is not None, 'please set the SO_BUCKET_NAME environment variable'

SO_KEY = os.environ.get('SO_KEY')
assert SO_KEY is not None, 'please set the SO_KEY environment variable'

_S3_URL = 's3://%s/%s' % (_S3_BUCKET_NAME, SO_KEY)



def initialize_bucket():
    subprocess.check_call(['aws', 's3', 'rm', '--recursive', _S3_URL])
    key = 's3://%s/%s/%s' % (_S3_BUCKET_NAME, SO_KEY, 'test-write-key-{}'.format(uuid.uuid4().hex))
    return key

def clear_bucket():
    subprocess.check_call(['aws', 's3', 'rm', '--recursive', _S3_URL])


def write_read(key, content, write_mode, read_mode, encoding=None, s3_upload=None, **kwargs):
    with smart_open.smart_open(
            key, write_mode, encoding=encoding,
            s3_upload=s3_upload, **kwargs) as fout:
        fout.write(content)
    with smart_open.smart_open(key, read_mode, encoding=encoding, **kwargs) as fin:
        actual = fin.read()
    return actual


def read_length_prefixed_messages(key, read_mode, encoding=None, **kwargs):
    with smart_open.smart_open(key, read_mode, encoding=encoding, **kwargs) as fin:
        actual = b''
        length_byte = fin.read(1)
        while len(length_byte):
            actual += length_byte
            msg = fin.read(ord(length_byte))
            actual += msg
            length_byte = fin.read(1)
    return actual


def test_s3_readwrite_text(benchmark):
    _S3_URL_KEY = initialize_bucket()

    key = _S3_URL_KEY + '/sanity.txt'
    text = 'с гранатою в кармане, с чекою в руке'
    actual = benchmark(write_read, key, text, 'w', 'r', 'utf-8')

    clear_bucket()
    assert actual == text


def test_s3_readwrite_text_gzip(benchmark):
    _S3_URL_KEY = initialize_bucket()

    key = _S3_URL_KEY + '/sanity.txt.gz'
    text = 'не чайки здесь запели на знакомом языке'
    actual = benchmark(write_read, key, text, 'w', 'r', 'utf-8')
    assert actual == text


def test_s3_readwrite_binary(benchmark):
    _S3_URL_KEY = initialize_bucket()

    key = _S3_URL_KEY + '/sanity.txt'
    binary = b'this is a test'
    actual = benchmark(write_read, key, binary, 'wb', 'rb')

    clear_bucket()
    assert actual == binary


def test_s3_readwrite_binary_gzip(benchmark):
    _S3_URL_KEY = initialize_bucket()

    key = _S3_URL_KEY + '/sanity.txt.gz'
    binary = b'this is a test'
    actual = benchmark(write_read, key, binary, 'wb', 'rb')

    clear_bucket()
    assert actual == binary


def test_s3_performance(benchmark):
    _S3_URL_KEY = initialize_bucket()

    one_megabyte = io.BytesIO()
    for _ in range(1024*128):
        one_megabyte.write(b'01234567')
    one_megabyte = one_megabyte.getvalue()

    key = _S3_URL_KEY + '/performance.txt'
    actual = benchmark(write_read, key, one_megabyte, 'wb', 'rb')

    clear_bucket()
    assert actual == one_megabyte


def test_s3_performance_gz(benchmark):
    _S3_URL_KEY = initialize_bucket()

    one_megabyte = io.BytesIO()
    for _ in range(1024*128):
        one_megabyte.write(b'01234567')
    one_megabyte = one_megabyte.getvalue()

    key = _S3_URL_KEY + '/performance.txt.gz'
    actual = benchmark(write_read, key, one_megabyte, 'wb', 'rb')

    clear_bucket()
    assert actual == one_megabyte


def test_s3_performance_small_reads(benchmark):
    _S3_URL_KEY = initialize_bucket()

    ONE_MIB = 1024**2
    one_megabyte_of_msgs = io.BytesIO()
    msg = b'\x0f' + b'0123456789abcde'  # a length-prefixed "message"
    for _ in range(0, ONE_MIB, len(msg)):
        one_megabyte_of_msgs.write(msg)
    one_megabyte_of_msgs = one_megabyte_of_msgs.getvalue()

    key = _S3_URL_KEY + '/many_reads_performance.bin'

    with smart_open.smart_open(key, 'wb') as fout:
        fout.write(one_megabyte_of_msgs)

    actual = benchmark(read_length_prefixed_messages, key, 'rb', buffer_size=ONE_MIB)

    clear_bucket()
    assert actual == one_megabyte_of_msgs


def test_s3_encrypted_file(benchmark):
    _S3_URL_KEY = initialize_bucket()

    key = _S3_URL_KEY + '/sanity.txt'
    text = 'с гранатою в кармане, с чекою в руке'
    actual = benchmark(write_read, key, text, 'w', 'r', 'utf-8', s3_upload={
        'ServerSideEncryption': 'AES256'
    })

    clear_bucket()
    assert actual == text
