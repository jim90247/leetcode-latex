#!/bin/bash
set -e

python leetcode-json-to-html.py
pandoc --standalone all.html --output index.tex 
python latex-postprocessing.py
pdflatex -interaction=nonstopmode main.tex >/dev/null 2>/dev/null
