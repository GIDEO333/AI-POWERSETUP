import re
import sys
import os

def clean_markdown(filepath):
    if not os.path.exists(filepath):
        print(f"Error: File {filepath} not found.")
        return

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Define the start and end of the actual conversation
    # English and Indonesian markers
    start_markers = ["# Conversation with Gemini", "# Percakapan dengan Gemini"]
    
    found_start = -1
    for marker in start_markers:
        pos = content.find(marker)
        if pos != -1:
            found_start = pos
            break
    
    if found_start != -1:
        content = content[found_start:]

    # Remove the footer / profile artifacts
    footer_markers = ["![profile picture]", "![gambar profil]"]
    for marker in footer_markers:
        pos = content.find(marker)
        if pos != -1:
            content = content[:pos]

    # Remove YouTube widgets and embeddings
    content = re.sub(r'\[\s*!\[\]\(https://www\.gstatic\.com/images/branding/productlogos/youtube/v9/192px\.svg\).*?</iframe>', '', content, flags=re.DOTALL)
    
    # Clean up roles
    content = re.sub(r'You said|Anda berkata', '### 👤 User\n', content)
    content = re.sub(r'Show thinking|Tampilkan alur berpikir', '', content)
    content = re.sub(r'## Gemini said|## Gemini berkata', '### 🤖 Gemini\n', content)

    # Clean up excessive empty lines
    content = re.sub(r'\n{3,}', '\n\n', content)

    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("# Humanized Gemini Conversation\n\n")
        f.write(content.strip() + "\n")

    print(f"File formatted successfully!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 format_md.py <file_path>")
    else:
        clean_markdown(sys.argv[1])
