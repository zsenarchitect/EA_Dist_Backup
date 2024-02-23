import ast


def extract_global_variables(script_path):
    with open(script_path, 'r') as file:
        script_content = file.read()
    
    tree = ast.parse(script_content)
    global_vars = {}
    
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    var_name = target.id
                    # Handling the value directly if it's a constant
                    if isinstance(node.value, ast.Constant):
                        var_value = node.value.value  # Directly accessing the value of the Constant node
                    else:
                        try:
                            # Fallback for other types using literal_eval for safe evaluation
                            var_value = ast.literal_eval(node.value)
                        except ValueError:
                            # For non-literals or complex cases, keep a representation of the code
                            var_value = "Unsupported value for safe evaluation"
                    global_vars[var_name] = var_value
    
    return global_vars