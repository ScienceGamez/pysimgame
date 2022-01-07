"""Earth view model for ills fate."""
from __future__ import annotations

import os
import warnings
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Tuple, Union

import numpy as np
import pygame
from pygame import Rect, Surface, draw, mouse
from pygame.event import Event

import pysimgame
from pysimgame.utils import HINT_DISPLAY, GameComponentManager, logging
from pysimgame.utils.directories import (
    BACKGROUND_DIR_NAME,
    ORIGINAL_BACKGROUND_FILESTEM,
)

from .utils.logging import logger

if TYPE_CHECKING:
    from .game_manager import GameManager
    from .types import RegionsDict

_REGION_COUNTER = 0


class RegionComponent:
    """A region is a that is set on top of the background surface.

    Each region is represented by a polygon.
    """

    # Stores the polygon rectangles
    _rectangles: List[Rect]
    name: str
    color: pygame.Color

    def __init__(
        self, surface, color: pygame.Color, polygons_points=None, name=None
    ):
        """Create a region surface.

        Arguments:
            size: The size of the surface
            color: The color of the region
            polygons_points: List of polygon points or list of list if multiple
                polygons.
        """
        self.surface = surface
        self.color = color
        self._rectangles = []
        if polygons_points is None:
            polygons_points = []
        self.polygons = (
            [polygons_points]
            if len(polygons_points)
            and len(polygons_points[0]) == 2  # If is coordinates
            else polygons_points
        )

        if name is None:
            # Attributes a default name
            global _REGION_COUNTER
            name = "REGION_{}".format(_REGION_COUNTER)
            _REGION_COUNTER += 1

        self.name = name
        logger.debug(f"Created Region Component {self}")

    def __repr__(self) -> str:
        return f"Region(name='{self.name}')"

    def to_dict(self) -> dict:
        """Return a dictionary representation of the region.

        Useful for storing the region in json files.
        """
        return {
            "color": tuple(self.color),
            "name": self.name,
            "polygons": self.polygons,
        }

    def from_dict(region_dict: Dict[str, Any]) -> RegionComponent:
        return RegionComponent(
            None,  # surface will need to be attributed later
            pygame.Color(*region_dict["color"]),
            polygons_points=region_dict["polygons"],
            name=region_dict["name"],
        )

    def collidepoint(self, *args):
        """Return true if a point is inside the region."""
        for rect in self._rectangles:
            if rect.collidepoint(*args):
                return True
        return False

    def show_hovered(self):
        """Make the region glow when hovered."""
        for coords in self.polygons:
            self._rectangles.append(
                draw.polygon(
                    self.surface,
                    self.color,
                    [(coord[0], coord[1]) for coord in coords],
                )
            )

    def show_selected(self):
        """Show the style of selected region."""
        for coords in self.polygons:
            self._rectangles.append(
                draw.lines(
                    self.surface,
                    self.color,
                    True,
                    [(coord[0], coord[1]) for coord in coords],
                    width=10,
                )
            )
            self._rectangles.append(
                draw.polygon(
                    self.surface,
                    self.color,
                    [(coord[0], coord[1]) for coord in coords],
                )
            )

    def show_idle(self):
        """Shows the map on the surface."""
        for coords in self.polygons:
            self._rectangles.append(
                draw.polygon(
                    self.surface,
                    self.color,
                    [(coord[0], coord[1]) for coord in coords],
                )
            )

    def show(self):
        """Shows the map on the surface. Register the places."""
        for coords in self.polygons:
            if len(coords) == 0:
                pass
            elif len(coords) == 1:
                self._rectangles.append(
                    draw.circle(self.surface, self.color, coords[0], 2)
                )
            elif len(coords) == 2:
                self._rectangles.append(
                    draw.line(self.surface, self.color, coords[0], coords[1])
                )
            else:
                self._rectangles.append(
                    draw.polygon(
                        self.surface,
                        self.color,
                        [(coord[0], coord[1]) for coord in coords],
                    )
                )


