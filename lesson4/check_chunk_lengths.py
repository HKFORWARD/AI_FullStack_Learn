from glob import glob

text_lines = []

# Read the file
for file_path in glob("mfd.md", recursive=True):
    with open(file_path, "r") as file:
        file_text = file.read()

    text_lines += file_text.split("# ")

# Print the length of each chunk
print("Length of each text chunk:")
for i, chunk in enumerate(text_lines):
    print(f"Chunk {i}: {len(chunk)} characters") 