"""Earth view model for ills fate."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List
import warnings
import pygame
from pygame import Rect, Surface, draw, mouse
import numpy as np

from typing import TYPE_CHECKING

from pysdgame.utils import HINT_DISPLAY
from pysdgame.utils.directories import (
    BACKGROUND_DIR_NAME,
    ORIGINAL_BACKGROUND_FILESTEM,
)
from .utils.logging import logger

if TYPE_CHECKING:
    from .game_manager import GameManager

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

        self.show()

        if name is None:
            # Attributes a default name
            global _REGION_COUNTER
            name = "REGION_{}".format(_REGION_COUNTER)
            _REGION_COUNTER += 1

        self.name = name

    def __repr__(self) -> str:
        return "-".join((self.name, str(self.color)))

    def to_dict(self) -> dict:
        """Return a dictionary representation of the region.

        Useful for storing the region in json files.
        """
        return {
            "color": tuple(self.color),
            "name": self.name,
            "polygons": self.polygons,
        }

    def from_dict(self, region_dict: Dict[str, Any]) -> RegionComponent:
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
            draw.polygon(
                self.surface,
                (*self.color, 150),
                [(coord[0], coord[1]) for coord in coords],
            )

    def show_selected(self):
        """Show the style of selected region."""
        for coords in self.polygons:
            draw.lines(
                self.surface,
                (*self.color, 250),
                True,
                [(coord[0], coord[1]) for coord in coords],
                width=10,
            )
            draw.polygon(
                self.surface,
                (*self.color, 200),
                [(coord[0], coord[1]) for coord in coords],
            )

    def show_idle(self):
        """Shows the map on the surface."""
        for coords in self.polygons:
            draw.polygon(
                self.surface,
                (*self.color, 100),
                [(coord[0], coord[1]) for coord in coords],
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


class RegionsSurface(pygame.Surface):
    """A view of the earth map."""

    region_components: Dict[str, RegionComponent] = {}
    region_surface: Surface

    HAS_NO_BACKGROUND: bool = False

    _previous_hovered: str = None

    def __init__(
        self,
        game_manager: GameManager,
        *args,
        **kwargs,
    ) -> None:
        """Initialize the regions surface.

        Same args as pygame.Surface().
        """
        super().__init__(game_manager.MAIN_DISPLAY.get_size(), *args, **kwargs)
        self.game_manager = game_manager

        self.load_background_image()

        if len(game_manager.game.REGIONS_DICT) > 1:
            # Set up the manager for multiple regions
            self.load_regions()

            self._previous_pressed = False
            self._selected_region_str = None
        else:
            # Only one region

            def do_nothing(*args):
                # Return False to avoid updating in the listen function
                return False

            # Changes the manager so that it does not handle regions
            setattr(self, "listen", do_nothing)

    @property
    def selected_region(self):
        """Return the :py:class:`RegionComponent` currently selected."""
        return self.region_components[self._selected_region_str]

    @selected_region.setter
    def selected_region(self, selected):
        if selected is None:
            self._selected_region_str = None
        elif isinstance(selected, str):
            if selected in self.region_components:
                # Unshow the previously selected
                self._selected_region_str = selected
            else:
                raise KeyError(
                    "{} not in available regions: {}.".format(
                        selected, self.region_components.keys()
                    )
                )
        else:
            raise ValueError(
                "Cannot assign selected_region with type {}.".format(
                    type(selected)
                )
            )

    def on_region_selected(self, region: RegionComponent) -> None:
        """Called when a region is selected.

        Can be overriden to do any thing particular.
        """
        pass

    def load_background_image(self):
        """Load the background image if it exists.

        A base image can be given, otherwise this method will resize
        the images to have the requested resolution.
        If no image is given, this will continue.
        """
        backgrounds_dir = Path(
            self.game_manager.game.GAME_DIR, BACKGROUND_DIR_NAME
        )

        # The background image takes the full space of the game
        size = self.game_manager.MAIN_DISPLAY.get_size()

        image_file = "{}x{}.tga".format(*size)
        img_path = Path(backgrounds_dir, image_file)
        original_img_path = Path(
            backgrounds_dir, ORIGINAL_BACKGROUND_FILESTEM
        ).with_suffix(".tga")
        if not img_path.exists():
            if original_img_path.exists():
                # Convert the image to this format if not yet
                logger.info(
                    "Resizing {} to {}.".format(original_img_path, size)
                )
                from .utils.images import resize_image

                resize_image(original_img_path, img_path, size)
            else:
                logger.debug(
                    (
                        "No default background set. \n"
                        "Place a file at {}".format(original_img_path)
                    )
                )
                # As no background image file was given
                return
        # Add the background on screen
        self.background_image = pygame.image.load(img_path)
        self.blit(self.background_image, (0, 0))
        logger.info(f"Loaded background {self.background_image}")

    def load_regions(self):
        """Load the regions polygons.

        At the moment only load available regions but future implementation
        could read from official geo data maps and show regions as requested
        by the models.
        """
        regions_dir = os.path.join(self.game_manager.GAME_DIR, "regions")
        if not os.path.isdir(regions_dir):
            os.mkdir(regions_dir)
        # TODO: change that to get the default resolution from the regions folder
        regions_resolution = self.game_manager
        regions_files = [
            os.path.join(regions_dir, file) for file in os.listdir(regions_dir)
        ]
        self.region_surface = pygame.Surface(self.get_size(), pygame.SRCALPHA)
        # Makes a transparent background of the surface
        transparent = (255, 255, 255, 0)
        self.region_surface.fill(transparent)
        for file in regions_files:
            x, y = np.loadtxt(file, delimiter=",", unpack=True)
            # Rescales
            x = x / regions_resolution[0] * self.get_size()[0]
            y = y / regions_resolution[1] * self.get_size()[1]

            region_component = RegionComponent(
                self.region_surface,
                np.random.randint(0, 256, size=3),
                [(x_, y_) for x_, y_ in zip(x, y)],
            )
            # Stores each regions in a dictionary
            self.region_components[region_component.name] = region_component

        # Adds a None region
        self.region_components[None] = IlluminatisHQ(
            self.region_surface,
        )
        self.blit(self.region_surface, (0, 0))

    def listen(self, events) -> bool:
        """Listen the events concerning the earth surface.

        The earth view surface listens for the following:
            * Hovering a region
            * Selecting a region by clicking on it
            * Deselecting region by clicking outside

        :return: True if the region surface has been updated.


        """
        logger.debug(f"[START] Listening : {events}")
        if not self.get_rect().collidepoint(mouse.get_pos()):
            return False
        # Finds on which region is the mouse
        hovered = None
        for name, region_component in self.region_components.items():
            if region_component.collidepoint(mouse.get_pos()):
                hovered = name
        # handles clicked event
        pressed = mouse.get_pressed()[0]
        clicked = not pressed and self._previous_pressed
        self._previous_pressed = pressed

        if clicked:
            # Select the clicked region
            self.selected_region = hovered
            self.on_region_selected(self.selected_region)

        if self._previous_hovered == hovered:
            return False

        # New region is hover
        self._previous_hovered = hovered
        # Show, the regions on the map
        self.region_surface.fill((250, 250, 250, 0))
        for name, region_component in self.region_components.items():
            if name == hovered:
                region_component.show_hovered()
            elif name == self.selected_region.name:
                region_component.show_selected()
            else:
                region_component.show_idle()

        self.blit(self.earth_map_img, (0, 0))
        self.blit(self.region_surface, (0, 0))

        logger.debug(f"[FINISHED] Listening : {events}")

        return True