def validate_regions_dict(
    regions_dict: Dict[str, RegionComponent], display: bool = True
) -> bool:
    """Validate whether the region dict given is valid.

    Validity of a region dict includes the following:

        * Regions names should be different
        * Regions names should have at least one character
        * Regions should have at least one polygon
    """

    # Register whether the regions chosen are a valid set
    valid_set = True
    names = []
    hint_msgs = []  # Tracks the messages to display
    for region in regions_dict.values():
        if region.name in names:
            # Regions names should be different
            valid_set = False
            hint_msgs.append(
                "{} region is present more than once.".format(region.name)
            )
        elif len(region.name) < 1:
            valid_set = False
            hint_msgs.append("A region has a name with no character.")
        elif len(region.polygons) < 1:
            # Regions should have at least one polygon
            valid_set = False
            hint_msgs.append("Region '{}' has no polygon.".format(region.name))
        else:
            # Valid case
            names.append(region.name)

    if display and not valid_set:
        HINT_DISPLAY.show("\n".join(hint_msgs))

    return valid_set


class IlluminatisHQ(RegionComponent):
    """The head quarters of the illuminatis.

    Currently used as None region component selected.
    Can implement easter eggs with it ?
    """

    def __init__(self, surface):
        # Find optimal equidistant triangle using x = sqrt(3)/2*y
        # (0,0), (x, 0), (x/2, y)
        triangle = [
            (0, 0),
            (6, 0),
            (3, 7),
        ]
        super().__init__(surface, "white", triangle, name="")

    def show(self):
        pass

    def show_selected(self):
        pass

    def show_hovered(self):
        pass

    def show_idle(self):
        pass

    def collidepoint(self, *args):
        return False


class SingleRegionComponent(RegionComponent):
    """Represent a region when there is only one region in the game."""

    def __init__(self):
        super().__init__(None, color=pygame.Color(255, 255, 255), name="")


