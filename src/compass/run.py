#!/usr/bin/env python3
"""
Strands Agent 実行スクリプト
"""
import sys
import os

# パッケージのルートディレクトリをPythonパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import main

if __name__ == "__main__":
    main()
