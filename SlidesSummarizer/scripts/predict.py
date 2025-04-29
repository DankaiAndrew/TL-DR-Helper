import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from mydatasets.base_dataset import BaseDataset
from agents.slides_summary_agent import SlidesSummaryAgent
import hydra
from omegaconf import DictConfig
import json

@hydra.main(config_path="../config", config_name="base", version_base="1.2")
def main(cfg: DictConfig):
    # 从命令行获取paper_name参数
    #if not hasattr(cfg, "paper_name"):
    #    raise ValueError("Missing required parameter: paper_name. Use paper_name=YOUR_PAPER_NAME")
    
    os.environ["CUDA_VISIBLE_DEVICES"] = cfg.cuda_visible_devices
    os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:64"
    for agent_config in cfg.agents:
        agent_name = agent_config.agent
        model_name = agent_config.model
        agent_cfg = hydra.compose(config_name="agent/"+agent_name, overrides=[]).agent
        model_cfg = hydra.compose(config_name="model/"+model_name, overrides=[]).model
        agent_config.agent = agent_cfg
        agent_config.model = model_cfg
    
    cfg.sum_agent.agent = hydra.compose(config_name="agent/"+cfg.sum_agent.agent, overrides=[]).agent
    cfg.sum_agent.model = hydra.compose(config_name="model/"+cfg.sum_agent.model, overrides=[]).model
    
    # Initialize dataset with paper_name from cfg
    dataset = BaseDataset(cfg.paper_name)
    slides_summary_agent = SlidesSummaryAgent(cfg)
    summary, all_messages = slides_summary_agent.predict(dataset)

    # dump all_message and summary to file, in data folder
    summary_path = os.path.join("data", cfg.paper_name, "summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f)
    
if __name__ == "__main__":
    main()