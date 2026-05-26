"""Configuration generator - main engine for rendering device configs."""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from ..exceptions import GenerationError, ValidationError
from ..integrations.mock_data import get_mock_devices, get_mock_secrets
from ..integrations.secretserver import SecretServerClient
from ..integrations.servicenow import ServiceNowClient
from ..templates import TemplateLoader
from ..utils import merge_configs
from ..utils.validators import validate_device, validate_override_file

logger = logging.getLogger(__name__)


class ConfigGenerator:
    """Main configuration generation engine."""

    def __init__(
        self,
        servicenow_client: Optional[ServiceNowClient] = None,
        secretserver_client: Optional[SecretServerClient] = None,
        template_dir: str = "./templates",
        device_overrides_dir: Optional[str] = None,
    ):
        """Initialize configuration generator.

        Args:
            servicenow_client: ServiceNow API client
            secretserver_client: SecretServer API client
            template_dir: Directory containing Jinja templates
            device_overrides_dir: Directory containing device-specific overrides
        """
        self.servicenow_client = servicenow_client
        self.secretserver_client = secretserver_client
        self.template_loader = TemplateLoader(template_dir)
        self.device_overrides_dir = (
            Path(device_overrides_dir) if device_overrides_dir else None
        )

    def generate(
        self,
        device_filter: Optional[List[str]] = None,
        use_mock: bool = False,
        dry_run: bool = False,
    ) -> Dict[str, Dict[str, Any]]:
        """Generate configurations for all devices.

        Args:
            device_filter: List of device names to filter on
            use_mock: Use mock data instead of APIs
            dry_run: Don't write files, just return results

        Returns:
            Dictionary with results per device
        """
        results = {}

        try:
            # Fetch devices
            devices = self._fetch_devices(device_filter, use_mock)
            logger.info(f"Processing {len(devices)} devices")

            # Generate config for each device
            for device in devices:
                device_name = device.get("name", "unknown")

                try:
                    result = self._generate_device_config(device, dry_run, use_mock)
                    results[device_name] = result
                except Exception as e:
                    logger.error(f"Failed to generate config for {device_name}: {str(e)}")
                    results[device_name] = {
                        "success": False,
                        "error": str(e),
                    }

            return results

        except Exception as e:
            logger.error(f"Configuration generation failed: {str(e)}")
            raise GenerationError(f"Failed to generate configurations: {str(e)}")

    def _fetch_devices(
        self,
        device_filter: Optional[List[str]] = None,
        use_mock: bool = False,
    ) -> List[Dict[str, Any]]:
        """Fetch devices from ServiceNow or mock data.

        Args:
            device_filter: Optional list of device names to fetch
            use_mock: Use mock data if True

        Returns:
            List of device dictionaries
        """
        if use_mock:
            logger.info("Using mock device data")
            devices = get_mock_devices()
        else:
            if not self.servicenow_client:
                raise GenerationError("ServiceNow client not configured")

            devices = self.servicenow_client.fetch_devices(
                device_filter=device_filter
            )

        # Validate devices
        valid_devices = []
        for device in devices:
            if validate_device(device):
                valid_devices.append(device)
            else:
                logger.warning(f"Skipping invalid device: {device.get('name', 'unknown')}")

        return valid_devices

    def _generate_device_config(
        self,
        device: Dict[str, Any],
        dry_run: bool = False,
        use_mock: bool = False,
    ) -> Dict[str, Any]:
        """Generate configuration for a single device.

        Args:
            device: Device dictionary
            dry_run: Don't write files
            use_mock: Use mock secrets if True

        Returns:
            Result dictionary with success and configuration details
        """
        device_name = device.get("name", "unknown")
        logger.info(f"Generating configuration for {device_name}")

        # Load device overrides
        device_config = self._load_device_overrides(device_name)

        # Fetch secrets
        secrets = self._fetch_secrets(device_name, use_mock)

        # Merge configurations
        merged_config = merge_configs(device, device_config, secrets)

        # Render template
        config_text = self.template_loader.render_template(
            manufacturer=device.get("manufacturer", ""),
            operating_system=device.get("os", ""),
            model=device.get("model", ""),
            context=merged_config,
        )

        # Write output if not dry-run
        output_file = None
        if not dry_run:
            output_file = self._write_config(device_name, config_text)

        return {
            "success": True,
            "device_name": device_name,
            "output_file": output_file,
            "config_lines": len(config_text.splitlines()),
        }

    def _load_device_overrides(self, device_name: str) -> Optional[Dict[str, Any]]:
        """Load device-specific override configuration.

        Args:
            device_name: Name of the device

        Returns:
            Override configuration dictionary or None
        """
        if not self.device_overrides_dir:
            return None

        # Try YAML first, then JSON
        yaml_file = self.device_overrides_dir / f"{device_name}.yaml"
        json_file = self.device_overrides_dir / f"{device_name}.json"

        for override_file in [yaml_file, json_file]:
            if override_file.exists():
                try:
                    with open(override_file, "r") as f:
                        if override_file.suffix == ".yaml":
                            override_config = yaml.safe_load(f)
                        else:
                            override_config = json.load(f)

                    if validate_override_file(override_config):
                        logger.info(f"Loaded device overrides from {override_file}")
                        return override_config
                    else:
                        logger.warning(f"Invalid override file: {override_file}")

                except Exception as e:
                    logger.warning(f"Failed to load override file {override_file}: {str(e)}")

        return None

    def _fetch_secrets(
        self,
        device_name: str,
        use_mock: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """Fetch secrets for a device from SecretServer.

        Args:
            device_name: Name of the device
            use_mock: Use mock secrets if True

        Returns:
            Secrets dictionary or None
        """
        if use_mock:
            secrets = get_mock_secrets()
            return secrets.get(device_name)

        if not self.secretserver_client:
            return None

        try:
            # Search for secret by device name
            results = self.secretserver_client.search_secrets(device_name)

            if results:
                secret_id = results[0].get("id")
                secret_data = self.secretserver_client.get_secret(secret_id)
                logger.info(f"Fetched secrets for {device_name} from SecretServer")
                return {"secrets": secret_data}

        except Exception as e:
            logger.warning(f"Failed to fetch secrets for {device_name}: {str(e)}")

        return None

    def _write_config(self, device_name: str, config_text: str) -> str:
        """Write configuration to file.

        Args:
            device_name: Name of the device
            config_text: Configuration text to write

        Returns:
            Path to written file
        """
        from ..config import config

        output_dir = Path(config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / f"{device_name}.conf"

        try:
            with open(output_file, "w") as f:
                f.write(config_text)

            logger.info(f"Wrote configuration to {output_file}")
            return str(output_file)

        except Exception as e:
            logger.error(f"Failed to write configuration file: {str(e)}")
            raise GenerationError(f"Failed to write configuration file: {str(e)}")
