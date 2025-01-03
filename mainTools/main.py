import os
import importlib
import inspect
import argparse
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
        print(f"\033[90m{cmd_class.example}\033[0m")
        print("\033[1;34m----------------------------\033[0m")
    print("\033[1;32mexit\033[0m - Exit the program")
    print("\033[1;32mhelp\033[0m - Show this help message")
    print("\033[1;34m===========================\033[0m")

def main():
    parser = argparse.ArgumentParser(description="My Tool for managing posts and collections")
    parser.add_argument('-p', '--path', default='../src/Posts', help="Path to the posts directory")
    parser.add_argument('-o', '--output', default='../src/assets/PostDirectory.json', help="Path to the output JSON file")
    args = parser.parse_args()

    posts_path = os.path.abspath(os.path.join(os.path.dirname(__file__), args.path))
    output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), args.output))

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
            # Split the command and its arguments
            parts = command_name.split()
            base_command = parts[0] if parts else ''
            command_args = parts[1:]

            # Find the matching command class
            matched_commands = [cmd for cmd in COMMANDS if cmd.lower() == base_command.lower()]
            if matched_commands:
                command_class = COMMANDS[matched_commands[0]]
                try:
                    # Get the __init__ method signature
                    init_signature = inspect.signature(command_class.__init__)
                    init_params = init_signature.parameters

                    # Create the appropriate arguments list
                    if 'output_path' in init_params and command_class.__name__ == 'AddPostCommand':
                        # Handle AddPostCommand separately, passing posts_path, output_path, name, and collection
                        name = command_args[0] if len(command_args) > 0 else None
                        collection = command_args[1] if len(command_args) > 1 else None
                        command_instance = command_class(posts_path, output_path, name, collection)
                    elif 'output_path' in init_params:
                        # If the class requires output_path, pass both posts_path and output_path
                        command_instance = command_class(posts_path, output_path)
                    else:
                        # Otherwise, pass only posts_path
                        command_instance = command_class(posts_path)
                    
                    result = command_instance.execute()
                    print(f"\n{command_name} output:")
                    print(result)
                except IndexError:
                    print(f"Error: Missing required parameters for {command_name}.")
                    print(f"{command_class.description}")
                    print(f"{command_class.example}")
                except Exception as e:
                    print(f"Error executing {command_name}: {e}")
            else:
                print("Unknown command. Please try again.")
                show_help()

if __name__ == '__main__':
    main()