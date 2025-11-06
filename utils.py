# utils.py
import os
import sys
import platform


def clear_screen():
    """Clear the terminal screen"""
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')


def pause():
    """Pause and wait for user input"""
    input("\nPress Enter to continue...")


def validate_input(prompt: str, input_type: str = "string", 
                   min_val=None, max_val=None) -> any:
    """
    Validate user input
    
    Args:
        prompt: Input prompt message
        input_type: Type of input expected ('string', 'int', 'float', 'bool')
        min_val: Minimum value (for numeric types)
        max_val: Maximum value (for numeric types)
        
    Returns:
        Validated input value
    """
    while True:
        try:
            value = input(prompt).strip()
            
            if input_type == "string":
                if value:
                    return value
                else:
                    print("Input cannot be empty!")
                    continue
            
            elif input_type == "int":
                num = int(value)
                if min_val is not None and num < min_val:
                    print(f"Value must be at least {min_val}!")
                    continue
                if max_val is not None and num > max_val:
                    print(f"Value must not exceed {max_val}!")
                    continue
                return num
            
            elif input_type == "float":
                num = float(value)
                if min_val is not None and num < min_val:
                    print(f"Value must be at least {min_val}!")
                    continue
                if max_val is not None and num > max_val:
                    print(f"Value must not exceed {max_val}!")
                    continue
                return num
            
            elif input_type == "bool":
                if value.lower() in ['yes', 'y', 'true', '1']:
                    return True
                elif value.lower() in ['no', 'n', 'false', '0']:
                    return False
                else:
                    print("Please enter yes/no!")
                    continue
        
        except ValueError:
            print(f"Invalid {input_type} input! Please try again.")
            continue
        except KeyboardInterrupt:
            print("\n\nOperation cancelled by user.")
            sys.exit(0)


def format_percentage(value: float, decimals: int = 2) -> str:
    """
    Format a decimal value as percentage
    
    Args:
        value: Decimal value (0.0 to 1.0)
        decimals: Number of decimal places
        
    Returns:
        Formatted percentage string
    """
    return f"{value * 100:.{decimals}f}%"


def format_table(headers: list, rows: list, col_widths: list = None) -> str:
    """
    Format data as a table
    
    Args:
        headers: List of header strings
        rows: List of row lists
        col_widths: Optional list of column widths
        
    Returns:
        Formatted table string
    """
    if not col_widths:
        col_widths = [max(len(str(row[i])) for row in [headers] + rows) + 2 
                     for i in range(len(headers))]
    
    # Header
    table = []
    header_row = "".join(str(headers[i]).ljust(col_widths[i]) for i in range(len(headers)))
    table.append(header_row)
    table.append("-" * len(header_row))
    
    # Rows
    for row in rows:
        table.append("".join(str(row[i]).ljust(col_widths[i]) for i in range(len(row))))
    
    return "\n".join(table)


def confirm_action(message: str) -> bool:
    """
    Ask user to confirm an action
    
    Args:
        message: Confirmation message
        
    Returns:
        bool: True if confirmed, False otherwise
    """
    response = input(f"{message} (yes/no): ").strip().lower()
    return response in ['yes', 'y']


def display_menu(title: str, options: list) -> int:
    """
    Display a menu and get user choice
    
    Args:
        title: Menu title
        options: List of menu option strings
        
    Returns:
        Selected option number (1-indexed)
    """
    clear_screen()
    print("=" * 60)
    print(title.center(60))
    print("=" * 60)
    print()
    
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")
    
    print("-" * 60)
    
    while True:
        try:
            choice = int(input(f"\nEnter your choice (1-{len(options)}): "))
            if 1 <= choice <= len(options):
                return choice
            else:
                print(f"Please enter a number between 1 and {len(options)}!")
        except ValueError:
            print("Invalid input! Please enter a number.")
        except KeyboardInterrupt:
            print("\n\nOperation cancelled.")
            return -1


def print_success(message: str):
    """Print a success message"""
    print(f"\n✓ {message}")


def print_error(message: str):
    """Print an error message"""
    print(f"\n❌ {message}")


def print_warning(message: str):
    """Print a warning message"""
    print(f"\n⚠ {message}")


def print_info(message: str):
    """Print an info message"""
    print(f"\nℹ {message}")


def create_banner(text: str, width: int = 70, char: str = "=") -> str:
    """
    Create a banner with text
    
    Args:
        text: Banner text
        width: Banner width
        char: Character to use for border
        
    Returns:
        Formatted banner string
    """
    lines = []
    lines.append(char * width)
    lines.append(text.center(width))
    lines.append(char * width)
    return "\n".join(lines)


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate a string to maximum length
    
    Args:
        text: String to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing invalid characters
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename


def get_file_size_mb(filepath: str) -> float:
    """
    Get file size in MB
    
    Args:
        filepath: Path to file
        
    Returns:
        File size in MB
    """
    if os.path.exists(filepath):
        size_bytes = os.path.getsize(filepath)
        return size_bytes / (1024 * 1024)
    return 0.0