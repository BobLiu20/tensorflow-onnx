# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT license.

"""Unit Tests for string ops."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import numpy as np
import tensorflow as tf

from backend_test_base import Tf2OnnxBackendTestBase
from common import unittest_main, check_tf_min_version, check_tf_max_version, check_onnxruntime_min_version, skip_tf2
from tf2onnx.tf_loader import is_tf2
from tf2onnx import utils
from tf2onnx import constants
from ortcustomops import get_library_path

# pylint: disable=missing-docstring,invalid-name,unused-argument,using-constant-test

# names for input and outputs for tests
_TFINPUT = "input"
_INPUT = "input:0"
_TFINPUT1 = "input1"
_INPUT1 = "input1:0"
_TFINPUT2 = "input2"
_INPUT2 = "input2:0"
_TFOUTPUT = "output"
_OUTPUT = "output:0"
_TFOUTPUT1 = "output1"
_OUTPUT1 = "output1:0"
_TFOUTPUT2 = "output2"
_OUTPUT2 = "output2:0"

class StringOpsTests(Tf2OnnxBackendTestBase):

    def test_static_regex_replace(self):
        text_val = np.array([["Hello world!", "Test 1 2 3"], ["Hi there", "test test"]], dtype=np.str)
        def func(text):
            x_ = tf.strings.regex_replace(text, " ", "_", replace_global=False)
            return tf.identity(x_, name=_TFOUTPUT)
        self._run_test_case(func, [_OUTPUT], {_INPUT: text_val})

    def test_string_join(self):
        text_val1 = np.array([["a", "Test 1 2 3"], ["Hi there", "test test"]], dtype=np.str)
        text_val2 = np.array([["b", "Test 1 2 3"], ["Hi there", "suits ♠♣♥♦"]], dtype=np.str)
        text_val3 = np.array("Some scalar text", dtype=np.str)
        def func(text1, text2, text3):
            x_ = tf.strings.join([text1, text2, text3], separator="±")
            return tf.identity(x_, name=_TFOUTPUT)
        self._run_test_case(func, [_OUTPUT], {_INPUT: text_val1, _INPUT1: text_val2, _INPUT2: text_val3})

    def test_string_split(self):
        text_val = np.array([["a", "Test 1 2 3"], ["Hi there", "test test"]], dtype=np.str)
        def func(text):
            x = tf.strings.split(text, sep=' ').flat_values
            x_ = tf.identity(x, name=_TFOUTPUT)
            return x_
        self._run_test_case(func, [_OUTPUT], {_INPUT: text_val})

    def test_string_to_hash_bucket_fast(self):
        text_val = np.array([["a", "Test 1 2 3", "♠♣"], ["Hi there", "test test", "♥♦"]], dtype=np.str)
        def func(text):
            x = tf.strings.to_hash_bucket_fast(text, 20)
            x_ = tf.identity(x, name=_TFOUTPUT)
            return x_
        self._run_test_case(func, [_OUTPUT], {_INPUT: text_val})

    def _run_test_case(self, func, output_names_with_port, feed_dict, **kwargs):
        extra_opset = [utils.make_opsetid(constants.CONTRIB_OPS_DOMAIN, 1)]
        process_args = {"extra_opset": extra_opset}
        return self.run_test_case(func, feed_dict, [], output_names_with_port, process_args=process_args, **kwargs)

    def run_onnxruntime(self, model_path, inputs, output_names):
        """Run test against onnxruntime backend."""
        import onnxruntime as rt
        opt = rt.SessionOptions()
        opt.register_custom_ops_library(get_library_path())
        m = rt.InferenceSession(model_path, opt)
        results = m.run(output_names, inputs)
        return results
