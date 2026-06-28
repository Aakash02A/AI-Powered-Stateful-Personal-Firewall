import os
import re

def replace_in_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replacements dictionary
    # background -> bg-background
    # text-slate-100 -> text-foreground
    # text-slate-200 -> text-foreground
    # text-slate-300 -> text-muted
    # text-slate-400 -> text-muted
    # bg-slate-900 -> bg-background
    # bg-slate-800 -> bg-panel
    # bg-slate-700 -> bg-panel-hover
    # border-slate-700 -> border-border
    # border-slate-800 -> border-border
    
    replacements = {
        r'bg-slate-900(/50)?': 'bg-background',
        r'bg-slate-900/80': 'bg-background/80',
        r'bg-slate-800(/50)?': 'bg-panel',
        r'bg-slate-800/30': 'bg-panel',
        r'bg-slate-800/80': 'bg-panel/80',
        r'bg-slate-700(/50)?': 'bg-panel-hover',
        r'bg-slate-700/30': 'bg-panel-hover',
        r'text-slate-100': 'text-foreground',
        r'text-slate-200': 'text-foreground',
        r'text-slate-300': 'text-foreground', # maybe slightly dimmer, but foreground is fine
        r'text-slate-400': 'text-muted',
        r'text-slate-500': 'text-muted',
        r'border-slate-800(/50)?': 'border-border',
        r'border-slate-700(/50)?': 'border-border',
        r'border-slate-600(/50)?': 'border-border',
        r'hover:bg-slate-800(/50)?': 'hover:bg-panel',
        r'hover:bg-slate-700(/50)?': 'hover:bg-panel-hover',
        r'hover:bg-slate-600(/50)?': 'hover:bg-panel-hover',
        r'hover:text-slate-200': 'hover:text-foreground',
        r'hover:border-slate-700': 'hover:border-border',
        r'hover:border-slate-600': 'hover:border-border',
    }

    new_content = content
    for pattern, replacement in replacements.items():
        new_content = re.sub(pattern, replacement, new_content)

    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {filepath}")

def main():
    for root, dirs, files in os.walk('frontend/src'):
        for file in files:
            if file.endswith('.tsx') or file.endswith('.ts'):
                replace_in_file(os.path.join(root, file))

if __name__ == "__main__":
    main()
