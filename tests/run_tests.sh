#!/bin/bash
rm report.html
pytest --html=report.html  --self-contained-html test_*

