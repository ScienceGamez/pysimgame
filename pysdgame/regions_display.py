"""Earth view model for ills fate."""
from __future__ import annotations

import os
from typing import Dict, List
import warnings
import pygame
from pygame import Rect, Surface, draw, mouse
import numpy as np

from typing import TYPE_CHECKING
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
    color: np.ndarray  # Shape (3,)

    def __init__(self, surface, color, polygons_points, name=None):
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
        self.polygons = (
            [polygons_points] if
            len(polygons_points[0]) == 2  # If is coordinates
            else polygons_points
        )

        self.show()

        if name is None:
            # Attributes a default name
            global _REGION_COUNTER
            name = 'REGION_{}'.format(_REGION_COUNTER)
            _REGION_COUNTER += 1

        self.name = name

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
                width=10
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
                [(coord[0], coord[1]) for coord in coords]
            )

    def show(self):
        """Shows the map on the surface. Register the places."""
        for coords in self.polygons:
            self._rectangles.append(draw.polygon(
                self.surface,
                (*self.color, 100),
                [(coord[0], coord[1]) for coord in coords]
            ))


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
        super().__init__(
            surface, 'white', triangle, name=''
        )

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


class SingleRegion:
    """Represent a region when there is only one region in the game."""

    def __init__(self, color=np.array([0, 0, 255])) -> None:
        """Create a region for a single model."""
        self.color = color


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
        on_region_selected=lambda: None,
        **kwargs
    ) -> None:
        """Initialize the earth.

        Same args as pygame.Surface().
        """
        super().__init__(
            game_manager.PYGAME_SETTINGS["Resolution"], *args, **kwargs
        )
        self.game_manager = game_manager

        self.load_background_image()

        if not game_manager.PYGAME_SETTINGS["Single Region"]:
            # Set up the manager for multiple regions
            self.load_regions()
            self.on_region_selected = on_region_selected
            self._previous_pressed = False
            self._selected_region_str = None
        else:
            # Only one region
            self.region_components['Single Region'] = SingleRegion()

            def do_nothing(*args):
                # Return False to avoid updating in the listen function
                return False
            # Changes the manager so that it does not handle regions
            setattr(self, 'listen', do_nothing)

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

    def load_background_image(self):
        """Load the background image if it exists.

        A base image can be given, otherwise this method will resize
        the images to have the requested resolution.
        If no image is given, this will continue.
        """
        backgrounds_dir = os.path.join(
            self.game_manager.GAME_DIR,
            'backgrounds',
        )
        if not os.path.isdir(backgrounds_dir):
            os.mkdir(backgrounds_dir)

        # The background image takes the full space of the game
        size = self.game_manager.PYGAME_SETTINGS["Resolution"]

        image_file = "background_{}x{}.jpg".format(
            size[0], size[1]
        )
        img_path = os.path.join(
            self.game_manager.GAME_DIR,
            'backgrounds',
            image_file
        )
        original_img_path = os.path.join(
            self.game_manager.GAME_DIR,
            'backgrounds',
            'background.jpg'
        )
        if not os.path.isfile(img_path):
            if os.path.isfile(original_img_path):
                # Convert the image to this format if not yet
                print('Resizing {} to {}.'.format(original_img_path, size))
                from .utils.images import resize_image
                resize_image(original_img_path, *size)
            else:
                warnings.warn((
                    "No default background set. \n"
                    "Place a file at {}".format(original_img_path)
                ))
                self.HAS_NO_BACKGROUND
                # As no background image file was given
                return

        self.earth_map_img = pygame.image.load(img_path)
        self.blit(self.earth_map_img, (0, 0))

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
            os.path.join(regions_dir, file)
            for file in os.listdir(regions_dir)
        ]
        self.region_surface = pygame.Surface(self.get_size(),  pygame.SRCALPHA)
        # Makes a transparent background of the surface
        transparent = (255, 255, 255, 0)
        self.region_surface.fill(transparent)
        for file in regions_files:
            x, y = np.loadtxt(file, delimiter=',', unpack=True)
            # Rescales
            x = x / regions_resolution[0] * self.get_size()[0]
            y = y / regions_resolution[1] * self.get_size()[1]

            region_component = RegionComponent(
                self.region_surface,
                np.random.randint(0, 256, size=3),
                [(x_, y_) for x_, y_ in zip(x, y)]
            )
            # Stores each regions in a dictionary
            self.region_components[region_component.name] = region_component

        # Adds a None region
        self.region_components[None] = IlluminatisHQ(
            self.region_surface,
        )
        self.blit(self.region_surface, (0, 0))

    def listen(self, events):
        """Listen the events concerning the earth surface.

        The earth view surface listens for the following:
            * Hovering a region
            * Selecting a region by clicking on it
            * Deselecting region by clicking outside


        """
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
            self.on_region_selected()

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
        return True