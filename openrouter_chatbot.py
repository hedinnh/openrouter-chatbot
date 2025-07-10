import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import requests
import json
import os
import threading
from datetime import datetime
import re
import sys

# Suppress ALSA audio warnings on Linux
if sys.platform.startswith('linux'):
    os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
    # Redirect stderr temporarily during pyttsx3 import
    import io
    old_stderr = sys.stderr
    sys.stderr = io.StringIO()

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None
finally:
    # Restore stderr
    if sys.platform.startswith('linux'):
        sys.stderr = old_stderr

class OpenRouterChatbot:
    def __init__(self, root):
        self.root = root
        self.root.title("OpenRouter AI Chat")
        self.root.geometry("1000x700")
        
        # Set modern dark theme colors
        self.bg_color = "#1e1e1e"
        self.fg_color = "#ffffff"
        self.accent_color = "#007acc"
        self.hover_color = "#005a9e"
        self.entry_bg = "#2d2d2d"
        self.button_bg = "#3c3c3c"
        self.chat_bg = "#252526"
        
        self.root.configure(bg=self.bg_color)
        
        # Initialize TTS engine
        self.tts_engine = None
        self.tts_available = False
        try:
            self.tts_engine = pyttsx3.init()
            self.tts_available = True
        except Exception as e:
            print(f"TTS initialization failed: {e}")
            print("TTS will be disabled. Install espeak on Linux: sudo apt-get install espeak")
        
        self.tts_enabled = tk.BooleanVar(value=False)
        
        # Initialize variables
        self.api_key = ""
        self.selected_model = tk.StringVar()
        self.models = []
        self.conversation_history = []
        self.memory_file = "chat_memory.json"
        self.config_file = "config.json"
        
        # Create GUI
        self.create_widgets()
        
        # Load config and memory after GUI is created
        self.load_config()
        self.load_memory()
        
        # Apply custom styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()
        
    def configure_styles(self):
        # Configure ttk styles for modern look
        self.style.configure("TLabel", background=self.bg_color, foreground=self.fg_color)
        self.style.configure("TFrame", background=self.bg_color)
        self.style.configure("TCombobox", fieldbackground=self.entry_bg, background=self.button_bg, foreground=self.fg_color)
        self.style.configure("TCheckbutton", background=self.bg_color, foreground=self.fg_color)
        self.style.map('TCombobox', fieldbackground=[('readonly', self.entry_bg)])
        
    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root, style="TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Settings Frame
        settings_frame = ttk.Frame(main_frame, style="TFrame")
        settings_frame.pack(fill=tk.X, pady=(0, 10))
        
        # API Key Section
        api_frame = ttk.Frame(settings_frame, style="TFrame")
        api_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(api_frame, text="API Key:", style="TLabel").pack(side=tk.LEFT, padx=(0, 5))
        
        self.api_key_entry = tk.Entry(api_frame, show="*", bg=self.entry_bg, fg=self.fg_color, 
                                     insertbackground=self.fg_color, bd=0, font=("Arial", 10))
        self.api_key_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.save_key_btn = tk.Button(api_frame, text="Save Key", command=self.save_api_key,
                                      bg=self.accent_color, fg=self.fg_color, bd=0, padx=15, pady=5,
                                      font=("Arial", 10, "bold"), cursor="hand2")
        self.save_key_btn.pack(side=tk.LEFT)
        self.save_key_btn.bind("<Enter>", lambda e: self.save_key_btn.config(bg=self.hover_color))
        self.save_key_btn.bind("<Leave>", lambda e: self.save_key_btn.config(bg=self.accent_color))
        
        # Model Selection and TTS Frame
        model_tts_frame = ttk.Frame(settings_frame, style="TFrame")
        model_tts_frame.pack(fill=tk.X)
        
        # Model Selection
        model_frame = ttk.Frame(model_tts_frame, style="TFrame")
        model_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 20))
        
        ttk.Label(model_frame, text="Model:", style="TLabel").pack(side=tk.LEFT, padx=(0, 5))
        
        self.model_dropdown = ttk.Combobox(model_frame, textvariable=self.selected_model, 
                                          state="readonly", width=50)
        self.model_dropdown.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.model_dropdown.bind("<<ComboboxSelected>>", lambda e: self.save_config())
        
        # TTS Toggle
        tts_text = "Enable Text-to-Speech" if self.tts_available else "Text-to-Speech (unavailable)"
        self.tts_check = ttk.Checkbutton(model_tts_frame, text=tts_text, 
                                         variable=self.tts_enabled, style="TCheckbutton",
                                         state="normal" if self.tts_available else "disabled",
                                         command=self.save_config)
        self.tts_check.pack(side=tk.LEFT)
        
        # Chat Display
        chat_frame = ttk.Frame(main_frame, style="TFrame")
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self.chat_display = scrolledtext.ScrolledText(chat_frame, wrap=tk.WORD, bg=self.chat_bg, 
                                                      fg=self.fg_color, insertbackground=self.fg_color,
                                                      font=("Arial", 11), bd=0, padx=10, pady=10)
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        self.chat_display.config(state=tk.DISABLED)
        
        # Configure tags for message styling
        self.chat_display.tag_config("user", foreground="#4ec9b0")
        self.chat_display.tag_config("assistant", foreground="#9cdcfe")
        self.chat_display.tag_config("system", foreground="#ce9178", font=("Arial", 9, "italic"))
        self.chat_display.tag_config("timestamp", foreground="#858585", font=("Arial", 8))
        self.chat_display.tag_config("thinking", foreground="#d4d4d4", font=("Arial", 10, "italic"), background="#2d2d2d")
        
        # Input Frame
        input_frame = ttk.Frame(main_frame, style="TFrame")
        input_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.message_entry = tk.Text(input_frame, height=3, bg=self.entry_bg, fg=self.fg_color,
                                    insertbackground=self.fg_color, font=("Arial", 11), bd=0, 
                                    padx=10, pady=10, wrap=tk.WORD)
        self.message_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        self.message_entry.bind("<Return>", self.send_message_event)
        self.message_entry.bind("<Shift-Return>", lambda e: None)
        
        # Button Frame
        button_frame = ttk.Frame(input_frame, style="TFrame")
        button_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.send_btn = tk.Button(button_frame, text="Send", command=self.send_message,
                                 bg=self.accent_color, fg=self.fg_color, bd=0, padx=20, pady=10,
                                 font=("Arial", 11, "bold"), cursor="hand2")
        self.send_btn.pack(pady=(0, 5))
        self.send_btn.bind("<Enter>", lambda e: self.send_btn.config(bg=self.hover_color))
        self.send_btn.bind("<Leave>", lambda e: self.send_btn.config(bg=self.accent_color))
        
        self.clear_btn = tk.Button(button_frame, text="Clear", command=self.clear_chat,
                                  bg=self.button_bg, fg=self.fg_color, bd=0, padx=20, pady=5,
                                  font=("Arial", 10), cursor="hand2")
        self.clear_btn.pack()
        self.clear_btn.bind("<Enter>", lambda e: self.clear_btn.config(bg="#4a4a4a"))
        self.clear_btn.bind("<Leave>", lambda e: self.clear_btn.config(bg=self.button_bg))
        
        # Log Window Frame
        log_frame = ttk.Frame(main_frame, style="TFrame")
        log_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(log_frame, text="System Log:", style="TLabel").pack(anchor=tk.W)
        
        # Log Display
        self.log_display = scrolledtext.ScrolledText(log_frame, height=6, wrap=tk.WORD, 
                                                     bg=self.chat_bg, fg="#808080",
                                                     font=("Consolas", 9), bd=0, padx=5, pady=5)
        self.log_display.pack(fill=tk.X)
        self.log_display.config(state=tk.DISABLED)
        
        # Configure log tags
        self.log_display.tag_config("error", foreground="#f48771")
        self.log_display.tag_config("warning", foreground="#dcdcaa")
        self.log_display.tag_config("success", foreground="#4ec9b0")
        self.log_display.tag_config("info", foreground="#9cdcfe")
        
        # Initial log message
        self.log_message("Application started", "SUCCESS")
        if not self.tts_available:
            self.log_message("TTS unavailable - install espeak for TTS support", "WARNING")
        
    def log_message(self, message, level="INFO"):
        """Add a message to the log window"""
        self.log_display.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Color coding for different log levels
        if level == "ERROR":
            self.log_display.insert(tk.END, f"[{timestamp}] ERROR: ", "error")
        elif level == "WARNING":
            self.log_display.insert(tk.END, f"[{timestamp}] WARNING: ", "warning")
        elif level == "SUCCESS":
            self.log_display.insert(tk.END, f"[{timestamp}] SUCCESS: ", "success")
        else:
            self.log_display.insert(tk.END, f"[{timestamp}] INFO: ", "info")
        
        self.log_display.insert(tk.END, f"{message}\n")
        self.log_display.config(state=tk.DISABLED)
        self.log_display.see(tk.END)
        
    def save_api_key(self):
        self.api_key = self.api_key_entry.get()
        if self.api_key:
            self.log_message("Saving API key...")
            self.save_config()
            self.fetch_models()
            self.log_message("API key saved successfully", "SUCCESS")
            messagebox.showinfo("Success", "API Key saved successfully!")
        else:
            self.log_message("No API key provided", "WARNING")
            messagebox.showwarning("Warning", "Please enter an API key")
    
    def save_config(self):
        config_data = {
            "api_key": self.api_key,
            "last_model": self.selected_model.get(),
            "tts_enabled": self.tts_enabled.get()
        }
        with open(self.config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
    
    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                    self.api_key = config_data.get("api_key", "")
                    
                    # Set the API key in entry field after GUI is created
                    self.root.after(100, self._populate_config_data, config_data)
            except Exception as e:
                print(f"Error loading config: {e}")
    
    def _populate_config_data(self, config_data):
        # Populate API key entry
        if self.api_key:
            self.api_key_entry.insert(0, self.api_key)
            self.fetch_models()
        
        # Set last used model if available
        last_model = config_data.get("last_model", "")
        if last_model and last_model in self.models:
            self.selected_model.set(last_model)
        
        # Set TTS preference
        self.tts_enabled.set(config_data.get("tts_enabled", False))
    
    def fetch_models(self):
        try:
            self.log_message("Fetching available models from OpenRouter...")
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            response = requests.get("https://openrouter.ai/api/v1/models", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.models = [model['id'] for model in data['data']]
                self.model_dropdown['values'] = self.models
                self.log_message(f"Successfully fetched {len(self.models)} models", "SUCCESS")
                
                # Try to preserve the selected model if it still exists
                current_model = self.selected_model.get()
                if current_model in self.models:
                    self.selected_model.set(current_model)
                elif self.models:
                    self.selected_model.set(self.models[0])
                    self.log_message(f"Selected model: {self.models[0]}")
            else:
                error_msg = f"Failed to fetch models: {response.text}"
                self.log_message(error_msg, "ERROR")
                messagebox.showerror("Error", error_msg)
        except Exception as e:
            error_msg = f"Error fetching models: {str(e)}"
            self.log_message(error_msg, "ERROR")
            messagebox.showerror("Error", error_msg)
    
    def send_message_event(self, event):
        if not event.state & 0x1:  # Check if Shift is not pressed
            self.send_message()
            return "break"
    
    def send_message(self):
        message = self.message_entry.get("1.0", tk.END).strip()
        if not message:
            return
        
        if not self.api_key:
            self.log_message("No API key set", "WARNING")
            messagebox.showwarning("Warning", "Please set your API key first")
            return
        
        if not self.selected_model.get():
            self.log_message("No model selected", "WARNING")
            messagebox.showwarning("Warning", "Please select a model")
            return
        
        # Clear input
        self.message_entry.delete("1.0", tk.END)
        
        # Display user message
        self.display_message("You", message, "user")
        
        # Add to conversation history
        self.conversation_history.append({"role": "user", "content": message})
        
        # Log the request
        self.log_message(f"Sending message to {self.selected_model.get()}")
        
        # Send request in thread
        threading.Thread(target=self.get_ai_response, args=(message,), daemon=True).start()
    
    def get_ai_response(self, message):
        try:
            self.root.after(0, self.log_message, "Preparing API request...")
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Prepare messages with context
            messages = self.conversation_history[-10:]  # Last 10 messages for context
            
            data = {
                "model": self.selected_model.get(),
                "messages": messages
            }
            
            self.root.after(0, self.log_message, f"Sending request to OpenRouter API...")
            
            # First try without streaming to get proper error messages
            response = requests.post("https://openrouter.ai/api/v1/chat/completions", 
                                   headers=headers, json=data, stream=False)
            
            if response.status_code == 200:
                self.root.after(0, self.log_message, "Response received, processing...", "SUCCESS")
                
                result = response.json()
                full_response = result['choices'][0]['message']['content']
                
                # Check for thinking tags in the response
                thinking_content = None
                display_response = full_response
                
                if '<thinking>' in full_response and '</thinking>' in full_response:
                    # Extract thinking content
                    import re
                    thinking_match = re.search(r'<thinking>(.*?)</thinking>', full_response, re.DOTALL)
                    if thinking_match:
                        thinking_content = thinking_match.group(1).strip()
                        self.root.after(0, self.log_message, "Model thinking process detected", "INFO")
                        # Remove thinking tags from the displayed response
                        display_response = re.sub(r'<thinking>.*?</thinking>', '', full_response, flags=re.DOTALL).strip()
                
                # Log success
                self.root.after(0, self.log_message, "Response received successfully", "SUCCESS")
                
                # Display thinking process if present
                if thinking_content:
                    self.root.after(0, self.display_thinking, "Assistant (thinking)", thinking_content)
                
                # Display actual response
                self.root.after(0, self.display_message, "Assistant", display_response, "assistant")
                
                # Save full response (without thinking tags) to history
                self.conversation_history.append({"role": "assistant", "content": display_response})
                
                # Save to memory
                self.save_memory()
                
                # TTS if enabled
                if self.tts_enabled.get():
                    self.root.after(0, self.log_message, "Starting TTS...")
                    threading.Thread(target=self.speak_text, args=(full_response,), daemon=True).start()
            else:
                # Parse error response
                error_data = response.json()
                error_msg = "Unknown error"
                
                if 'error' in error_data:
                    error_info = error_data['error']
                    error_msg = error_info.get('message', 'Unknown error')
                    
                    # Log detailed error info
                    self.root.after(0, self.log_message, f"API Error {response.status_code}: {error_msg}", "ERROR")
                    
                    if 'metadata' in error_info:
                        metadata = error_info['metadata']
                        if 'raw' in metadata:
                            self.root.after(0, self.log_message, f"Raw error: {metadata['raw']}", "ERROR")
                        if 'provider_name' in metadata:
                            self.root.after(0, self.log_message, f"Provider: {metadata['provider_name']}", "ERROR")
                    
                    # Check for specific error types
                    if "No instances available" in error_msg:
                        self.root.after(0, self.log_message, 
                                      "This model may not exist or is currently unavailable. Try selecting a different model.", 
                                      "WARNING")
                
                self.root.after(0, messagebox.showerror, "API Error", 
                               f"Error {response.status_code}: {error_msg}\n\nPlease check the log for details.")
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error: {str(e)}"
            self.root.after(0, self.log_message, error_msg, "ERROR")
            self.root.after(0, messagebox.showerror, "Network Error", error_msg)
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self.root.after(0, self.log_message, error_msg, "ERROR")
            self.root.after(0, messagebox.showerror, "Error", error_msg)
    
    def speak_text(self, text):
        if not self.tts_available or not self.tts_engine:
            return
        
        try:
            # Clean text for TTS
            clean_text = re.sub(r'[*_`#]', '', text)
            self.tts_engine.say(clean_text)
            self.tts_engine.runAndWait()
        except Exception as e:
            print(f"TTS error: {e}")
    
    def display_message(self, sender, message, tag):
        self.chat_display.config(state=tk.NORMAL)
        
        # Add timestamp
        timestamp = datetime.now().strftime("%H:%M")
        self.chat_display.insert(tk.END, f"[{timestamp}] ", "timestamp")
        
        # Add sender and message
        self.chat_display.insert(tk.END, f"{sender}: ", tag)
        self.chat_display.insert(tk.END, f"{message}\n\n")
        
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def display_thinking(self, sender, thinking_content):
        """Display thinking process in a special format"""
        self.chat_display.config(state=tk.NORMAL)
        
        # Add timestamp
        timestamp = datetime.now().strftime("%H:%M")
        self.chat_display.insert(tk.END, f"[{timestamp}] ", "timestamp")
        
        # Add thinking header
        self.chat_display.insert(tk.END, f"{sender}:\n", "thinking")
        
        # Add thinking content in a box
        self.chat_display.insert(tk.END, "┌─ Thinking Process ─────────────────────────────────\n", "thinking")
        
        # Process and display thinking content with proper indentation
        lines = thinking_content.split('\n')
        for line in lines:
            self.chat_display.insert(tk.END, "│ ", "thinking")
            self.chat_display.insert(tk.END, f"{line}\n", "thinking")
        
        self.chat_display.insert(tk.END, "└────────────────────────────────────────────────────\n\n", "thinking")
        
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def clear_chat(self):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete("1.0", tk.END)
        self.chat_display.config(state=tk.DISABLED)
        self.conversation_history = []
        self.save_memory()
        self.display_message("System", "Chat cleared. Memory reset.", "system")
    
    def save_memory(self):
        memory_data = {
            "conversation_history": self.conversation_history[-50:],  # Keep last 50 messages
            "last_model": self.selected_model.get(),
            "timestamp": datetime.now().isoformat()
        }
        with open(self.memory_file, 'w') as f:
            json.dump(memory_data, f, indent=2)
    
    def load_memory(self):
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    memory_data = json.load(f)
                    self.conversation_history = memory_data.get("conversation_history", [])
                    
                    # Display loaded conversation
                    for msg in self.conversation_history:
                        if msg["role"] == "user":
                            self.display_message("You", msg["content"], "user")
                        else:
                            self.display_message("Assistant", msg["content"], "assistant")
                    
                    if self.conversation_history:
                        self.display_message("System", "Previous conversation loaded from memory.", "system")
            except Exception as e:
                print(f"Error loading memory: {e}")

def main():
    root = tk.Tk()
    app = OpenRouterChatbot(root)
    root.mainloop()

if __name__ == "__main__":
    main()
