import requests
from packaging.specifiers import SpecifierSet
from packaging.version import parse as parse_version

def get_min_python_version(requires_python_str):
    """
    Extracts the highest lower-bound version from a requires_python specifier string.
    Example: '>=3.8, <4.0' -> Version('3.8')
    """
    if not requires_python_str:
        return None
        
    try:
        spec_set = SpecifierSet(requires_python_str)
        min_ver = None
        for spec in spec_set:
            # Look for operators that define a minimum version bound
            if spec.operator in ('>=', '>', '~=', '=='):
                ver = parse_version(spec.version)
                if min_ver is None or ver > min_ver:
                    min_ver = ver
        return min_ver
    except Exception:
        return None

def analyze_requirements(dependencies):
    deps_checked = len(dependencies)
    not_found = 0
    incompatible = 0
    
    max_min_version = None
    highest_req_string = ""

    for dep in dependencies:
        dep = dep.strip()
        if not dep:
            continue
            
        # Parse the package name and pinned version
        name, version = dep.split('==')
        
        # PyPI JSON API endpoint for specific release
        url = f"https://pypi.org/pypi/{name}/{version}/json"
        response = requests.get(url)
        
        # 1. Check if it exists on PyPI
        if response.status_code == 404:
            not_found += 1
            continue
            
        data = response.json()
        requires_python = data['info'].get('requires_python')
        
        if requires_python:
            try:
                spec_set = SpecifierSet(requires_python)
                # 2. Check Python 3.11 compatibility
                if not spec_set.contains("3.11"):
                    incompatible += 1
                
                # 3. Track the highest minimum requirement
                min_ver = get_min_python_version(requires_python)
                if min_ver:
                    if max_min_version is None or min_ver > max_min_version:
                        max_min_version = min_ver
                        highest_req_string = f"{name}=={version} ({requires_python})"
            except Exception:
                # Fallback for invalid specifiers, treat as compatible
                pass

    # Print Outputs
    print(f"Dependencies checked: {deps_checked}")
    print(f"Not found on PyPI: {not_found}")
    print(f"Incompatible with Python 3.11: {incompatible}")
    if highest_req_string:
        print(f"Highest requirement: {highest_req_string}")


if __name__ == "__main__":
    # The input list provided at the bottom of the assignment page
    test_input = [
        "django==4.2",
        "numpy==2.3.0",
        "scipy==1.7.0",
        "scikit-learn==1.4.0",
        "fastapi-agent-router==0.3.1",
        "matplotlib==3.99.0",
        "six==1.16.0",
        "requests==2.32.0"
    ]
    
    print("--- Output ---")
    analyze_requirements(test_input)