"""medir_contenedor: solo lo que se puede probar sin un contenedor real."""

from app.medir_contenedor import main


def test_clip_inexistente_da_error_claro_sin_reventar(tmp_path, capsys):
    assert main([str(tmp_path / "no_existe.mov")]) == 2
    assert "No existe el clip" in capsys.readouterr().out
