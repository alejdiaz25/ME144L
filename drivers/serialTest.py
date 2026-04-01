#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 16 14:18:04 2026

@author: alejandrodiaz
"""

print("Testing installation of pyserial module...")

try:
    import serial
    print("Congratulations, pyserial is installed correctly!")
except:
    print("Error, pyserial is not installed.")
