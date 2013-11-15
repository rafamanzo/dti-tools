#!/bin/bash

coverage run --source src/classes/ src/tests/unit_tests.py
coverage report -m
coverage html