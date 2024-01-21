
from typing import List


def is_match_error_warn(content: str, match_excludes: List[str]) -> bool:
    return is_match_strings(content, match_strings=["error", "ERROR", "warn", "WARN"], match_excludes=match_excludes)


def is_match_strings(content: str, match_strings: List[str], match_excludes: List[str]) -> bool:

    for content_line in content.split("\n"):
        for match_string in match_strings:
            if match_string in content_line:
                return is_match_wo_excludes(content_line=content_line, match_excludes=match_excludes)

    return False


def is_match_wo_excludes(content_line: str, match_excludes: List[str]) -> bool:
    for match_exclude in match_excludes:
        if match_exclude in content_line:
            return False

    return True
