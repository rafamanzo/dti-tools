#!/bin/bash

coverage run --source classes/ tests/classes/base/step_test.py
coverage report -m
coverage html