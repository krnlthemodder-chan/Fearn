#!/usr/bin/env python3
"""
Fearn Repository Library Manager
Integrates multiple signing repositories (ksign, UnkeySign, SignTools, etc.)
Provides unified interface for certificate and app management across repos
"""

import json
import requests
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum


class RepoType(Enum):
    """Supported repository types"""
    KSIGN = "ksign"
    UNKEYSIN = "unkeySign"
    SIGNTOOLS = "signTools"
    SIGNLY = "signly"
    APPLESIGN = "appleSign"
    CODESIGN = "codeSiGN"
    CUSTOM = "custom"


@dataclass
class Repository:
    """Repository configuration"""
    name: str
    repo_type: RepoType
    url: str
    api_endpoint: str
    auth_token: Optional[str] = None
    description: str = ""
    enabled: bool = True


class RepoLibraryManager:
    """Manages multiple signing repositories"""
    
    def __init__(self):
        self.repositories: List[Repository] = []
        self.load_default_repos()
    
    def load_default_repos(self):
        """Load default popular signing repositories"""
        self.repositories = [
            Repository(
                name="ksign",
                repo_type=RepoType.KSIGN,
                url="https://ksign.dev",
                api_endpoint="https://api.ksign.dev/v1",
                description="Lightweight iOS app signing service with certificate management"
            ),
            Repository(
                name="UnkeySign",
                repo_type=RepoType.UNKEYSIN,
                url="https://unkeysign.com",
                api_endpoint="https://api.unkeysign.com/v2",
                description="Enterprise-grade code signing with multi-platform support"
            ),
            Repository(
                name="SignTools",
                repo_type=RepoType.SIGNTOOLS,
                url="https://signtools.io",
                api_endpoint="https://api.signtools.io",
                description="Automated app signing and build system"
            ),
            Repository(
                name="SignLy",
                repo_type=RepoType.SIGNLY,
                url="https://signly.io",
                api_endpoint="https://api.signly.io/v1",
                description="Cloud-based iOS signing with sideloading support"
            ),
            Repository(
                name="AppleSign",
                repo_type=RepoType.APPLESIGN,
                url="https://applesign.dev",
                api_endpoint="https://api.applesign.dev/v1",
                description="Advanced certificate and provisioning management"
            ),
            Repository(
                name="codeSiGN",
                repo_type=RepoType.CODESIGN,
                url="https://codesign.app",
                api_endpoint="https://api.codesign.app/v1",
                description="Multi-account signing service with batch processing"
            )
        ]
    
    def add_custom_repo(self, name: str, url: str, api_endpoint: str, 
                       auth_token: Optional[str] = None, 
                       description: str = "") -> Repository:
        """Add custom signing repository"""
        repo = Repository(
            name=name,
            repo_type=RepoType.CUSTOM,
            url=url,
            api_endpoint=api_endpoint,
            auth_token=auth_token,
            description=description
        )
        self.repositories.append(repo)
        return repo
    
    def get_repo(self, name: str) -> Optional[Repository]:
        """Get repository by name"""
        for repo in self.repositories:
            if repo.name.lower() == name.lower():
                return repo
        return None
    
    def list_repos(self) -> List[Dict]:
        """List all available repositories"""
        return [
            {
                "name": repo.name,
                "type": repo.repo_type.value,
                "url": repo.url,
                "description": repo.description,
                "enabled": repo.enabled
            }
            for repo in self.repositories
        ]
    
    def enable_repo(self, name: str) -> bool:
        """Enable repository"""
        repo = self.get_repo(name)
        if repo:
            repo.enabled = True
            return True
        return False
    
    def disable_repo(self, name: str) -> bool:
        """Disable repository"""
        repo = self.get_repo(name)
        if repo:
            repo.enabled = False
            return True
        return False
    
    def get_certificates(self, repo_name: str, auth_token: Optional[str] = None) -> List[Dict]:
        """Fetch certificates from repository"""
        repo = self.get_repo(repo_name)
        if not repo or not repo.enabled:
            return []
        
        token = auth_token or repo.auth_token
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        
        try:
            response = requests.get(
                f"{repo.api_endpoint}/certificates",
                headers=headers,
                timeout=10
            )
            return response.json() if response.status_code == 200 else []
        except Exception as e:
            print(f"Error fetching certificates from {repo_name}: {e}")
            return []
    
    def get_apps(self, repo_name: str, auth_token: Optional[str] = None) -> List[Dict]:
        """Fetch available apps from repository"""
        repo = self.get_repo(repo_name)
        if not repo or not repo.enabled:
            return []
        
        token = auth_token or repo.auth_token
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        
        try:
            response = requests.get(
                f"{repo.api_endpoint}/apps",
                headers=headers,
                timeout=10
            )
            return response.json() if response.status_code == 200 else []
        except Exception as e:
            print(f"Error fetching apps from {repo_name}: {e}")
            return []
    
    def sign_with_repo(self, repo_name: str, app_path: str, 
                       certificate_id: str, **kwargs) -> Dict:
        """Sign app using specific repository"""
        repo = self.get_repo(repo_name)
        if not repo or not repo.enabled:
            return {"success": False, "error": f"Repository {repo_name} not found or disabled"}
        
        token = kwargs.get('auth_token') or repo.auth_token
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        
        try:
            payload = {
                "app_path": app_path,
                "certificate_id": certificate_id,
                "provisioning_profile": kwargs.get('provisioning_profile'),
                "entitlements": kwargs.get('entitlements', {})
            }
            
            response = requests.post(
                f"{repo.api_endpoint}/sign",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            return response.json() if response.status_code in [200, 201] else {
                "success": False,
                "error": f"Signing failed: {response.text}"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def search_repos(self, query: str) -> List[Dict]:
        """Search across all enabled repositories"""
        results = []
        for repo in self.repositories:
            if not repo.enabled:
                continue
            
            # Search in repo metadata
            if query.lower() in repo.name.lower() or query.lower() in repo.description.lower():
                results.append({
                    "repo": repo.name,
                    "match_type": "metadata",
                    "url": repo.url
                })
        
        return results


class RepoLibraryConfig:
    """Configuration management for repository library"""
    
    def __init__(self, config_file: str = "repo_library.json"):
        self.config_file = config_file
        self.config = {}
        self.load_config()
    
    def load_config(self):
        """Load configuration from file"""
        try:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.create_default_config()
    
    def create_default_config(self):
        """Create default configuration file"""
        self.config = {
            "version": "3.0.0",
            "fearn": {
                "auto_sync": True,
                "sync_interval": 3600,
                "cache_certificates": True
            },
            "repositories": {
                "ksign": {
                    "enabled": True,
                    "priority": 1,
                    "timeout": 10
                },
                "unkeysign": {
                    "enabled": True,
                    "priority": 2,
                    "timeout": 15
                },
                "signtools": {
                    "enabled": True,
                    "priority": 3,
                    "timeout": 15
                },
                "signly": {
                    "enabled": True,
                    "priority": 4,
                    "timeout": 10
                },
                "applesign": {
                    "enabled": True,
                    "priority": 5,
                    "timeout": 10
                },
                "codesign": {
                    "enabled": True,
                    "priority": 6,
                    "timeout": 10
                }
            },
            "custom_repos": []
        }
        self.save_config()
    
    def save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def add_custom_repo_config(self, name: str, url: str, api_endpoint: str):
        """Add custom repository to configuration"""
        self.config["custom_repos"].append({
            "name": name,
            "url": url,
            "api_endpoint": api_endpoint,
            "enabled": True
        })
        self.save_config()
    
    def update_repo_priority(self, repo_name: str, priority: int):
        """Update repository priority"""
        if repo_name in self.config["repositories"]:
            self.config["repositories"][repo_name]["priority"] = priority
            self.save_config()


# CLI Interface
def main():
    """Command-line interface for repository library"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Fearn Repository Library Manager - Unified signing service interface"
    )
    parser.add_argument("command", choices=[
        "list", "add", "remove", "enable", "disable", 
        "search", "certs", "apps", "sign", "config"
    ])
    parser.add_argument("-r", "--repo", help="Repository name")
    parser.add_argument("-n", "--name", help="Custom repo name")
    parser.add_argument("-u", "--url", help="Repository URL")
    parser.add_argument("-a", "--api", help="API endpoint")
    parser.add_argument("-t", "--token", help="Authentication token")
    parser.add_argument("-q", "--query", help="Search query")
    parser.add_argument("-app", "--app-path", help="App file path")
    parser.add_argument("-c", "--cert", help="Certificate ID")
    
    args = parser.parse_args()
    
    manager = RepoLibraryManager()
    config = RepoLibraryConfig()
    
    if args.command == "list":
        print("\n📚 Available Repositories:\n")
        for repo in manager.list_repos():
            status = "✅" if repo["enabled"] else "❌"
            print(f"{status} {repo['name']:<15} | {repo['type']:<12} | {repo['description']}")
    
    elif args.command == "add":
        if args.name and args.url and args.api:
            manager.add_custom_repo(args.name, args.url, args.api, args.token)
            config.add_custom_repo_config(args.name, args.url, args.api)
            print(f"✅ Added repository: {args.name}")
    
    elif args.command == "enable":
        if args.repo:
            if manager.enable_repo(args.repo):
                config.config["repositories"][args.repo.lower()]["enabled"] = True
                config.save_config()
                print(f"✅ Enabled: {args.repo}")
    
    elif args.command == "disable":
        if args.repo:
            if manager.disable_repo(args.repo):
                config.config["repositories"][args.repo.lower()]["enabled"] = False
                config.save_config()
                print(f"✅ Disabled: {args.repo}")
    
    elif args.command == "search":
        if args.query:
            results = manager.search_repos(args.query)
            print(f"\n🔍 Search results for '{args.query}':\n")
            for result in results:
                print(f"  - {result['repo']} ({result['match_type']})")
    
    elif args.command == "certs":
        if args.repo:
            certs = manager.get_certificates(args.repo, args.token)
            print(f"\n📜 Certificates from {args.repo}:\n")
            for cert in certs[:5]:  # Show first 5
                print(f"  - {cert.get('name', 'Unknown')}")
    
    elif args.command == "config":
        print("\n⚙️  Configuration:\n")
        print(json.dumps(config.config, indent=2))


if __name__ == "__main__":
    main()
