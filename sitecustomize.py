try:
    import pydevd
    DEBUGGING = True
except ImportError:
    DEBUGGING = False

if not DEBUGGING:
    try:
        import coverage
        coverage.process_startup()
    except ImportError:
        pass
