# Fyodorov Utils

<p>
<img alt="GitHub Contributors" src="https://img.shields.io/github/contributors/fyodorovai/fyodorov-utils" />
<img alt="GitHub Last Commit" src="https://img.shields.io/github/last-commit/fyodorovai/fyodorov-utils" />
<img alt="" src="https://img.shields.io/github/repo-size/fyodorovai/fyodorov-utils" />
<img alt="GitHub Issues" src="https://img.shields.io/github/issues/fyodorovai/fyodorov-utils" />
<img alt="GitHub Pull Requests" src="https://img.shields.io/github/issues-pr/fyodorovai/fyodorov-utils" />
</p>

`fyodorov_-_utils` is a Python library that provides a collection of utility functions and classes used across multiple 
services within the Fyodorov project. The Fyodorov project is a suite of complementary services for working with 
LLM-based agents.

The library defines standard practices and includes tooling around logging, error handling, and authentication, 
as well as configuration management.

### Error handling
There is a decorator which will handle errors for FastAPI endpoints. It will also log those errors in a consistent 
fashion without any input required. It can be used like this:
```Python
from fyodorov_utils.decorators.logging import error_handler

@app.post
@error_handler
def endpoint():
    return 
```

### Authentication
You can import the authentication helper like so:
```Python
from fyodorov_utils.auth.auth import authenticate

@app.post('/endpoint')
@error_handler
def create_provider(provider: ProviderModel, user = Depends(authenticate)):
    return
```

This will require calls to that endpoint to be authenticated by the user's access token (which is a JWT). It also makes 
the user object available within the function for additional authentication or authorization logic.

### Shared User Endpoints
There are certain endpoints around user actions that are shared functionality across all services. These include 
signing up, logging in, and creating API keys (which can be used for **tools** or third-party services). These 
endpoints are defined in the library and can be used like this:

```Python
# User endpoints
from fyodorov_utils.auth.endpoints import users_app
app.mount('/users', users_app)
```

## Installation

You can install `fyodorov_utils` using pip: 
```shell
pip install fyodorov-utils==0.2.11
```
