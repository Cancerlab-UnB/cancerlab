name: Convert images to WebP

on:
  push:
    branches: [ main, master ]
    paths:
      - '**.jpg'
      - '**.jpeg'
      - '**.png'
      - 'tools/convert_to_webp.py'
      - '.github/workflows/convert-webp.yml'
  workflow_dispatch: {}

jobs:
  webp:
    runs-on: ubuntu-latest
    permissions:
      contents: write   # permite commitar de volta com GITHUB_TOKEN
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install Pillow
        run: pip install pillow

      - name: Convert to WebP
        run: python tools/convert_to_webp.py

      - name: Commit WebP files (if any)
        uses: stefanzweifel/git-auto-commit-action@v5
        with:
          commit_message: "chore: auto-generate WebP assets"
          file_pattern: "**/*.webp"
