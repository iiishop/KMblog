"""
PyInstaller runtime hook for uvicorn
Disables uvicorn's default logging configuration to prevent formatter errors
"""

import sys

# Only apply this hook when running as frozen executable
if getattr(sys, 'frozen', False):
    import logging
    
    # Configure basic logging before uvicorn tries to
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s',
        force=True
    )
    
    # Monkey-patch uvicorn's logging config to prevent it from loading
    try:
        import uvicorn.config
        
        # Store original __init__
        original_init = uvicorn.config.Config.__init__
        
        def patched_init(self, *args, **kwargs):
            # Force log_config to None to disable uvicorn's logging setup
            kwargs['log_config'] = None
            kwargs['access_log'] = False
            original_init(self, *args, **kwargs)
        
        # Apply patch
        uvicorn.config.Config.__init__ = patched_init
        
        print("[Hook] Uvicorn logging configuration disabled for frozen environment")
    except Exception as e:
        print(f"[Hook] Warning: Failed to patch uvicorn config: {e}")
