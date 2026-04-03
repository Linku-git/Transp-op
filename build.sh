#!/bin/bash
set -e

cd frontend
npm install
npm run build
cd ..

pip install -r backend/requirements.txt
