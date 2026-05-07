def test_mr_imports():
    import mr
    assert mr is not None

def test_cli_main_app_callable():
    from mr.cli.main import app
    assert callable(app)
