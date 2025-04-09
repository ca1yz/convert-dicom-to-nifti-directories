from contextlib import contextmanager

class ConversionError(Exception):
    """Exception raised for errors during DICOM to NIfTI conversion."""
    def __init__(self, message="DICOM to NIfTI conversion failed"):
        self.message = message
        super().__init__(self.message)

@contextmanager
def suppress_stdout_stderr():
    """Context manager to suppress stdout and stderr output."""
    import sys
    from io import StringIO
    
    # Save original stdout/stderr
    original_stdout, original_stderr = sys.stdout, sys.stderr
    # Redirect to StringIO objects
    sys.stdout, sys.stderr = StringIO(), StringIO()
    
    try:
        yield
    finally:
        # Restore original stdout/stderr
        sys.stdout, sys.stderr = original_stdout, original_stderr
