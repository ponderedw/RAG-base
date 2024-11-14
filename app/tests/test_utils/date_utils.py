from contextlib import contextmanager
from datetime import datetime
from typing import Generator
from unittest.mock import MagicMock, patch


@contextmanager
def patch_now(target_path: str, my_now: datetime) -> Generator[MagicMock, None, None]:
    """Patch the `datetime.now` function to return the given, known `my_now`.

    :param target_path: The path to the target to patch.
    :param my_now: The known `datetime.now` to return.
    
    :return: A MagicMock object that can be used to assert the function was called.
    
    This is based on: https://docs.python.org/3/library/unittest.mock-examples.html#partial-mocking
    """

    with patch(target_path) as mock_datetime:
        mock_datetime.now.return_value = my_now
        mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

        yield mock_datetime
