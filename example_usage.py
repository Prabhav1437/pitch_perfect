"""
Example usage of the evaluation API.
"""
import requests
import json
from pathlib import Path


def evaluate_presentation_sync(
    ppt_file_path: str,
    problem_statement: str,
    api_url: str = "http://localhost:8000"
):
    """
    Evaluate a presentation using the API (synchronous).
    
    Args:
        ppt_file_path: Path to the PowerPoint file
        problem_statement: Problem statement or rubric
        api_url: Base URL of the API
        
    Returns:
        Evaluation results as dictionary
    """
    endpoint = f"{api_url}/evaluate"
    
    # Prepare files and data
    with open(ppt_file_path, 'rb') as f:
        files = {'file': (Path(ppt_file_path).name, f, 'application/vnd.openxmlformats-officedocument.presentationml.presentation')}
        data = {'problem_statement': problem_statement}
        
        # Make request
        response = requests.post(endpoint, files=files, data=data)
    
    # Check response
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API error: {response.status_code} - {response.text}")


def check_health(api_url: str = "http://localhost:8000"):
    """
    Check API health status.
    
    Args:
        api_url: Base URL of the API
        
    Returns:
        Health status as dictionary
    """
    endpoint = f"{api_url}/health"
    response = requests.get(endpoint)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Health check failed: {response.status_code}")


def batch_evaluate(
    ppt_files: list,
    problem_statement: str,
    api_url: str = "http://localhost:8000"
):
    """
    Evaluate multiple presentations.
    
    Args:
        ppt_files: List of paths to PowerPoint files
        problem_statement: Problem statement or rubric
        api_url: Base URL of the API
        
    Returns:
        List of evaluation results
    """
    results = []
    
    for ppt_file in ppt_files:
        print(f"\nEvaluating: {ppt_file}")
        try:
            result = evaluate_presentation_sync(ppt_file, problem_statement, api_url)
            results.append({
                'file': ppt_file,
                'success': True,
                'evaluation': result
            })
            print(f"✓ Score: {result['overall_score']}/50")
        except Exception as e:
            results.append({
                'file': ppt_file,
                'success': False,
                'error': str(e)
            })
            print(f"✗ Error: {e}")
    
    return results


# Example usage
if __name__ == "__main__":
    # Check if API is running
    try:
        health = check_health()
        print("API Health Status:")
        print(json.dumps(health, indent=2))
        print()
    except Exception as e:
        print(f"Error: API is not running. Please start it first.")
        print(f"Run: uvicorn main:app --reload")
        exit(1)
    
    # Example evaluation
    # Uncomment and modify with your actual file path
    """
    result = evaluate_presentation_sync(
        ppt_file_path="sample_presentation.pptx",
        problem_statement="Build a web scraper for e-commerce websites that extracts product information"
    )
    
    print("Evaluation Results:")
    print("=" * 60)
    print(f"Overall Score: {result['overall_score']}/50")
    print()
    print("Individual Scores:")
    for category, score in result['scores'].items():
        print(f"  {category}: {score}/10")
    print()
    print("Strengths:")
    for strength in result['strengths']:
        print(f"  + {strength}")
    print()
    print("Weaknesses:")
    for weakness in result['weaknesses']:
        print(f"  - {weakness}")
    print()
    print("Improvement Suggestions:")
    for suggestion in result['improvement_suggestions']:
        print(f"  → {suggestion}")
    print()
    print(f"Summary: {result['summary_evaluation']}")
    """
    
    # Example batch evaluation
    """
    ppt_files = [
        "presentation1.pptx",
        "presentation2.pptx",
        "presentation3.pptx"
    ]
    
    results = batch_evaluate(
        ppt_files,
        "Build a machine learning model for image classification"
    )
    
    # Print summary
    print("\n" + "=" * 60)
    print("Batch Evaluation Summary")
    print("=" * 60)
    for result in results:
        if result['success']:
            score = result['evaluation']['overall_score']
            print(f"{result['file']}: {score}/50")
        else:
            print(f"{result['file']}: FAILED - {result['error']}")
    """
