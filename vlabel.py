from pyglet.text import Label


class VLabel(Label):
    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, visibility):
        self._visible = visibility

        if visibility is True:
            self._update()
            self.update(self._x, self._y)
        else:
            self.delete()