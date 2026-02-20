from __future__ import annotations

from gdo.base.Application import Application
from gdo.base.GDO_Module import GDO_Module
from gdo.base.GDT import GDT

from typing import TYPE_CHECKING, Self

from gdo.core.GDO_File import GDO_File
from gdo.favicon.IcoGenerator import IcoGenerator
from gdo.ui.GDT_Color import GDT_Color
from gdo.ui.GDT_Image import GDT_Image

if TYPE_CHECKING:
    from gdo.ui.GDT_Page import GDT_Page


class module_favicon(GDO_Module):

    def gdo_module_config(self) -> list[GDT]:
        return [
            GDT_Image('favicon'),
            GDT_Color('bg_color').initial('EEEEEEFF').not_null().label('bg_color'),
            GDT_Color('theme_color').initial('111111FF').not_null().label('theme_color'),
        ]

    def cfg_favicon_original(self) -> GDO_File | None:
        images = self.get_config_value('favicon')
        return images[0] if images else None

    def cfg_bg_color(self) -> str:
        return self.get_config_val('bg_color')

    def cfg_theme_color(self) -> str:
        return self.get_config_val('theme_color')

    def gdo_subscribe_events(self):
        Application.EVENTS.subscribe("module_favicon_favicon_changed", self.favicon_changed)
        Application.EVENTS.subscribe("module_favicon_bg_color_changed", self.manifest_changed)
        Application.EVENTS.subscribe("module_favicon_theme_color_changed", self.manifest_changed)

    async def favicon_changed(self, module: Self, gdt: GDT_Image):
        if image := module.cfg_favicon_original():
            IcoGenerator.generate(image)

    async def manifest_changed(self, module: Self, gdt: GDT_Image):
        IcoGenerator.generate_manifest()

    def gdo_init_sidebar(self, page: 'GDT_Page'):
        rev = self.CORE_REV
        page.__class__._meta += f"""
        <link rel="icon" href="/assets/favicon.ico?v={rev}" sizes="any">
        <link rel="icon" type="image/png" href="/assets/favicon32.png?v={rev}" sizes="32x32">
        <link rel="apple-touch-icon" href="/assets/favicon180.png?v={rev}">
        <link rel="manifest" href="/assets/manifest.json?v={rev}">
        <meta name="theme-color" content="#{self.cfg_theme_color()[2:]}">
        """
