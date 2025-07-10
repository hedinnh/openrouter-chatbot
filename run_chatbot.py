#!/usr/bin/env python3
"""
Launcher script for OpenRouter Chatbot that suppresses ALSA warnings
"""

import os
import sys
import subprocess

# Suppress ALSA warnings
if sys.platform.startswith('linux'):
    # Run the main program with stderr redirected to devnull
    with open(os.devnull, 'w') as devnull:
        subprocess.run([sys.executable, 'openrouter_chatbot.py'], stderr=devnull)
else:
    # On non-Linux systems, just run normally
    subprocess.run([sys.executable, 'openrouter_chatbot.py'])
