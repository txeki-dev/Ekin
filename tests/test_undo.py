"""Pruebas unitarias para UndoManager y UndoAction."""
from undo import UndoManager, UndoAction


def test_undo_manager_initial_state():
    mgr = UndoManager(max_depth=5)
    assert not mgr.can_undo()
    assert not mgr.can_redo()
    assert mgr.undo() is None
    assert mgr.redo() is None


def test_undo_manager_push_enables_can_undo():
    mgr = UndoManager(max_depth=5)
    action = UndoAction("Borrar tarea", lambda: None, lambda: None)
    mgr.push(action)
    assert mgr.can_undo()
    assert not mgr.can_redo()


def test_undo_manager_undo_and_redo_lifecycle():
    state = {"count": 0}

    def do_undo():
        state["count"] -= 1

    def do_redo():
        state["count"] += 1

    mgr = UndoManager(max_depth=5)
    action = UndoAction("Modificar valor", do_undo, do_redo)
    mgr.push(action)

    assert mgr.can_undo()
    assert not mgr.can_redo()

    # Ejecutar Undo
    label = mgr.undo()
    assert label == "Modificar valor"
    assert state["count"] == -1
    assert not mgr.can_undo()
    assert mgr.can_redo()

    # Ejecutar Redo
    label = mgr.redo()
    assert label == "Modificar valor"
    assert state["count"] == 0
    assert mgr.can_undo()
    assert not mgr.can_redo()


def test_undo_manager_push_clears_redo():
    mgr = UndoManager(max_depth=5)
    action1 = UndoAction("A1", lambda: None, lambda: None)
    action2 = UndoAction("A2", lambda: None, lambda: None)

    mgr.push(action1)
    mgr.undo()
    assert mgr.can_redo()

    mgr.push(action2)
    assert not mgr.can_redo()
    assert mgr.can_undo()


def test_undo_manager_max_depth():
    mgr = UndoManager(max_depth=2)
    a1 = UndoAction("A1", lambda: None, lambda: None)
    a2 = UndoAction("A2", lambda: None, lambda: None)
    a3 = UndoAction("A3", lambda: None, lambda: None)

    mgr.push(a1)
    mgr.push(a2)
    mgr.push(a3)

    assert len(mgr._undo) == 2
    assert mgr._undo[0].label == "A2"
    assert mgr._undo[1].label == "A3"
