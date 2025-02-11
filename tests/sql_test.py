from biobridge.dnalite.sqld import SQLDNAEncoder
encoder = SQLDNAEncoder()

# Store data
data = {"name": "John Doe", "age": 30, "city": "New York"}
encoder.store_data("person_info", data)

# Retrieve data
try:
    retrieved_data = encoder.retrieve_data("person_info")
    print(retrieved_data)
except ValueError as e:
    print(f"Error: {e}")


# Delete data
encoder.delete_data("person_info")

encoder.close()
