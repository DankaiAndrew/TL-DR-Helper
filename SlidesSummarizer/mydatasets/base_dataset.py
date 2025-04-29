import json
import os
from PIL import Image
from datetime import datetime
import glob

class BaseDataset():
    def __init__(self, paper_name, data_folder="data", max_character_per_page=4000):
        """
        Initialize the dataset for a single paper
        
        Args:
            paper_name: Name of the paper (folder name)
            data_folder: Path to the data folder containing papers
            max_character_per_page: Maximum characters per page
        """
        self.paper_name = paper_name
        self.data_folder = data_folder
        self.paper_folder = os.path.join(data_folder, paper_name)
        
        # Check if paper folder exists
        if not os.path.exists(self.paper_folder):
            raise ValueError(f"Paper folder not found: {self.paper_folder}")
            
        # Check for content.json
        self.content_file = os.path.join(self.paper_folder, "content.json")
        if not os.path.exists(self.content_file):
            raise ValueError(f"Content file not found: {self.content_file}")
        
        # Set paths for retrieval files
        self.model_structure_file = os.path.join(self.paper_folder, "retrieval", "model_structure_pages.json")
        self.experiment_results_file = os.path.join(self.paper_folder, "retrieval", "experiment_results_pages.json")
        
        # Set configuration parameters
        self.max_character_per_page = max_character_per_page
        
        # Load paper content
        self.content = self.load_paper_content()
        
        # Set current time for output files
        current_time = datetime.now()
        self.time = current_time.strftime("%Y-%m-%d-%H-%M")
    
    def get_pdf(self):
        """
        Get the path to the paper's PDF file
        
        Returns:
            List of paths to all images in the images folder
        """
        pdf_images_path = os.path.join(self.data_folder, self.paper_name, "images")
        if not os.path.exists(pdf_images_path):
            raise ValueError(f"Images folder not found: {pdf_images_path}")
        
        # 获取images文件夹下所有图片路径
        image_paths = []
        for file_name in sorted(os.listdir(pdf_images_path)):
            if file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                image_path = os.path.join(pdf_images_path, file_name)
                image_paths.append(image_path)
        
        # 按照文件名顺序排序
        image_paths.sort(key=lambda x: int(os.path.basename(x).split('_')[0]) if os.path.basename(x).split('_')[0].isdigit() else float('inf'))
        
        return image_paths
    
    def load_paper_content(self):
        """
        Load paper content from content.json
        
        Returns:
            Dictionary containing paper content
        """
        try:
            with open(self.content_file, 'r', encoding='utf-8') as f:
                content = json.load(f)
                return content
        except Exception as e:
            raise ValueError(f"Error loading content file: {str(e)}")
    
    def get_full_text(self):
        """
        Get the full text of the paper from content.json
        
        Returns:
            String containing the full text of the paper
        """
        full_text = ""
        
        if not hasattr(self, 'content') or not self.content:
            self.content = self.load_paper_content()
            
        for page in self.content.get("pages", []):
            page_text = page.get("text", "").strip()
            full_text += page_text + " "
            
        return full_text.strip()
    
    def _load_retrieval_json(self, json_path):
        """
        Helper function to load a retrieval JSON file
        
        Args:
            json_path: Path to the retrieval JSON file
            
        Returns:
            Dictionary with the retrieval data or None if file doesn't exist
        """
        if not os.path.exists(json_path):
            print(f"Warning: Retrieval file not found: {json_path}")
            return None
            
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data
        except Exception as e:
            print(f"Error loading retrieval file {json_path}: {str(e)}")
            return None
    
    def get_model_structure_images(self):
        """
        Get paths to model structure images from retrieval data
        
        Returns:
            List of image paths or empty list if not found
        """
        data = self._load_retrieval_json(self.model_structure_file)
        
        if not data:
            return []
            
        return data.get("full_paths", [])
    
    def get_experiment_results_images(self):
        """
        Get paths to experiment results images from retrieval data
        
        Returns:
            List of image paths or empty list if not found
        """
        data = self._load_retrieval_json(self.experiment_results_file)
        
        if not data:
            return []
            
        return data.get("full_paths", [])
    
    def get_retrival_images(self):
        """
        Get paths to all images from retrieval data
        
        Returns:
            List of image paths or empty list if not found
        """
        model_structure_images = self.get_model_structure_images()
        experiment_results_images = self.get_experiment_results_images()
        return model_structure_images + experiment_results_images
    
    def save_summary(self, summary_data, output_folder=None):
        """
        Save summary to a JSON file
        
        Args:
            summary_data: Dictionary containing the summary data
            output_folder: Path to save the summary (defaults to paper folder)
            
        Returns:
            Path to the saved summary file
        """
        if output_folder is None:
            output_folder = self.paper_folder
            
        os.makedirs(output_folder, exist_ok=True)
        summary_path = os.path.join(output_folder, f"summary_{self.time}.json")
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, ensure_ascii=False, indent=2)
            
        print(f"Summary saved to {summary_path}")
        return summary_path
