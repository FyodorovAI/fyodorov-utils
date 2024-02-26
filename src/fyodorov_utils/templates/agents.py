from fyodorov_llm_agents.tools.tool import Tool as ToolModel
from fyodorov_llm_agents.agents.agent import Agent as AgentModel
import yaml

def parse_yaml(yaml_str: str) -> ToolModel:
    if not yaml_str:
        raise ValueError('YAML string is required')
    print(f"Parsing YAML: {yaml_str}")
    yaml_str = yaml_str.strip()
    yaml_dict = yaml.safe_load(yaml_str)
    print(f"Parsing agents YAML in format: {yaml_dict['version']}")
    agents = []
    for agent in yaml_dict['agents']:
        print(f"Parsing agent: {agent}")
        print(f"body: {yaml_dict['agents'][agent]}")
        agent = AgentModel(**yaml_dict['agents'][agent])
        agent.validate()
        agents.append(agent)
    print(f"agents: {agents}")
    return agents
