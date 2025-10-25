"""
Version Manager
Semantic versioning and version comparison
"""

import logging
from packaging import version

logger = logging.getLogger(__name__)


class VersionManager:
    """
    Manage semantic versioning for models
    """
    
    def __init__(self):
        """Initialize version manager"""
        logger.info("Version manager initialized")
    
    def parse_version(self, version_string):
        """
        Parse version string
        
        Args:
            version_string: Version string (e.g., "1.2.3")
            
        Returns:
            Version object
        """
        try:
            return version.parse(version_string)
        except Exception as e:
            logger.error(f"Invalid version string: {version_string}")
            raise ValueError(f"Invalid version: {version_string}")
    
    def compare_versions(self, version1, version2):
        """
        Compare two versions
        
        Args:
            version1: First version string
            version2: Second version string
            
        Returns:
            -1 if version1 < version2
             0 if version1 == version2
             1 if version1 > version2
        """
        v1 = self.parse_version(version1)
        v2 = self.parse_version(version2)
        
        if v1 < v2:
            return -1
        elif v1 > v2:
            return 1
        else:
            return 0
    
    def is_newer(self, version1, version2):
        """
        Check if version1 is newer than version2
        
        Args:
            version1: First version string
            version2: Second version string
            
        Returns:
            True if version1 is newer
        """
        return self.compare_versions(version1, version2) > 0
    
    def is_compatible(self, version1, version2):
        """
        Check if versions are compatible (same major version)
        
        Args:
            version1: First version string
            version2: Second version string
            
        Returns:
            True if compatible
        """
        v1 = self.parse_version(version1)
        v2 = self.parse_version(version2)
        
        # Compatible if same major version
        return v1.major == v2.major
    
    def get_latest_version(self, versions):
        """
        Get latest version from list
        
        Args:
            versions: List of version strings
            
        Returns:
            Latest version string
        """
        if not versions:
            return None
        
        parsed_versions = [(v, self.parse_version(v)) for v in versions]
        latest = max(parsed_versions, key=lambda x: x[1])
        
        return latest[0]
    
    def increment_version(self, version_string, part='patch'):
        """
        Increment version
        
        Args:
            version_string: Current version
            part: Part to increment ('major', 'minor', 'patch')
            
        Returns:
            New version string
        """
        v = self.parse_version(version_string)
        
        if part == 'major':
            new_version = f"{v.major + 1}.0.0"
        elif part == 'minor':
            new_version = f"{v.major}.{v.minor + 1}.0"
        elif part == 'patch':
            new_version = f"{v.major}.{v.minor}.{v.micro + 1}"
        else:
            raise ValueError(f"Invalid part: {part}")
        
        logger.info(f"Version incremented: {version_string} -> {new_version}")
        return new_version
    
    def validate_version(self, version_string):
        """
        Validate version string format
        
        Args:
            version_string: Version to validate
            
        Returns:
            True if valid
        """
        try:
            self.parse_version(version_string)
            return True
        except:
            return False
