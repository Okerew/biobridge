import os
import sys
import ast


def parse_setup_py(setup_py_path):
    with open(setup_py_path, 'r') as file:
        setup_code = file.read()

    # Parse the content of the setup.py file
    tree = ast.parse(setup_code)

    return setup_code, tree


def find_ext_modules(tree):
    # Find the 'ext_modules' variable in the setup.py AST
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == 'ext_modules':
                    return node.value
    return None


def append_source_to_extension(setup_py_path, cpp_file_path, ext_index):
    # Ensure files exist
    if not os.path.exists(setup_py_path):
        print(f"Error: setup.py file not found at {setup_py_path}")
        sys.exit(1)

    if not os.path.exists(cpp_file_path):
        print(f"Error: C++ file not found at {cpp_file_path}")
        sys.exit(1)

    # Parse the setup.py file
    setup_code, tree = parse_setup_py(setup_py_path)

    # Find the ext_modules list in the setup.py file
    ext_modules_node = find_ext_modules(tree)

    if not ext_modules_node or not isinstance(ext_modules_node, ast.List):
        print("Error: Could not find 'ext_modules' in setup.py")
        sys.exit(1)

    # Check if the index is valid
    if ext_index >= len(ext_modules_node.elts):
        print(f"Error: Invalid ext_index {ext_index}. Only {len(ext_modules_node.elts)} extensions found.")
        sys.exit(1)

    # Get the specific extension module by index
    extension_node = ext_modules_node.elts[ext_index]

    # Check if it has a 'sources' field
    if not hasattr(extension_node, 'keywords'):
        print("Error: Could not find sources in the Extension.")
        sys.exit(1)

    keywords = getattr(extension_node, 'keywords', None)
    sources_node = None
    if keywords is not None:
        for kw in keywords:
            if kw.arg == 'sources' and isinstance(kw.value, ast.List):
                sources_node = kw.value
                break
    if sources_node is None:
        print("Error: 'sources' not found in the Extension.")
        sys.exit(1)

    # Append the new C++ source file
    cpp_file_path = os.path.abspath(cpp_file_path)
    sources_node.elts.append(ast.Constant(value=cpp_file_path, kind=None))

    # Generate new source code with the updated ext_modules
    with open(setup_py_path, 'w') as file:
        file.write(ast.unparse(tree))

    print(f"Appended {cpp_file_path} to ext_modules[{ext_index}].")


def add_new_extension(setup_py_path, ext_name, cpp_source, extra_compile_args=None):
    # Ensure files exist
    if not os.path.exists(setup_py_path):
        print(f"Error: setup.py file not found at {setup_py_path}")
        sys.exit(1)

    if not os.path.exists(cpp_source):
        print(f"Error: C++ file not found at {cpp_source}")
        sys.exit(1)

    # Parse the setup.py file
    with open(setup_py_path, 'r') as file:
        setup_code = file.read()

    try:
        tree = ast.parse(setup_code)
    except SyntaxError as e:
        print(f"Error: Failed to parse setup.py file - {e}")
        sys.exit(1)

    # Find the ext_modules list in the setup.py file
    ext_modules_node = None
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == 'ext_modules':
                    ext_modules_node = node
                    break

    if ext_modules_node is None:
        print("Error: Could not find 'ext_modules' in setup.py")
        sys.exit(1)

    # Create a new extension with provided sources
    cpp_source = os.path.abspath(cpp_source)
    new_extension = ast.Call(
        func=ast.Name(id='Extension'),
        args=[
            ast.Str(s=ext_name),
            ast.List(elts=[ast.Str(s=cpp_source)], ctx=ast.Load())
        ],
        keywords=[
            ast.keyword(arg='language', value=ast.Str(s='c++'))  # Ensure language is set to C++
        ]
    )

    # Add extra_compile_args if provided
    if extra_compile_args:
        new_extension.keywords.append(
            ast.keyword(arg='extra_compile_args', value=ast.List(elts=[ast.Str(s=arg) for arg in extra_compile_args], ctx=ast.Load()))
        )

    # Append the new extension to ext_modules
    if isinstance(ext_modules_node.value, ast.List):
        ext_modules_node.value.elts.append(new_extension)
    else:
        print("Error: ext_modules is not a list")
        sys.exit(1)

    # Generate new source code with the updated ext_modules
    with open(setup_py_path, 'w') as file:
        file.write(ast.unparse(tree))

    print(f"Added new Extension '{ext_name}' with sources [{cpp_source}].")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print(
            "To link a source to an existing Extension: python modify_setup.py -link <path_to_setup.py> <path_to_cpp_file> <ext_index>")
        print(
            "To add a new Extension: python modify_setup.py -add <path_to_setup.py> <extension_name> <cpp_source> [extra_compile_args...]")
        sys.exit(1)

    mode = sys.argv[1]

    python_lib_path = os.path.join(sys.prefix, 'lib')
    biobridge_path = os.path.join(python_lib_path, 'biobridge')
    setup_py_path = os.path.join(biobridge_path, 'setup.py')

    if mode == "-link":
        if len(sys.argv) != 4:
            print("Usage: python extension_manager.py -link <path_to_cpp_file> <ext_index>")
            sys.exit(1)

        cpp_file_path = sys.argv[2]
        ext_index = int(sys.argv[3])

        append_source_to_extension(setup_py_path, cpp_file_path, ext_index)

    elif mode == "-add":
        if len(sys.argv) < 4:
            print("Usage: python extension_manager.py -add <extension_name> <cpp_source> [extra_compile_args...]")
            sys.exit(1)

        ext_name = sys.argv[2]
        cpp_source = sys.argv[3]
        extra_compile_args = sys.argv[4:] if len(sys.argv) > 4 else None

        add_new_extension(setup_py_path, ext_name, cpp_source, extra_compile_args)

    else:
        print("Invalid mode. Use '-link' or '-add'.")
        sys.exit(1)
