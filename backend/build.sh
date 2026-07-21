#!/usr/bin/env bash
# Render build script — installs deps, downloads spaCy model, copies frontend
pip install -r requirements.txt
python -m spacy download en_core_web_sm
# Copy frontend files into backend/static/ so Flask serves everything
cp -r ../frontend/* static/
