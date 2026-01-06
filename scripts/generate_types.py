#!/usr/bin/env python3
"""
TypeScript Type Generator
=========================

Generate TypeScript interfaces from Pydantic models for frontend consumption.

Features
--------
- Scans Pydantic models from contexts, shared, and presentation layers
- Converts Python types to TypeScript equivalents
- Handles Optional, List, Dict, UUID, datetime types
- Generates JSDoc comments from field descriptions

Usage
-----
```bash
# Generate types to default location
python scripts/generate_types.py

# Generate to custom location
python scripts/generate_types.py --output frontend/src/types/api.ts
```

Output
------
TypeScript interfaces file with all Pydantic models converted.

Exit Codes
----------
- 0: Success
- 1: Error (import failed, generation failed, etc.)
"""
import sys
from pathlib import Path
from typing import Any, Dict, List, Type, Union, get_args, get_origin
import inspect

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from pydantic import BaseModel


def python_type_to_typescript(py_type: Any) -> str:
    """Convert Python type to TypeScript type"""

    # Handle None/Optional
    origin = get_origin(py_type)
    if origin is type(None):
        return "null"

    # Handle Union types (Optional)
    if origin is Union:
        args = get_args(py_type)
        ts_types = [python_type_to_typescript(arg) for arg in args]
        return " | ".join(ts_types)
    
    # Handle List
    if origin is list:
        args = get_args(py_type)
        if args:
            return f"Array<{python_type_to_typescript(args[0])}>"
        return "Array<any>"
    
    # Handle Dict
    if origin is dict:
        return "Record<string, any>"
    
    # Basic types
    type_map = {
        int: "number",
        float: "number",
        str: "string",
        bool: "boolean",
        bytes: "string",  # Base64 encoded
        type(None): "null",
    }
    
    if py_type in type_map:
        return type_map[py_type]
    
    # Handle UUID
    if hasattr(py_type, "__name__") and py_type.__name__ == "UUID":
        return "string"
    
    # Handle datetime
    if hasattr(py_type, "__name__") and "datetime" in py_type.__name__.lower():
        return "string"
    
    # Default to any
    return "any"


def generate_interface_from_model(model: Type[BaseModel], name: str = None) -> str:
    """Generate TypeScript interface from Pydantic model"""
    
    interface_name = name or model.__name__
    fields: List[str] = []
    
    for field_name, field_info in model.model_fields.items():
        # Get field type
        field_type = field_info.annotation
        ts_type = python_type_to_typescript(field_type)
        
        # Check if field is optional
        is_optional = not field_info.is_required()
        optional_mark = "?" if is_optional else ""
        
        # Add description if available
        description = field_info.description
        if description:
            fields.append(f"  /** {description} */")
        
        fields.append(f"  {field_name}{optional_mark}: {ts_type};")
    
    interface_body = "\n".join(fields)
    
    return f"""export interface {interface_name} {{
{interface_body}
}}"""


def find_pydantic_models(module_path: Path) -> List[Type[BaseModel]]:
    """Find all Pydantic models in a module"""
    models: List[Type[BaseModel]] = []
    
    for py_file in module_path.rglob("*.py"):
        if py_file.name.startswith("__"):
            continue
        
        # Import module
        rel_path = py_file.relative_to(project_root)
        module_name = str(rel_path.with_suffix("")).replace("/", ".")
        
        try:
            module = __import__(module_name, fromlist=[""])
            
            # Find Pydantic models
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, BaseModel) and 
                    obj != BaseModel):
                    models.append(obj)
        except Exception as e:
            print(f"Warning: Could not import {module_name}: {e}")
    
    return models


def generate_types_file(output_path: Path):
    """Generate TypeScript types file"""
    
    print("🔨 Generating TypeScript types...")
    
    # Find all DTO models - updated for new project structure
    dto_paths = [
        project_root / "src" / "contexts",
        project_root / "src" / "shared",
        project_root / "src" / "presentation",
    ]
    
    all_models: List[Type[BaseModel]] = []
    for path in dto_paths:
        if path.exists():
            models = find_pydantic_models(path)
            all_models.extend(models)
    
    # Generate interfaces
    interfaces: List[str] = []
    interfaces.append("// Auto-generated TypeScript types")
    interfaces.append("// DO NOT EDIT MANUALLY")
    interfaces.append("")
    
    for model in all_models:
        try:
            interface = generate_interface_from_model(model)
            interfaces.append(interface)
            interfaces.append("")
        except Exception as e:
            print(f"Warning: Could not generate interface for {model.__name__}: {e}")
    
    # Write to file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(interfaces))
    
    print(f"✅ Generated {len(all_models)} TypeScript interfaces")
    print(f"📄 Output: {output_path}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate TypeScript types from Pydantic models"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default="frontend/src/types/api.ts",
        help="Output file path (default: frontend/src/types/api.ts)"
    )
    
    args = parser.parse_args()
    
    try:
        output_path = Path(args.output)
        generate_types_file(output_path)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()