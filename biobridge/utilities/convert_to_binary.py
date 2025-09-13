class BinaryConverter:
    def __init__(self, input_str):
        self.input_str = input_str

    def char_to_binary(self, char):
        """
        Convert a single character to its binary representation.
        """
        return format(ord(char), '08b')

    def int_to_binary(self, number):
        """
        Convert an integer to its binary representation.
        """
        return format(int(number), 'b')

    def convert_string_with_ints_to_binary(self):
        """
        Detect integers in the string and convert both the string characters
        and the detected integers to their binary representations.
        """
        binary_representation = []
        current_number = ''

        for char in self.input_str:
            if char.isdigit():
                current_number += char
            else:
                if current_number:
                    # Convert detected number to binary and add to the result list
                    binary_representation.append(self.int_to_binary(current_number))
                    current_number = ''
                # Convert current non-digit character to binary and add to the result list
                binary_representation.append(self.char_to_binary(char))

        # If the string ends with a number, ensure it's converted to binary
        if current_number:
            binary_representation.append(self.int_to_binary(current_number))

        # Join the binary representations with spaces
        return ' '.join(binary_representation)
