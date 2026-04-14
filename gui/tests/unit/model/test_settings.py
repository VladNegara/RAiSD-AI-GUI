import pytest
import yaml

from PySide6.QtCore import (
    QDir,
    QFileInfo
)

from gui.model.settings import Settings

class TestSettings:
    """Tests for Settings class."""

    @pytest.fixture(autouse=True)
    def setup(self):
        pass

    @pytest.fixture()
    def correct_settings_obj(self) -> dict:
        settings_obj = {
            "config_file" : "/home/raisd/config.yml",
            "environment_manager" : "raise",
            "environment_name" : "utwente",
            "executable" : "/home/raisd/raisdai",
            "workspace" : "/home/raisd/workspace"
        }
        return settings_obj

    def test_init_values(self):
        """Test initialisation with values."""
        # Arrange
        workspace_path = QDir("/home/raisd")
        executable_file_path = QFileInfo("/home/raisd/raisdai")
        environment_manger = 0
        environment_manger_name = Settings.environment_managers[environment_manger]
        environment_name = "raisdai"
        config_path = QFileInfo("/home/raisd/config.yml")

        # Act
        settings = Settings(
            workspace_path=workspace_path,
            executable_file_path=executable_file_path,
            environment_manager=environment_manger,
            environment_name=environment_name,
            config_path=config_path,
        )

        # Assert
        assert settings.workspace_path == workspace_path
        assert settings.executable_file_path == executable_file_path
        assert settings.environment_manager == settings.environment_manager
        assert settings.environment_manager_name == environment_manger_name
        assert settings.environment_name == environment_name
        assert settings.config_path == config_path