
from tqdm import tqdm
import importlib
import json
import torch
import os
from agents.multi_agent_system import MultiAgentSystem
from agents.base_agent import Agent
from mydatasets.base_dataset import BaseDataset

class SlidesSummaryAgent(MultiAgentSystem):
    def __init__(self, config):
        super().__init__(config)
    
    def predict(self, dataset:BaseDataset):
        general_agent = self.agents[-1]
        pdf = dataset.get_pdf()
        general_response, messages = general_agent.predict("", None, pdf, with_sys_prompt=True)
        print("### General Agent: "+ general_response)
        critical_info = general_agent.self_reflect(prompt = general_agent.config.agent.critical_prompt, add_to_message=False)
        print("### General Critical Agent: " + critical_info)

        start_index = critical_info.find('{') 
        end_index = critical_info.find('}') + 1 
        critical_info = critical_info[start_index:end_index]
        text_reflection = ""
        image_reflection = ""
        try:
            critical_info = json.loads(critical_info)
            text_reflection = critical_info.get("text", "")
            image_reflection = critical_info.get("image", "")
        except Exception as e:
            print(e)

        text_agent = self.agents[1]
        image_agent = self.agents[0]
        all_messages = "General Agent:\n" + general_response + "\n"
        
        relect_prompt = "\nYou may use the given clue:\n"
        full_text = dataset.get_full_text()
        full_images = dataset.get_retrival_images()
        text_response, messages = text_agent.predict(relect_prompt +text_reflection, texts = None, images = pdf, with_sys_prompt=True)
        all_messages += "Text Agent:\n" + text_response + "\n"
        image_response, messages = image_agent.predict(relect_prompt +image_reflection, texts = None, images = full_images, with_sys_prompt=True)
        all_messages += "Image Agent:\n" + image_response + "\n"
            
        # print("### Text Agent: " + text_response)
        # print("### Image Agent: " + image_response)
        summary, all_messages = self.sum_agent.predict(all_messages)

        return summary, all_messages
    
    def clean_messages(self):
        for agent in self.agents:
            agent.clean_messages()
        self.sum_agent.clean_messages()