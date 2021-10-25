"""Introduce several additons to `pygame gui
<https://pygame-gui.readthedocs.io/en/latest/>`_.

A toggle button, which is the same as a
:class:`UIButton <pygame_gui.elements.UIButton>` with additonal
settings. It stores a boolean value that remember which state the button is.


Event:

UI_TOGGLEBUTTON_TOGGLED
.................................................................................................

Fired when a user clicks on a Toggle Button.

 - **'type'** : pygame.USEREVENT
 - **'user_type'** : pygame_gui.UI_TOGGLEBUTTON_TOGGLED
 - **'value'** : The current value of the button (True of False).
 - **'ui_element'** : The :class:`UIToggleButton <.UIToggleButton>` that fired this event.
 - **'ui_object_id'** : The most unique ID for the button that fired this event.

**Example usage**:

.. code-block:: python
   :linenos:

    for event in pygame.event.get():
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_TOGGLEBUTTON_TOGGLED:
                if event.ui_element == toggle_button:
                    print('current value:', event.value)
"""
from typing import Any, Callable, Dict, List, Union
import pygame
import pygame_gui
from pygame_gui.core import ui_element
from pygame_gui.core.drawable_shapes.ellipse_drawable_shape import (
    EllipseDrawableShape,
)
from pygame_gui.core.drawable_shapes.rect_drawable_shape import (
    RectDrawableShape,
)
from pygame_gui.core.drawable_shapes.rounded_rect_drawable_shape import (
    RoundedRectangleShape,
)
from pygame_gui.core.interfaces.container_interface import (
    IContainerLikeInterface,
)
from pygame_gui.core.interfaces.manager_interface import IUIManagerInterface
from pygame_gui.elements.ui_button import UIButton

from pygame_gui._constants import (
    UI_BUTTON_PRESSED,
    UI_BUTTON_DOUBLE_CLICKED,
    UI_BUTTON_START_PRESS,
)
from pygame_gui._constants import UI_BUTTON_ON_HOVERED, UI_BUTTON_ON_UNHOVERED

from itertools import chain

UI_TOGGLEBUTTON_TOGGLED = "ui_button_toggled"


