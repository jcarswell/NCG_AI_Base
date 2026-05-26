"""Template loader with inheritance support."""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from ..exceptions import TemplateError

logger = logging.getLogger(__name__)


class TemplateLoader:
    """Manages Jinja2 template loading with inheritance by manufacturer, OS, and model."""

    # Template resolution order (highest to lowest priority)
    TEMPLATE_HIERARCHY = [
        "model",      # {manufacturer}/{os}/{model}.j2
        "os_base",    # {manufacturer}/{os}/base.j2
        "mfg_base",   # {manufacturer}/base.j2
        "global",     # base.j2
    ]

    def __init__(self, template_dir: str):
        """Initialize template loader.

        Args:
            template_dir: Root directory containing templates
        """
        self.template_dir = Path(template_dir)

        if not self.template_dir.exists():
            raise TemplateError(f"Template directory does not exist: {template_dir}")

        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        logger.info(f"Template loader initialized with directory: {template_dir}")

    def discover_templates(self) -> List[Path]:
        """Discover all template files in the template directory.

        Returns:
            List of template file paths
        """
        templates = list(self.template_dir.glob("**/*.j2"))
        logger.info(f"Discovered {len(templates)} templates")
        return templates

    def get_template_path(
        self,
        manufacturer: str,
        operating_system: str,
        model: str,
    ) -> Tuple[Optional[str], str]:
        """Resolve template path using inheritance hierarchy.

        Template resolution order (first match wins):
        1. {manufacturer}/{os}/{model}.j2
        2. {manufacturer}/{os}/base.j2
        3. {manufacturer}/base.j2
        4. base.j2

        Args:
            manufacturer: Device manufacturer (e.g., "cisco")
            operating_system: Device OS (e.g., "ios-xe")
            model: Device model (e.g., "c9300-24uxm")

        Returns:
            Tuple of (template_path, resolution_level)

        Raises:
            TemplateError: If no template found in hierarchy
        """
        manufacturer = manufacturer.lower().strip()
        operating_system = operating_system.lower().strip()
        model = model.lower().strip()

        # Build candidate paths in priority order
        candidates = [
            (f"{manufacturer}/{operating_system}/{model}.j2", "model"),
            (f"{manufacturer}/{operating_system}/base.j2", "os_base"),
            (f"{manufacturer}/base.j2", "mfg_base"),
            ("base.j2", "global"),
        ]

        for template_path, level in candidates:
            full_path = self.template_dir / template_path

            if full_path.exists():
                logger.debug(
                    f"Resolved template for {manufacturer}/{operating_system}/{model} "
                    f"to {template_path} (level: {level})"
                )
                return template_path, level

        # No template found
        logger.error(
            f"No template found for {manufacturer}/{operating_system}/{model}"
        )
        raise TemplateError(
            f"No matching template found for {manufacturer}/{operating_system}/{model}"
        )

    def render_template(
        self,
        manufacturer: str,
        operating_system: str,
        model: str,
        context: Dict,
    ) -> str:
        """Render configuration from template with given context.

        Args:
            manufacturer: Device manufacturer
            operating_system: Device OS
            model: Device model
            context: Template context variables

        Returns:
            Rendered configuration string

        Raises:
            TemplateError: If rendering fails
        """
        try:
            template_path, level = self.get_template_path(
                manufacturer, operating_system, model
            )

            logger.info(
                f"Rendering template {template_path} "
                f"(resolved at {level} level)"
            )

            template = self.env.get_template(template_path)
            rendered = template.render(context)

            return rendered

        except TemplateNotFound as e:
            logger.error(f"Template not found: {str(e)}")
            raise TemplateError(f"Template not found: {str(e)}")
        except Exception as e:
            logger.error(f"Template rendering error: {str(e)}")
            raise TemplateError(f"Failed to render template: {str(e)}")

    def validate_template(
        self,
        manufacturer: str,
        operating_system: str,
        model: str,
    ) -> Dict[str, any]:
        """Validate template exists and can be parsed.

        Args:
            manufacturer: Device manufacturer
            operating_system: Device OS
            model: Device model

        Returns:
            Dictionary with validation results

        Raises:
            TemplateError: If validation fails
        """
        try:
            template_path, level = self.get_template_path(
                manufacturer, operating_system, model
            )

            template = self.env.get_template(template_path)

            return {
                "valid": True,
                "template_path": template_path,
                "resolution_level": level,
                "template_name": template.name,
            }

        except TemplateError as e:
            logger.warning(f"Template validation failed: {str(e)}")
            return {
                "valid": False,
                "error": str(e),
                "manufacturer": manufacturer,
                "operating_system": operating_system,
                "model": model,
            }
