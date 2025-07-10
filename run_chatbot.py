#!/usr/bin/env python3
"""
Launcher script for OpenRouter Chatbot that suppresses ALSA warnings
"""

import os
import sys
import subprocess

# Suppress ALSA warnings completely
if sys.platform.startswith('linux'):
    # Set environment variables to suppress audio warnings
    env = os.environ.copy()
    env['ALSA_CARD'] = 'null'
    env['SDL_AUDIODRIVER'] = 'dummy'
    
    # Run the main program with both stdout and stderr redirected for complete silence
    with open(os.devnull, 'w') as devnull:
        # Start the process with suppressed output
        proc = subprocess.Popen(
            [sys.executable, 'openrouter_chatbot.py'], 
            stderr=devnull,
            stdout=subprocess.PIPE,
            env=env
        )
        
        # Only print actual application output, not ALSA warnings
        for line in proc.stdout:
            decoded = line.decode('utf-8', errors='ignore')
            if not any(x in decoded.lower() for x in ['alsa', 'aplay', 'audio', 'pcm', 'card']):
                print(decoded, end='')
        
        proc.wait()
else:
    # On non-Linux systems, just run normally
    subprocess.run([sys.executable, 'openrouter_chatbot.py'])
