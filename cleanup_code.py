"""
Cleanup script for debug statements and code quality improvements.
"""
import re
from pathlib import Path
from typing import List, Tuple

def clean_debug_statements(file_path: Path) -> Tuple[int, List[str]]:
    """
    Clean up debug print statements from a file.
    
    Args:
        file_path: Path to the file to clean
        
    Returns:
        Tuple of (number of changes, list of changes made)
    """
    if not file_path.exists():
        return 0, []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_lines = content.split('\n')
    cleaned_lines = []
    changes = []
    changes_count = 0
    
    for i, line in enumerate(original_lines):
        line_number = i + 1
        original_line = line
        
        # Remove debug print statements
        debug_patterns = [
            r'print\s*\(\s*["\'].*DEBUG.*["\'].*\)',  # print("DEBUG...")
            r'print\s*\(\s*["\']asdhfapsh8p9hfaiafdsi.*["\'].*\)',  # Specific debug pattern
            r'print\s*\(\s*["\']IMPORTANT VVV DEBUG["\'].*\)',  # Important debug
            r'#\s*print\s*\(\s*["\'].*DEBUG.*["\'].*\)',  # Commented debug prints
        ]
        
        cleaned_line = line
        for pattern in debug_patterns:
            if re.search(pattern, line):
                # Replace debug prints with proper logging or remove entirely
                if 'IMPORTANT' in line:
                    cleaned_line = line.replace('print (', '# DEBUG: print (')
                    changes.append(f"Line {line_number}: Commented important debug statement")
                else:
                    cleaned_line = re.sub(pattern, '# Removed debug print statement', line)
                    changes.append(f"Line {line_number}: Removed debug print")
                changes_count += 1
                break
        
        # Clean up excessive comment markers
        if re.search(r'#+\s*$', cleaned_line.strip()):
            cleaned_line = ''
            changes.append(f"Line {line_number}: Removed excessive comment markers")
            changes_count += 1
        
        cleaned_lines.append(cleaned_line)
    
    # Write back if changes were made
    if changes_count > 0:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(cleaned_lines))
    
    return changes_count, changes

def clean_todo_comments(file_path: Path) -> Tuple[int, List[str]]:
    """
    Improve TODO comments by making them more actionable.
    
    Args:
        file_path: Path to the file to clean
        
    Returns:
        Tuple of (number of changes, list of changes made)
    """
    if not file_path.exists():
        return 0, []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_lines = content.split('\n')
    cleaned_lines = []
    changes = []
    changes_count = 0
    
    for i, line in enumerate(original_lines):
        line_number = i + 1
        cleaned_line = line
        
        # Improve TODO comments
        if re.search(r'#\s*TODO\s+', line, re.IGNORECASE):
            # Make TODOs more specific and actionable
            if 'SOMETHING HERE' in line:
                cleaned_line = line.replace('TODO SOMETHING HERE', 'TODO: Add proper error handling')
                changes.append(f"Line {line_number}: Made TODO more specific")
                changes_count += 1
            elif 'THERE WAS A BUG HERE' in line:
                cleaned_line = line.replace('TODO THERE WAS A BUG HERE', 'TODO: Review and test this section for edge cases')
                changes.append(f"Line {line_number}: Improved TODO description")
                changes_count += 1
        
        cleaned_lines.append(cleaned_line)
    
    # Write back if changes were made
    if changes_count > 0:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(cleaned_lines))
    
    return changes_count, changes

def main():
    """Main cleanup function."""
    print("=== Code Cleanup Script ===\n")
    
    # Files to clean
    files_to_clean = [
        "reverie/backend_server/persona/prompt_template/run_gpt_prompt.py",
        "reverie/backend_server/persona/prompt_template/defunct_run_gpt_prompt.py",
    ]
    
    total_debug_changes = 0
    total_todo_changes = 0
    
    for file_path_str in files_to_clean:
        file_path = Path(file_path_str)
        
        if not file_path.exists():
            print(f"⚠️  File not found: {file_path}")
            continue
        
        print(f"🧹 Cleaning {file_path}...")
        
        # Clean debug statements
        debug_changes, debug_details = clean_debug_statements(file_path)
        total_debug_changes += debug_changes
        
        if debug_changes > 0:
            print(f"  ✅ Cleaned {debug_changes} debug statements")
            for detail in debug_details[:3]:  # Show first 3 changes
                print(f"    - {detail}")
            if len(debug_details) > 3:
                print(f"    - ... and {len(debug_details) - 3} more")
        
        # Clean TODO comments
        todo_changes, todo_details = clean_todo_comments(file_path)
        total_todo_changes += todo_changes
        
        if todo_changes > 0:
            print(f"  ✅ Improved {todo_changes} TODO comments")
            for detail in todo_details:
                print(f"    - {detail}")
        
        if debug_changes == 0 and todo_changes == 0:
            print(f"  ✨ No changes needed")
        
        print()
    
    print("=== Cleanup Summary ===")
    print(f"🧹 Total debug statements cleaned: {total_debug_changes}")
    print(f"📝 Total TODO comments improved: {total_todo_changes}")
    print(f"✅ Total files processed: {len(files_to_clean)}")
    
    if total_debug_changes > 0 or total_todo_changes > 0:
        print("\n📋 Next Steps:")
        print("1. Review the changes made")
        print("2. Test the application to ensure functionality")
        print("3. Commit the cleanup changes")
    else:
        print("\n✨ All files are already clean!")

if __name__ == "__main__":
    main()