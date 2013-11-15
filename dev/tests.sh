#!/bin/bash

coverage run --source src/classes/ src/tests/classes/base/step_test.py
coverage report -m
coverage html