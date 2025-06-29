import os

# Service name to port mapping
SERVICE_PORTS = {
    'Dostoyevsky': 8000,
    'Zhukovsky': 8003, 
    'Gagarin': 8002,
    'Tsiolkovsky': 8001
}

def get_service_url(service_name: str) -> str:
    """Get service URL from environment or default to Docker Compose service name."""
    if service_name not in SERVICE_PORTS:
        raise ValueError(f"Unknown service: {service_name}")
    
    env_var = f"{service_name.upper()}_URL"
    default_url = f"http://{service_name.lower()}:{SERVICE_PORTS[service_name]}"
    
    return os.getenv(env_var, default_url)
