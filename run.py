import generator
import sys

if len(sys.argv) > 1:
    generator.execute(sys.argv[1]) # Directly to reading and generation
else:
    generator.execute() # With prompts
