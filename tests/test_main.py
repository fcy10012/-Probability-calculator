import pytest
import builtins
from main import show_main_menu

def test_show_main_menu(capsys):
    show_main_menu()
    captured = capsys.readouterr()
    # 检查菜单输出核心内容
    assert "多袋摸球概率计算器" in captured.out
    assert "主菜单" in captured.out

def test_main_quit(monkeypatch):
    # 模拟连续输入‘q’退出
    inputs = iter(['q'])
    monkeypatch.setattr(builtins, 'input', lambda _: next(inputs))
    from main import main
    main()  # 应该能优雅退出
