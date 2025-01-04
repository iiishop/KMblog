import os
import importlib
import inspect
import readline
from commands import Command

# Define a completer function for readline
def completer(text, state):
    options = [cmd for cmd in COMMANDS.keys() if cmd.lower().startswith(text.lower())]
    if state < len(options):
        return options[state]
    else:
        return None

# Function to dynamically get all command classes from the module
def get_commands(module):
    commands = {}
    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj) and issubclass(obj, Command) and obj is not Command:
            commands[name] = obj
    return commands

def show_help():
    print("\033[1;34m\n=== Available Commands ===\033[0m")
    for cmd_name, cmd_class in COMMANDS.items():
        print(f"\033[1;32m{cmd_name}\033[0m - {cmd_class.description}")
        print("\033[1;34m----------------------------\033[0m")
    print("\033[1;32mexit\033[0m - Exit the program")
    print("\033[1;32mhelp\033[0m - Show this help message")
    print("\033[1;34m===========================\033[0m")

def main():
    # Dynamically load the commands from the commands module
    commands_module = importlib.import_module('commands')
    global COMMANDS
    COMMANDS = get_commands(commands_module)

    # Setup readline for command completion
    readline.set_completer(completer)
    readline.parse_and_bind("tab: complete")

    while True:
        command_name = input(">>> ").strip()
        if command_name.lower() == 'exit':
            print("Exiting...")
            break
        elif command_name.lower() == 'help':
            show_help()
        else:
            # Find the matching command class
            matched_commands = [cmd for cmd in COMMANDS if cmd.lower() == command_name.lower()]
            if matched_commands:
                command_class = COMMANDS[matched_commands[0]]
                try:
                    command_instance = command_class()
                    result = command_instance.execute()
                    print(f"\n{command_name} output:")
                    print(result)
                except Exception as e:
                    print(f"Error executing {command_name}: {e}")
            else:
                print("Unknown command. Please try again.")
                show_help()

if __name__ == '__main__':
    main()