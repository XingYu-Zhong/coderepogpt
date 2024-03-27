
from typing import Optional


def read_file(file_path: str, encoding: Optional[str] = 'utf-8', begin_byte: Optional[int] = None, end_byte: Optional[int] = None) -> Optional[str]:
    try:
        with open(file_path, 'r', encoding=encoding) as file:
            if begin_byte is not None or end_byte is not None:
                file.seek(begin_byte or 0)
                return file.read((end_byte - begin_byte) if end_byte is not None else -1)
            else:
                return file.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None