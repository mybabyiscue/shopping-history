#!/usr/bin/env python3
# -*- coding: utf-8 -*-

try:
    import matplotlib.pyplot as plt
    print("matplotlib已安装")
except ImportError:
    print("matplotlib未安装")
except Exception as e:
    print(f"matplotlib检查出错: {e}")