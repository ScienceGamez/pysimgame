"""Tools to create a menu dynamically from a json/dict input."""
import os
from typing import Any, Dict, Union
from enum import IntEnum, auto
import pygame
import pygame_gui
from pygame_gui.core.interfaces.container_interface import (
    IContainerLikeInterface,
)
from pygame_gui.core.interfaces.manager_interface import IUIManagerInterface
from pygame_gui.core.ui_container import UIContainer
from pygame_gui.core.ui_element import ObjectID, UIElement
from pygame_gui.elements import UIDropDownMenu, UITextBox, UIScrollingContainer
from pygame_gui.elements.ui_button import UIButton
from pygame_gui.elements.ui_horizontal_slider import UIHorizontalSlider
from pygame_gui.elements.ui_label import UILabel
from pygame_gui.windows import UIFileDialog

from pysdgame.utils import logging


class UIColumnContainer(UIScrollingContainer):
    """A vertical layout where you can add elements.

    Similar to usual forms layouts.

    :param vertical_spacing: Vertical spacing between the elements of
        the menu
    """

    # Store the position of the next element to add to the menu
    _next_position: Union[int, float] = 0
    vertical_spacing: Union[int, float]
    _current_file_menu_name: str = None

    def __init__(
        self,
        relative_rect: pygame.Rect,
        manager: IUIManagerInterface,
        *,
        vertical_spacing: Union[int, float] = 0,
        starting_height: int = 1,
        container: Union[IContainerLikeInterface, None] = None,
        parent_element: Union[UIElement, None] = None,
        object_id: Union[ObjectID, str, None] = None,
        anchors: Union[Dict[str, str], None] = None,
        visible: int = 1,
    ):
        super().__init__(
            relative_rect,
            manager,
            starting_height=starting_height,
            container=container,
            anchors=anchors,
            visible=visible,
        )

        self._create_valid_ids(
            container=container,
            parent_element=parent_element,
            object_id=object_id,
            element_id="column_container",
        )

        self.vertical_spacing = vertical_spacing
        self._max_width = 0

    def add_row(self, *elements: UIElement):
        """Add a UI element to the menu."""
        this_position = self._next_position

        max_height = 0  # Stores the height of the elements

        for element in elements:
            element_rect = element.get_relative_rect()
            element.set_relative_position(
                (element.get_relative_rect().left, this_position)
            )
            # Adds the element to the container
            element._setup_container(self)

            # Sets the position of the element on the container
            element._update_absolute_rect_position_from_anchors()

            element._update_container_clip()
            self._max_width = max(
                self._max_width,
                element_rect.width + element.get_relative_rect().left,
            )
            max_height = max(max_height, element_rect.height)

        # Update for the next element
        self._next_position = (
            this_position + max_height + self.vertical_spacing
        )

        # Update the size of the scrollable area, which displays the menu
        self.set_scrollable_area_dimensions(
            (self._max_width, self._next_position)
        )


class RowWrapPolicy(IntEnum):
    """Specify how the form's rows wrap.

    :attr:
        DONT_WRAP_ROWS, Dont wrap (ignore end)
        WRAP_LONG_ROWS, Wrap to the largest label
    """

    DONT_WRAP_ROWS = auto()
    WRAP_LONG_ROWS = auto()


class WidgetWrapPolicy(IntEnum):
    """Specify how the form's wrap the widgets given.

    :attr:
        ORIGINAL_SIZE, The row size adapts to the widget
        ADAPT_TO_LAYOUT, The widget is rescaled to fit the layout
    """

    ORIGINAL_SIZE = auto()
    ADAPT_TO_LAYOUT = auto()