class RegionsManager(GameComponentManager):
    """A view of the earth map."""

    selected_region: RegionComponent
    REGION_SURFACE: Surface
    BACKGROUND_SURFACE: Surface
    HAS_NO_BACKGROUND: bool = False
    REGIONS_DICT: RegionsDict

    _previous_hovered: RegionComponent
    _hovered_region: RegionComponent
    # Position of region surface on MAIN_DISPLAY
    _anchor: Tuple[float, float] = (0, 0)

    def prepare(self):
        self.REGIONS_DICT = self.GAME.REGIONS_DICT
        display_size = self.GAME_MANAGER.MAIN_DISPLAY.get_size()
        # Region surface is transparent over the background
        self.REGION_SURFACE = Surface(display_size, flags=pygame.SRCALPHA)
        self.REGION_SURFACE.fill(pygame.Color(0, 0, 0, 0))
        for region in self.REGIONS_DICT.values():
            region.surface = self.REGION_SURFACE

        self.load_background_image()
        # Simply point to the game dict

        self._previous_hovered = None
        self._hovered_region = None

        if len(self.REGIONS_DICT) > 1:

            self._previous_pressed = False
            self._selected_region_str = None

        else:
            # Only one region
            self._selected_region_str = list(self.REGIONS_DICT.keys())[0]

            def do_nothing(*args):
                # Return False to avoid updating in the listen function
                return False

            # Changes the manager so that it does not handle regions
            setattr(self, "listen", do_nothing)
            setattr(self, "_listen_mouse_events", do_nothing)

        self._update_regions_surface()

    def connect(self):
        pass

    @property
    def selected_region(self) -> RegionComponent:
        """Return the :py:class:`RegionComponent` currently selected."""
        if self._selected_region_str is None:
            return list(self.REGIONS_DICT.values())[0]
        else:
            return self.REGIONS_DICT[self._selected_region_str]

    @selected_region.setter
    def selected_region(self, selected: Union[str, RegionComponent, None]):
        if selected is None:
            self._selected_region_str = None
        elif isinstance(selected, str):
            if selected in self.REGIONS_DICT:
                # Unshow the previously selected
                self._selected_region_str = selected
            else:
                raise KeyError(
                    "{} not in available regions: {}.".format(
                        selected, self.REGIONS_DICT.keys()
                    )
                )
        elif isinstance(selected, RegionComponent):
            self.selected_region = selected.name
        else:
            raise ValueError(
                "Cannot assign selected_region with type {}.".format(
                    type(selected)
                )
            )

    def load_background_image(self):
        """Load the background image if it exists.

        A base image can be given, otherwise this method will resize
        the images to have the requested resolution.
        If no image is given, this will continue.
        """
        backgrounds_dir = Path(
            self.GAME_MANAGER.game.GAME_DIR, BACKGROUND_DIR_NAME
        )

        # The background image takes the full space of the game
        size = self.GAME_MANAGER.MAIN_DISPLAY.get_size()

        image_file = "{}x{}.tga".format(*size)
        img_path = Path(backgrounds_dir, image_file)
        original_img_path = Path(
            backgrounds_dir, ORIGINAL_BACKGROUND_FILESTEM
        ).with_suffix(".tga")
        if not img_path.exists():
            if original_img_path.exists():
                # Convert the image to this format if not yet
                self.logger.info(
                    "Resizing {} to {}.".format(original_img_path, size)
                )
                from .utils.images import resize_image

                resize_image(original_img_path, img_path, size)
            else:
                self.logger.debug(
                    (
                        "No default background set. \n"
                        "Place a file at {}".format(original_img_path)
                    )
                )
                # As no background image file was given
                self.HAS_NO_BACKGROUND = True
                return
        # Add the background on screen
        self.BACKGROUND_SURFACE = pygame.image.load(img_path)
        self.HAS_NO_BACKGROUND = False

        self.logger.info(f"Loaded background {self.BACKGROUND_SURFACE}")

    def _listen_mouse_events(self) -> bool:
        """Listen to mouse clicks and movement.

        When a region is clicked, it should become the selected region.
        Throw a :var:`RegionFocusChanged` when a region is selected.

        The earth view surface listens for the following:
            * Hovering a region
            * Selecting a region by clicking on it
            * Deselecting region by clicking outside

        :return: True if something should change in the display.
        """
        if not self.REGION_SURFACE.get_rect().collidepoint(mouse.get_pos()):
            return False
        hovered_region = None
        # Finds on which region is the mouse
        for region_component in self.REGIONS_DICT.values():
            if region_component.collidepoint(mouse.get_pos()):
                hovered_region = region_component
        # handles clicked event
        pressed = mouse.get_pressed()[0]
        clicked = not pressed and self._previous_pressed
        self._previous_pressed = pressed
        self.logger.debug(f"hovered {hovered_region}")

        if clicked and hovered_region is not None:
            # Select the clicked region
            self.selected_region = hovered_region
            event = Event(
                pysimgame.events.RegionFocusChanged,
                {"region": self.selected_region},
            )
            pygame.event.post(event)
            self.logger.info(f"Selected Region {self.selected_region}")

        if self._previous_hovered == hovered_region:
            return False

        # New region is hover
        self._previous_hovered = hovered_region
        return True

    def process_events(self, event: pygame.event.Event):
        """Listen the events for this manager."""
        match event:
            case pygame.event.EventType(
                type=pysimgame.events.RegionFocusChanged
            ):
                print(event)
                self.selected_region = event.region
            case _:
                pass

    def update(self) -> bool:
        update_regions = self._listen_mouse_events()
        if update_regions:
            self._update_regions_surface()
        if not self.HAS_NO_BACKGROUND:
            # Blit the background if there is one
            self.GAME_MANAGER.MAIN_DISPLAY.blit(
                self.BACKGROUND_SURFACE, self._anchor
            )
        self.GAME_MANAGER.MAIN_DISPLAY.blit(self.REGION_SURFACE, self._anchor)
        return True

    def _update_regions_surface(self):
        # Re-draw the regions on the map
        self.REGION_SURFACE.fill((250, 250, 250, 0))
        for region in self.REGIONS_DICT.values():
            if region == self._hovered_region:
                # region.show_hovered()
                region.show()
            elif region == self.selected_region:
                # region.show_selected()
                region.show()
            else:
                # region.show_idle()
                region.show()