class UIToggleButton(UIButton):
    """Togglable button.

    A toggle button, a lot of the appearance of the button, including
    images to be displayed, is
    setup via the theme file.
    This button is designed to be toggled on or off.

    The button element is reused throughout the UI as part of other
    elements as it happens to be a
    very flexible interactive element.

    :param relative_rect: A rectangle describing the position (relative
        to its container) and dimensions.
    :param text: Text for the button.
    :param manager: The UIManager that manages this element.
    :param container: The container that this element is within. If set
        to None will be the root window's container.
    :param tool_tip_text: Optional tool tip text, can be formatted with
        HTML. If supplied will appear on hover.
    :param starting_height: The height in layers above it's container
        that this element will be placed.
    :param parent_element: The element this element 'belongs to' in the
        theming hierarchy.
    :param object_id: A custom defined ID for fine tuning of theming.
    :param anchors: A dictionary describing what this element's
        relative_rect is relative to.
    :param allow_double_clicks: Enables double clicking on buttons which
        will generate a unique event.
    :param visible: Whether the element is visible by default.
        Warning - container visibility may override this.
    """

    toggled: bool
    switched_event: bool = False

    colors_parameters: List[str] = [
        "normal_bg",
        "hovered_bg",
        "disabled_bg",
        "selected_bg",
        "active_bg",
        "normal_text",
        "hovered_text",
        "disabled_text",
        "selected_text",
        "active_text",
        "normal_border",
        "hovered_border",
        "disabled_border",
        "selected_border",
        "active_border",
    ]

    def __init__(
        self,
        relative_rect: pygame.Rect,
        text: str,
        manager: IUIManagerInterface,
        initial_state: bool = False,
        container: Union[IContainerLikeInterface, None] = None,
        tool_tip_text: Union[str, None] = None,
        starting_height: int = 1,
        parent_element: ui_element = None,
        object_id: Union[ui_element.ObjectID, str, None] = None,
        anchors: Dict[str, str] = None,
        visible: int = 1,
    ):

        self.toggled = initial_state

        super().__init__(
            relative_rect,
            text,
            manager,
            container=container,
            tool_tip_text=tool_tip_text,
            starting_height=starting_height,
            parent_element=parent_element,
            object_id=object_id,
            anchors=anchors,
            allow_double_clicks=False,  # Toggle does not need double clicks
            visible=visible,
        )

    def process_event(self, event: pygame.event.Event) -> bool:
        """
        Handles various interactions with the button.

        :param event: The event to process.

        :return: Return True if we want to consume this event so it is not passed on to the
                 rest of the UI.

        """

        consumed_event = super().process_event(event)

        if consumed_event and self.pressed_event:
            # Toggle the button when it is pressed
            self.toggled = not self.toggled
            self.switched_event = True
            # Send a toggle event
            event_data = {
                "user_type": UI_TOGGLEBUTTON_TOGGLED,
                "ui_element": self,
                "ui_object_id": self.most_specific_combined_id,
                "value": self.toggled,
            }
            pygame.event.post(pygame.event.Event(pygame.USEREVENT, event_data))
            self.rebuild_from_changed_theme_data()

        return consumed_event

    def update(self, time_delta: float):
        super().update(time_delta)
        if self.alive():
            # clear the event for the new cycle
            self.switched_event = False

    def add_if_toggled(self, s: str):
        return "toggled_" + s if self.toggled else s

    def rebuild_from_changed_theme_data(self):
        """Rebuild the button if any theming parameters have changed.

        Check if any theming parameters have changed, and if so triggers
        a full Rebuild of the button's drawable shape.

        As each different types of parameters has a different implementation
        we summarize here how they are handled for the different
        style when toggled.
        - colors: direcly in this method
        - font: TODO
        - misc: _check_misc_theme_data_changed
        - images: TODO
        """
        ui_element.UIElement.rebuild_from_changed_theme_data(self)
        has_any_changed = False

        font = self.ui_theme.get_font(self.combined_element_ids)
        if font != self.font:
            self.font = font
            has_any_changed = True

        cols = {
            el_name: self.ui_theme.get_colour_or_gradient(
                # Workaround for the colors, to change toggled
                self.add_if_toggled(el_name),
                self.combined_element_ids,
            )
            for el_name in self.colors_parameters
        }

        if cols != self.colours:
            self.colours = cols
            has_any_changed = True

        if self._set_any_images_from_theme():
            has_any_changed = True

        # misc
        if self._check_misc_theme_data_changed(
            attribute_name="shape",
            default_value="rectangle",
            casting_func=str,
            allowed_values=["rectangle", "rounded_rectangle", "ellipse"],
        ):
            has_any_changed = True

        if self._check_shape_theming_changed(
            defaults={
                "border_width": 1,
                "shadow_width": 2,
                "shape_corner_radius": 2,
            }
        ):
            has_any_changed = True

        if self._check_misc_theme_data_changed(
            attribute_name="tool_tip_delay",
            default_value=1.0,
            casting_func=float,
        ):
            has_any_changed = True

        if self._check_text_alignment_theming():
            has_any_changed = True

        try:
            state_transitions = self.ui_theme.get_misc_data(
                "state_transitions", self.combined_element_ids
            )
        except LookupError:
            self.state_transitions = {}
        else:
            if isinstance(state_transitions, dict):
                for key in state_transitions:
                    states = key.split("_")
                    if len(states) == 2:
                        start_state = states[0]
                        target_state = states[1]
                        try:
                            duration = float(state_transitions[key])
                        except ValueError:
                            duration = 0.0
                        self.state_transitions[
                            (start_state, target_state)
                        ] = duration

        if has_any_changed:
            self.rebuild()

    def rebuild(self):
        return super().rebuild()

    def _check_misc_theme_data_changed(
        self,
        attribute_name: str,
        default_value: Any,
        casting_func: Callable[[Any], Any],
        allowed_values: Union[List, None] = None,
    ) -> bool:

        has_changed = False
        attribute_value = default_value
        try:
            attribute_value = casting_func(
                self.ui_theme.get_misc_data(
                    # Adds the toggled name
                    self.add_if_toggled(attribute_name),
                    self.combined_element_ids,
                )
            )
        except (LookupError, ValueError):
            attribute_value = default_value
        finally:
            if allowed_values and attribute_value not in allowed_values:
                attribute_value = default_value

            if attribute_value != getattr(self, attribute_name, default_value):
                setattr(self, attribute_name, attribute_value)
                has_changed = True
        return has_changed
