"""Pila simple de deshacer/rehacer para acciones destructivas (borrar tarea/columna/tablero).

Cada acción guarda dos callables: `undo` (revertir) y `redo` (volver a aplicar). Ekin la usa
para restaurar elementos borrados a partir de un snapshot de la base de datos."""


class UndoAction:
    def __init__(self, label, undo, redo):
        self.label = label
        self.undo = undo
        self.redo = redo


class UndoManager:
    def __init__(self, max_depth=40):
        self._undo = []
        self._redo = []
        self.max_depth = max_depth

    def push(self, action):
        self._undo.append(action)
        if len(self._undo) > self.max_depth:
            self._undo.pop(0)
        self._redo.clear()

    def can_undo(self):
        return bool(self._undo)

    def can_redo(self):
        return bool(self._redo)

    def undo(self):
        if not self._undo:
            return None
        action = self._undo.pop()
        action.undo()
        self._redo.append(action)
        return action.label

    def redo(self):
        if not self._redo:
            return None
        action = self._redo.pop()
        action.redo()
        self._undo.append(action)
        return action.label