class UIFormLayout(UIColumnContainer):
    def __init__(
        self,
        relative_rect: pygame.Rect,
        manager: IUIManagerInterface,
        *,
        # TODO implement wrap policy
        row_wrap_policy: RowWrapPolicy = RowWrapPolicy.DONT_WRAP_ROWS,
        widget_wrap_policy: RowWrapPolicy = WidgetWrapPolicy.ADAPT_TO_LAYOUT,
        width_ratio: float = 0.5,
        starting_height: int = 1,
        container: Union[IContainerLikeInterface, None] = None,
        parent_element: Union[UIElement, None] = None,
        object_id: Union[ObjectID, str, None] = None,
        anchors: Union[Dict[str, str], None] = None,
        visible: int = 1,
        vertical_spacing: Union[int, float] = 0,
        default_height: Union[int, float] = 40,
    ):
        super().__init__(
            relative_rect,
            manager,
            starting_height=starting_height,
            container=container,
            anchors=anchors,
            visible=visible,
            vertical_spacing=vertical_spacing,
        )

        self._create_valid_ids(
            container=container,
            parent_element=parent_element,
            object_id=object_id,
            element_id="form_layout",
        )

        self.row_wrap_policy = row_wrap_policy
        self.widget_wrap_policy = widget_wrap_policy
        self.label_width = width_ratio * self._view_container.rect.width
        self.default_height = default_height

    def add_row(
        self,
        label: Union[str, None, UIElement],
        *fields: Union[str, None, UIElement],
    ) -> None:
        """Add a row to the form layout.

        Each row is composed by a label and one or more fields.

        :param label: A string or widget.
        :param field: A widget or a string to add, defaults to None
        """
        elements = []

        label_width = (  # Label is extended if No field is given
            self.label_width if fields else self._view_container.rect.width
        )
        if isinstance(label, str):
            label = UILabel(
                pygame.Rect(0, 0, label_width, self.default_height),
                label,
                self.ui_manager,
                parent_element=self,
                container=self,
            )
        if isinstance(label, UIElement):
            label.set_relative_position((0, 0))
            elements.append(label)

        if fields:
            widgets_width = (
                self._view_container.rect.width - self.label_width
            ) / len(fields)

        for i, field in enumerate(fields):

            if isinstance(field, str):
                # Make it a UIElement Label
                field = UILabel(
                    pygame.Rect(
                        self.label_width,
                        0,
                        widgets_width,
                        self.default_height,
                    ),
                    field,
                    self.ui_manager,
                    parent_element=self,
                    container=self,
                )

            if isinstance(field, UIElement):

                # The fields shoud be linearly spaced
                field.set_relative_position(
                    (self.label_width + i * widgets_width, 0)
                )
                if self.widget_wrap_policy == WidgetWrapPolicy.ADAPT_TO_LAYOUT:
                    field.set_dimensions((widgets_width, self.default_height))

                elements.append(field)

        # Add elements to the column layout
        super().add_row(*elements)


