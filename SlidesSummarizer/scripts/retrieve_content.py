import os
import sys
import argparse

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from retrieval.image_retrieval import ImageRetrieval


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Retrieve model structure and experiment results pages from paper images")
    parser.add_argument("--base_dir", default="data", help="Base directory")
    parser.add_argument("--paper_name", required=True, help="Paper name")
    parser.add_argument("--top_k", type=int, default=3, help="Number of top pages to retrieve")
    parser.add_argument("--type", choices=["model", "experiment", "both"], default="both", 
                        help="Type of pages to retrieve: model structure, experiment results, or both")
    
    args = parser.parse_args()

    image_dir = os.path.join(args.base_dir, args.paper_name, "images")
    output_dir = os.path.join(args.base_dir, args.paper_name, "retrieval")

    # 检查目录是否存在
    if not os.path.exists(image_dir):
        print(f"Image directory {image_dir} does not exist")
        return
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Starting image retrieval for {args.paper_name}")
    print(f"Image directory: {image_dir}")
    print(f"Output directory: {output_dir}")
    print(f"Retrieving top {args.top_k} pages for {args.type} content")
    
    # 初始化检索系统
    retriever = ImageRetrieval()
    
    # 执行检索
    if args.type == "model":
        print(f"Retrieving model structure pages for {args.paper_name}...")
        results = retriever.find_model_structure_pages(image_dir, output_dir, args.top_k)
        print(f"Found {len(results['model_structure_pages'])} model structure pages")
    elif args.type == "experiment":
        print(f"Retrieving experiment results pages for {args.paper_name}...")
        results = retriever.find_experiment_results_pages(image_dir, output_dir, args.top_k)
        print(f"Found {len(results['experiment_results_pages'])} experiment results pages")
    else:  # both
        print(f"Retrieving both model structure and experiment results pages for {args.paper_name}...")
        results = retriever.find_specialized_pages(image_dir, output_dir, args.top_k)
        print(f"Found {len(results['model_structure']['model_structure_pages'])} model structure pages")
        print(f"Found {len(results['experiment_results']['experiment_results_pages'])} experiment results pages")
    
    print(f"Retrieval complete. Results saved to {output_dir}")

if __name__ == "__main__":
    main()