from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.responses import Response
import yaml

from fyodorov_utils.decorators.logging import error_handler
from fyodorov_utils.auth.auth import authenticate

from fyodorov_llm_agents.providers.provider_model import ProviderModel
from fyodorov_llm_agents.providers.provider_service import Provider
from fyodorov_llm_agents.models.llm_model import LLMModel
from fyodorov_llm_agents.tools.mcp_tool_service import MCPTool as Tool
from fyodorov_llm_agents.tools.mcp_tool_model import MCPTool as ToolModel
from fyodorov_llm_agents.instances.instance_model import InstanceModel
from fyodorov_llm_agents.models.llm_service import LLMService
from fyodorov_llm_agents.instances.instance_service import Instance
from fyodorov_llm_agents.agents.agent_service import AgentService as Agent

app = FastAPI(
    title="Fyodorov-Auth",
    description="Common auth endpoints for Fyodorov services",
    version="0.0.1",
)


# Yaml parsing
@app.post("/")
@error_handler
async def create_from_yaml(request: Request, user=Depends(authenticate)):
    try:
        fyodorov_yaml = await request.body()
        print(f"fyodorov_yaml: \n{fyodorov_yaml}")
        fyodorov_config = yaml.safe_load(fyodorov_yaml)
        print(f"fyodorov_config: \n{fyodorov_config}")
        response = {
            "providers": [],
            "models": [],
            "agents": [],
            "instances": [],
            "tools": [],
        }
        print(f"fyodorov_config: \n{fyodorov_config}")
        if "providers" in fyodorov_config:
            print("Saving providers")
            for provider_dict in fyodorov_config["providers"]:
                print(f"Provider: {provider_dict}")
                provider = ProviderModel.from_dict(provider_dict)
                new_provider = await Provider.save_provider_in_db(
                    user["session_id"], provider, user["sub"]
                )
                response["providers"].append(new_provider)
        print("Saved providers", response["providers"])
        if "models" in fyodorov_config:
            for model_dict in fyodorov_config["models"]:
                model = LLMModel.from_dict(model_dict)
                print(f"Model: {model}")
                llm_service = LLMService()
                new_model = await llm_service.save_model_in_db(
                    user["session_id"], user["sub"], model
                )
                response["models"].append(new_model.to_dict())
        print("Saved models", response["models"])
        if "tools" in fyodorov_config:
            for tool_dict in fyodorov_config["tools"]:
                print(f"Tool dict: {tool_dict}")
                # marshal back to yaml
                tool_yaml = yaml.dump(tool_dict)
                print(f"Tool yaml: {tool_yaml}")
                new_tool = ToolModel.from_yaml(tool_yaml)
                print(f"New tool: {new_tool}")
                if new_tool:
                    tool_instance = await Tool.create_or_update_in_db(
                        user["session_id"], new_tool, user["sub"]
                    )
                    print(f"Saved tool: {tool_instance}")
                    response["tools"].append(tool_instance.to_dict())
        print("Saved tools", response["tools"])
        if "agents" in fyodorov_config:
            for agent_dict in fyodorov_config["agents"]:
                new_agent = await Agent.save_from_dict(
                    user["session_id"], user["sub"], agent_dict
                )
                response["agents"].append(new_agent)
        print("Saved agents", response["agents"])
        if len(response["agents"]) > 0:
            for agent in response["agents"]:
                instance = InstanceModel(
                    agent_id=str(agent["id"]), title=f"Default Instance {agent['id']}"
                )
                new_instance = await Instance.create_in_db(instance)
                response["instances"].append(new_instance)
        print("Saved instances", response["instances"])
        return response
    except Exception as e:
        print("Error parsing config from yaml", str(e))
        raise HTTPException(status_code=400, detail="Invalid YAML format")


@app.get("/")
@error_handler
async def get_yaml(user=Depends(authenticate)):
    try:
        limit = 100
        result = {
            "providers": [],
            "models": [],
            "agents": [],
            "instances": [],
            "tools": [],
        }
        providers = await Provider.get_providers(limit=limit, user_id=user["sub"])
        result["providers"] = [provider.resource_dict() for provider in providers]
        llm_service = LLMService()
        models = await llm_service.get_models(access_token=user["session_id"], user_id=user["sub"], limit=limit)
        result["models"] = [model.resource_dict() for model in models]
        agents = await Agent.get_all_in_db(limit=limit, user_id=user["sub"])
        result["agents"] = [agent.resource_dict() for agent in agents]
        instances = await Instance.get_all_in_db(limit=limit, user_id=user["sub"])
        result["instances"] = [instance.resource_dict() for instance in instances]
        tools = await Tool.get_all_in_db(limit=limit, user_id=user["sub"])
        result["tools"] = [tool.resource_dict() for tool in tools]
        print(f"Result: {result}")
        yaml_result = yaml.dump(result, indent=2)
        print(f"YAML: {yaml_result}")
        return Response(content=yaml_result, media_type="application/x-yaml")
    except Exception as e:
        print("Error getting yaml:", str(e))
        raise HTTPException(
            status_code=400, detail="Error marshaling resources to yaml"
        )


@app.get("/{resource_type}")
@error_handler
async def get_yaml_by_name(resource_type: str, user=Depends(authenticate)):
    limit = 100
    print(f"Got request for {resource_type} yaml")
    resources = {}
    try:
        if resource_type not in ["providers", "models", "agents", "instances", "tools"]:
            raise HTTPException(status_code=400, detail="Unrecognized resource type")
        elif resource_type == "providers":
            resources["providers"] = await Provider.get_providers(
                limit=limit, user_id=user["sub"]
            )
            resources["providers"] = [
                provider.resource_dict() for provider in resources["providers"]
            ]
        elif resource_type == "models":
            llm_service = LLMService()
            resources["models"] = await llm_service.get_models(access_token=user["session_id"], user_id=user["sub"], limit=limit)
            resources["models"] = [
                models.resource_dict() for models in resources["models"]
            ]
        elif resource_type == "agents":
            resources["agents"] = await Agent.get_all_in_db(
                limit=limit, user_id=user["sub"]
            )
            resources["agents"] = [
                agents.resource_dict() for agents in resources["agents"]
            ]
        elif resource_type == "instances":
            resources["instances"] = await Instance.get_all_in_db(
                limit=limit, user_id=user["sub"]
            )
            resources["instances"] = [
                instances.resource_dict() for instances in resources["instances"]
            ]
        elif resource_type == "tools":
            resources["tools"] = await Tool.get_all_in_db(
                limit=limit, user_id=user["sub"]
            )
            resources["tools"] = [tools.resource_dict() for tools in resources["tools"]]
        else:
            raise HTTPException(status_code=400, detail="Invalid resource type")
        print(f"Resources: {resources}")
        yaml_result = yaml.dump(resources, indent=2)
        return Response(content=yaml_result, media_type="application/x-yaml")
    except Exception as e:
        print("Error getting yaml for resource:", str(e))
        raise HTTPException(
            status_code=400,
            detail=f"Error marshaling {resource_type} resources to yaml",
        )
