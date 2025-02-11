from biobridge.utilities.convert_to_binary import BinaryConverter

converter = BinaryConverter("Hello123World45")
binary_output = converter.convert_string_with_ints_to_binary()
print(binary_output)