class UISettingsMenu(UIContainer):
    """A menu with two colums: one for the text and one for the widget.

    Settings are associated through a specific widget.
    Its possible to feed a dictionary, which is updated when the
    player changes a setting.

    :param relative_rect: A pygame.Rect whose position is relative to
        whatever UIContainer it is
        inside of, if any.
    :param manager: The UIManager that manages this UIElement.
    :param settings: A dictionary containing the settings to be displayed.
    :param starting_height: The starting layer height for this element
        above it's container.
    :param is_window_root_container: True/False flag for whether this
        container is the root container for a UI window.
    :param container: The UIContainer that this
        UIElement is contained within.
    :param parent_element: The element this element 'belongs to'
        in the theming hierarchy.
    :param object_id: A custom defined ID for fine tuning of theming.
    :param anchors: A dictionary describing what this element's
        relative_rect is relative to.
    :param visible: Whether the container and its children
        are visible by default. Warning - it's parent container
        visibility may override this.

    """

    def __init__(
        self,
        relative_rect: pygame.Rect,
        manager: IUIManagerInterface,
        settings: Dict[str, Any] = None,
        *,
        starting_height: int = 1,
        is_window_root_container: bool = False,
        container: Union[IContainerLikeInterface, None] = None,
        parent_element: Union[UIElement, None] = None,
        object_id: Union[ObjectID, str, None] = None,
        anchors: Union[Dict[str, str], None] = None,
        visible: int = 1,
        # The following elements should be considered as style elements TODO
        width_ratio: float = 0.5,
        menu_name: str = "Menu",
        title_height: int = 40,
        elements_height: int = 35,
    ):
        # TODO: modify in UIContainer to be able to change the element_id
        super().__init__(
            relative_rect,
            manager,
            starting_height=starting_height,
            is_window_root_container=is_window_root_container,
            container=container,
            parent_element=parent_element,
            object_id=object_id,
            anchors=anchors,
            visible=visible,
        )

        # Set the proportion of the window
        UITextBox(
            menu_name,
            pygame.Rect(
                0, 0, relative_rect.width - title_height, title_height
            ),
            manager,
            wrap_to_height=True,
            container=self,
            parent_element=self,
        )

        self.keys_container = UIColumnContainer(
            pygame.Rect(
                0,
                title_height,
                relative_rect.width * width_ratio,
                relative_rect.height - title_height,
            ),
            manager,
            container=self,
            parent_element=self,
        )

        self.values_container = UIColumnContainer(
            pygame.Rect(
                relative_rect.width * width_ratio,
                title_height,
                relative_rect.width * (1 - width_ratio),
                relative_rect.height - title_height,
            ),
            manager,
            container=self,
            parent_element=self,
        )

        self.close_window_button = UIButton(
            relative_rect=pygame.Rect(
                -title_height, 0, title_height, title_height
            ),
            text="╳",
            manager=manager,
            container=self,
            parent_element=self,
            object_id="close_button",
            anchors={
                "top": "top",
                "bottom": "top",
                "left": "right",
                "right": "right",
            },
        )

        self.elements_height = elements_height
        self._menu_updates_methods = []

        self._read_settings(settings)

    def _read_settings(self, settings):

        self._settings_json = {}
        if settings is not None:
            for key, value in settings.items():
                try:
                    self.add_setting(key, value)
                except NotImplementedError as err:
                    logging.exception(err)
            # Allow for pointing to original settings
            self._settings_json = settings

    def generate_menu(self, json):
        """Generate the menu from the json file."""
        return NotImplemented

    def add_setting(self, name: str, value: Any):
        """Add a setting parameter to the menu."""
        if name in self._settings_json:
            raise ValueError("'{}' is already in the settings.".format(name))

        # Create rectangles to store the new settings
        key_rect = pygame.Rect(
            0,
            0,
            keys_width := self.keys_container.get_abs_rect().width,
            self.elements_height,
        )
        value_rect = pygame.Rect(
            0,
            0,
            values_width := self.values_container.get_abs_rect().width,
            self.elements_height,
        )
        # Keyword arguments passed to every element
        kwargs = {
            "manager": self.ui_manager,
            "parent_element": self,
        }
        # Adds the key first
        self.keys_container.add_row(
            UITextBox(name, key_rect, container=self.keys_container, **kwargs)
        )

        # Adds the container of the values for the following
        kwargs["container"] = self.values_container
        if value is None:
            # Generates a line with no elements
            ui_elements = [UITextBox("", value_rect, **kwargs)]

        elif isinstance(value, bool):
            drop_down = UIDropDownMenu(
                ["Yes", "No"],
                "Yes" if value else "No",
                value_rect,
                object_id="bool",
                **kwargs,
            )
            ui_elements = [drop_down]
        elif isinstance(value, list) and all(
            isinstance(s, str) for s in value
        ):
            # List of string
            ui_elements = [
                UIDropDownMenu(value, value[0], value_rect, **kwargs)
            ]

        elif isinstance(value, (int, float)):
            # Make a slider with its label
            label_width = 30
            slider = UIHorizontalSlider(value_rect, value, (0, 100), **kwargs)
            label = UILabel(
                pygame.Rect(
                    0.5 * (values_width - label_width),
                    0,
                    label_width,
                    self.elements_height,
                ),
                str(value),
                **kwargs,
            )

            slider.label = label
            ui_elements = [label, slider]

        elif isinstance(value, str):
            if os.path.isfile(value):
                file_text = UITextBox(
                    value,
                    pygame.Rect(
                        0, 0, 2 * values_width / 3, self.elements_height
                    ),
                    **kwargs,
                )
                button = UIButton(
                    pygame.Rect(
                        2 * values_width / 3,
                        0,
                        values_width / 3,
                        self.elements_height,
                    ),
                    "Choose File",
                    object_id="choose_file_button",
                    **kwargs,
                )
                button.file_path = value
                ui_elements = [button, file_text]
            else:
                raise NotImplementedError("TODO")

        else:
            raise NotImplementedError(
                "No settings determined for 'value' of type: {}.".format(
                    type(value)
                )
            )

        # Set the name to the 1rst  ui element so that when the event occurs
        # we know which setting should be changed
        ui_elements[0].name_in_menu = name
        self.values_container.add_row(*ui_elements)
        self.change_setting(name, value)

    def process_event(self, event: pygame.event.Event) -> bool:
        """Process the events relevant for changing of value in the menu.

        :param event: The event to process.

        :return: Should return True if this element makes use of this event.

        """
        if event.type != pygame.USEREVENT:
            return False

        if event.user_type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            event.ui_element.label.set_text("{}".format(event.value))
            self.change_setting(
                event.ui_element.label.name_in_menu, event.value
            )
            return True
        if event.user_type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if event.ui_object_id.endswith("bool"):
                # Case boolean object
                new_value = {"Yes": True, "No": False}[event.text]
            else:
                new_value = event.text
            self.change_setting(event.ui_element.name_in_menu, new_value)
            return True
        if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element is self.close_window_button:
                self.kill()  # Close
            if event.ui_object_id.endswith("choose_file_button"):
                self._current_file_menu_name = event.ui_element.name_in_menu
                UIFileDialog(
                    pygame.Rect(0, 0, *self.get_size()),
                    self.ui_manager,
                    "File for {}".format(event.ui_element.name_in_menu),
                    event.ui_element.file_path,
                )
                return True
        if event.user_type == pygame_gui.UI_FILE_DIALOG_PATH_PICKED:
            # Change a file path after the file dialog is closed
            if self._current_file_menu_name is not None:  # Waiting for input
                self.change_setting(self._current_file_menu_name, event.text)
                self._current_file_menu_name = None

        return False

    def change_setting(self, key: str, value: Any):
        self._settings_json[key] = value
        logging.info(self.get_settings())

    def get_settings(self) -> Dict[str, Any]:
        return self._settings_json

    def update(self, time_delta: float):
        super().update(time_delta)

        if self.alive():
            for method in self._menu_updates_methods:
                method()
