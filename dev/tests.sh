#!/bin/bash

coverage run src/tests/unit_tests.py
coverage report -m
coverage html