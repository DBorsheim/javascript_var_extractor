import re

def camel_to_snake(name):
    """
    Attempts to convert a given name to snake_case. If the name does not appear
    to be in camelCase or another convertible format, returns the original name.
    """
    # First, try converting camelCase to snake_case
    snake = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    snake = re.sub('([a-z0-9])([A-Z])', r'\1_\2', snake).lower()

    # Catch double underscores in case
    snake = snake.replace('__', '_')
    
    # Check if conversion has actually occurred by comparing with the original
    if snake == name:
        # No conversion needed/possible; return the original name
        return name
    else:
        # Conversion occurred; return the converted name
        return snake

def extract_js_variables(js_file_path, start_line=559):
    # Regular expressions to match variable and function declarations
    var_pattern = re.compile(r'\b(var|let|const)\s+([\w, {}]+)\s*=?')
    func_pattern = re.compile(r'function\s+\w*\s*\(([^)]*)\)')
    seen = set()  # Track seen variables for uniqueness
    variables = []  # Maintain original order of first occurrence
    current_line = 0  # Track the current line number

    with open(js_file_path, 'r') as file:
        for line in file:
            current_line += 1
            # Skip to the desired start line
            if current_line < start_line:
                continue

            # Skip commented lines
            if line.strip().startswith('//'):
                continue

            # Find all variable declarations
            vars_found = var_pattern.findall(line)
            for _, var_group in vars_found:
                # Handle multiple variables declared in one line
                for var in var_group.split(','):
                    var_name = var.split('=')[0].strip()
                    # Add to list if not already seen
                    if var_name not in seen:
                        seen.add(var_name)
                        # If the variable is a single letter, skip it
                        if len(var_name) > 1:
                            variables.append(var_name)
                            

            # Find all function parameters
            # funcs_found = func_pattern.findall(line)
            # for func_params in funcs_found:
            #     params = [param.strip() for param in func_params.split(',')]
            #     for param in params:
            #         # Add to list if not already seen
            #         if param not in seen:
            #             seen.add(param)
            #             variables.append(param)

    return variables


def process_and_save_variables(variables, output_file_path, save_new_variables=True):
    # Process variables into the specified format (original, new)
    processed_variables = [(var, camel_to_snake(var)) for var in variables]
    
    if save_new_variables:
        # Write the processed variable names to the file
        with open(output_file_path, 'w') as file:
            for original, new in processed_variables:
                file.write(f"{original}, {new}\n")
        print(f"Processed variable names saved to {output_file_path}.")

def replace_variables_in_file(js_file_path, variables_file_path):
    # Read the mappings from the variables file
    with open(variables_file_path, 'r') as file:
        mappings = dict(line.strip().split(', ') for line in file if line.strip())
    
    # Read the original JavaScript file content
    with open(js_file_path, 'r') as file:
        content = file.read()
    
    # Replace all instances of the original variable names with the new names
    for original, new in mappings.items():
        content = content.replace(original, new)
    
    # Write the modified content back to the file or a new file
    new_js_file_path = js_file_path.replace('.js', '_modified.js')
    with open(new_js_file_path, 'w') as file:
        file.write(content)
    
    print(f"All variables replaced. Modified file saved as {new_js_file_path}.")

# Main script starts here
js_file_path = input("Enter the path to the JavaScript file: ").strip().replace('"', '').replace("'", "").replace('\\', '/')
start_line = input("Enter the start line number (default is 500, press Enter to skip): ").strip()
start_line = int(start_line) if start_line.isdigit() else 500

variables = extract_js_variables(js_file_path, start_line)
print(f"Found {len(variables)} unique variables starting from line {start_line}.")

# Decide whether to save new variable names
save_option = input("Do you want to save the new variable names to a file? (yes/no): ").strip().lower()
save_new_variables = save_option == "yes"

# File path for variable mappings
variables_file_path = js_file_path.replace('.jsx', '_variables.txt')
if save_new_variables:
    process_and_save_variables(variables, variables_file_path, save_new_variables)

# Ask if the user wants to replace variable names in the JavaScript file
replace_option = input("Do you want to replace the variable names in the JavaScript file based on the text file? (yes/no): ").strip().lower()
if replace_option == "yes":
    replace_variables_in_file(js_file_path, variables_file_path)

