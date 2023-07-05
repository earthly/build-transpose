from typing import List

def extract_code_blocks(markdown: str) -> List[str]:
    in_code_block = False
    code_blocks : List[str] = []
    current_block : List[str] = []

    lines = markdown.split('\n')
    for line in lines:
        if line.strip().startswith('```'):
            if in_code_block:  # End of a block
                # Small blocks are usually just an description
                # of how to run the code, and not actual code
                if len(current_block) > 2:
                    code_blocks.append('\n'.join(current_block))
                current_block = []
            in_code_block = not in_code_block
        elif in_code_block:  # Inside a block
            current_block.append(line)

    return code_blocks