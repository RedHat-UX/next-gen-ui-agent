#!/usr/bin/env python3
"""
Test script to see components returned by the agent with input_data_type and formatters.

This script demonstrates how to:
1. Send data to the agent with a data_type
2. See the generated component JSON with input_data_type
3. Verify formatter identifiers are included
"""

import json
import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "libs"))
sys.path.insert(0, str(project_root / "tests"))
sys.path.insert(0, str(Path(__file__).parent / "server"))

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from next_gen_ui_langgraph import NextGenUILangGraphAgent

# Import config to use proper data_types configuration
from config import NGUI_CONFIG


def test_agent_with_input_data_type():
    """Test the agent with input_data_type to see generated component."""
    
    # Sample data that will generate a table component
    products_data = {
        "products": [
            {
                "name": "Laptop",
                "price": 999.99,
                "status": True,
                "category": "Electronics"
            },
            {
                "name": "Mouse",
                "price": 25.50,
                "status": False,
                "category": "Accessories"
            },
            {
                "name": "Keyboard",
                "price": 79.99,
                "status": True,
                "category": "Accessories"
            }
        ]
    }
    
    # Create agent (using JSON renderer for easy inspection)
    agent = NextGenUILangGraphAgent()
    graph = agent.build_graph()
    
    # Use NGUI_CONFIG which includes data_types configuration for formatters
    config = NGUI_CONFIG
    
    # Build messages with data_type
    # The tool_name will be mapped to input_data_type in the component
    # Use "products" to match the config key (LangGraph will map tool name to data type)
    tool_name = "products"
    call_id = "test_call_1"
    
    messages = [
        HumanMessage(content="Show me a table of products with their prices and status"),
        AIMessage(
            content="",
            tool_calls=[
                {
                    "name": tool_name,
                    "args": {},
                    "id": call_id,
                }
            ],
        ),
        ToolMessage(
            content=json.dumps(products_data, default=str),
            tool_call_id=call_id,
            name=tool_name,
        ),
    ]
    
    print("=" * 80)
    print("Testing Agent with input_data_type")
    print("=" * 80)
    print(f"\nInput data type: 'products'")
    print(f"Data: {json.dumps(products_data, indent=2)}")
    print("\nInvoking agent...")
    
    # Invoke agent
    import asyncio
    result = asyncio.run(graph.ainvoke(messages, config))
    
    # Extract component data
    if result.get("components_data"):
        component_data = result["components_data"][0]
        
        print("\n" + "=" * 80)
        print("Generated Component JSON")
        print("=" * 80)
        
        # Convert to dict for pretty printing
        component_dict = component_data.model_dump()
        
        # Pretty print the component
        print(json.dumps(component_dict, indent=2))
        
        # Check for input_data_type
        print("\n" + "=" * 80)
        print("Key Fields Check")
        print("=" * 80)
        
        if "input_data_type" in component_dict:
            print(f"✅ input_data_type: {component_dict['input_data_type']}")
        else:
            print("❌ input_data_type: NOT FOUND (this is expected if data_type wasn't set)")
        
        if "component" in component_dict:
            print(f"✅ component: {component_dict['component']}")
        
        if "fields" in component_dict:
            print(f"✅ fields: {len(component_dict['fields'])} fields")
            for i, field in enumerate(component_dict['fields']):
                print(f"   Field {i+1}: {field.get('name')} (id: {field.get('id')})")
                if "formatter" in field:
                    print(f"      - formatter: {field['formatter']}")
        
        if "on_row_click" in component_dict:
            print(f"✅ on_row_click: {component_dict['on_row_click']}")
        
        # Show CSS class that would be generated
        if "input_data_type" in component_dict:
            css_class = f"data-view-{component_dict['input_data_type']}"
            print(f"\n📝 Generated CSS class: {css_class}")
        
        # Show formatter identifiers that would be used
        if "fields" in component_dict:
            print("\n📝 Formatter identifiers in fields:")
            for field in component_dict['fields']:
                if "formatter" in field and field["formatter"]:
                    field_id = field.get("id", "unknown")
                    input_type = component_dict.get("input_data_type", "")
                    if input_type:
                        resolved_formatter = f"{input_type}.{field['formatter']}"
                        print(f"   - {field['name']}: '{field['formatter']}' → '{resolved_formatter}'")
                    else:
                        print(f"   - {field['name']}: '{field['formatter']}' (generic)")
    
    # Show renditions
    if result.get("renditions"):
        print("\n" + "=" * 80)
        print("Rendered Output")
        print("=" * 80)
        rendition = result["renditions"][0]
        print(f"Component System: {rendition.component_system}")
        print(f"MIME Type: {rendition.mime_type}")
        print(f"Content (first 500 chars):\n{rendition.content[:500]}...")
    
    return result


if __name__ == "__main__":
    test_agent_with_input_data_type()



