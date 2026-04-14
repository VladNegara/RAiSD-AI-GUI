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
        settings_obj = { # TODO: Mocking QDir exists works but not for QFileInfo.
            "config_file" : "/",
            "environment_manager" : "conda",
            "environment_name" : "utwente",
            "executable" : "/",
            "workspace" : "/home/raisd/workspace"
        }
        return settings_obj

    def test_init_empty(self):
        """Test initialisation with no values."""
        # Act
        settings = Settings()

        # Assert
        with pytest.raises(RuntimeError) as e:
            x = settings.workspace_path == None
        with pytest.raises(RuntimeError) as e:
            x = settings.executable_file_path == None
        with pytest.raises(RuntimeError) as e:
            x = settings.environment_manager == None
        with pytest.raises(RuntimeError) as e:
            x = settings.environment_manager_name == None
        with pytest.raises(RuntimeError) as e:
            x = settings.environment_name == None
        with pytest.raises(RuntimeError) as e:
            x = settings.config_path == None

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

    def test_yaml_file_not_found(self, monkeypatch):
        """Test from yaml with nonexistent file."""
        # Arrange
        monkeypatch.setattr(yaml, "load", lambda: FileNotFoundError)
        settings = Settings()

        # Act
        settings.from_yaml("")

        # Assert
        with pytest.raises(RuntimeError) as e:
            x = settings.workspace_path == None
        assert settings.executable_file_path == Settings.default_executable_file_path
        assert settings.environment_manager == Settings.default_environment_manager
        assert settings.environment_name== Settings.default_environment_name
        assert settings.config_path == Settings.default_config_path
    
