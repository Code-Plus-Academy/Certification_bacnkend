import os
import sys
import json
import csv
import argparse
from datetime import datetime
from generator import (
    generate_document, 
    list_templates, 
    save_custom_template, 
    delete_template, 
    extract_template_variables,
    TEMPLATES_DIR, 
    OUTPUT_DIR
)

def get_template_path(template_name):
    if not template_name.endswith('.html'):
        template_name += '.html'
    path = os.path.join(TEMPLATES_DIR, template_name)
    if os.path.exists(path):
        return path
    elif os.path.exists(template_name):
        return template_name
    else:
        raise FileNotFoundError(f"Template '{template_name}' not found.")

def run_single(template_name, data, output_filename=None):
    template_path = get_template_path(template_name)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    if not output_filename:
        safe_name = data.get('name', 'document').replace(' ', '_')
        output_filename = os.path.join(OUTPUT_DIR, f"{template_name.replace('.html','')}_{safe_name}.pdf")
    elif not os.path.isabs(output_filename):
        output_filename = os.path.join(OUTPUT_DIR, output_filename)
        
    return generate_document(template_path, data, output_filename)

def run_batch_csv(template_name, csv_filepath):
    template_path = get_template_path(template_name)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print(f"Reading batch data from CSV: {csv_filepath}")
    results = []
    with open(csv_filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, 1):
            if 'date' not in row or not row['date']:
                row['date'] = datetime.today().strftime('%B %d, %Y')
            name_slug = row.get('name', f'entry_{i}').replace(' ', '_')
            output_name = os.path.join(OUTPUT_DIR, f"{template_name.replace('.html','')}_{name_slug}.pdf")
            pdf_path = generate_document(template_path, row, output_name)
            results.append(pdf_path)
            
    print(f"\n[SUCCESS] Batch generation finished! Generated {len(results)} PDFs.")
    return results

def interactive_mode():
    print("==================================================")
    print("      PDF GENERATION & TEMPLATE MANAGEMENT        ")
    print("==================================================")
    templates = list_templates()
    
    print("\nSelect Available Template:")
    for idx, t in enumerate(templates, 1):
        custom_tag = " (Custom)" if t['is_custom'] else ""
        print(f" {idx}. {t['name']} [{t['filename']}]{custom_tag}")
    print(f" {len(templates)+1}. Add New Custom HTML Template")
    
    choice = input(f"Enter choice (1-{len(templates)+1}): ").strip()
    
    if choice == str(len(templates)+1):
        file_path = input("Enter path to custom HTML file: ").strip()
        if not os.path.exists(file_path):
            print(f"[ERROR] File '{file_path}' not found.")
            return
        t_name = input("Enter template name (e.g. Internship_Letter): ").strip()
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        saved_name, _, vars_found = save_custom_template(t_name, content)
        print(f"\n[SUCCESS] Added template '{saved_name}' with variables: {vars_found}")
        return
        
    try:
        selected_template = templates[int(choice)-1]
    except (ValueError, IndexError):
        print("[ERROR] Invalid selection.")
        return
        
    template_filename = selected_template['filename']
    required_vars = selected_template['variables']
    
    print(f"\nEnter dynamic values for '{selected_template['name']}':")
    data = {}
    for var in required_vars:
        default_val = datetime.today().strftime('%B %d, %Y') if var == 'date' else f"Sample {var.replace('_', ' ').title()}"
        val = input(f" - {var} [{default_val}]: ").strip()
        data[var] = val if val else default_val
        
    run_single(template_filename, data)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Automated Certificate & Offer Letter PDF Generator with Template Management")
    parser.add_argument('--template', help="Template filename or path")
    parser.add_argument('--json', help="JSON string of dynamic fields")
    parser.add_argument('--csv', help="Path to CSV file for batch generation")
    parser.add_argument('--output', help="Output PDF file name")
    parser.add_argument('--list-templates', action='store_true', help="List all available HTML templates")
    parser.add_argument('--add-template', help="Path to HTML file to register as a custom template")
    parser.add_argument('--name', help="Custom template name (used with --add-template)")
    parser.add_argument('--delete-template', help="Filename of template to delete")
    parser.add_argument('--interactive', '-i', action='store_true', help="Run interactive mode")
    
    args = parser.parse_args()
    
    if args.list_templates:
        print("\n--- INSTALLED HTML TEMPLATES ---")
        for t in list_templates():
            custom_str = " (Custom)" if t['is_custom'] else " (System Default)"
            print(f"• {t['filename']}{custom_str}")
            print(f"  Detected Placeholders: {', '.join(t['variables']) if t['variables'] else 'None'}\n")
    elif args.add_template:
        if not os.path.exists(args.add_template):
            print(f"[ERROR] Template file '{args.add_template}' not found.")
            sys.exit(1)
        name = args.name or os.path.basename(args.add_template)
        with open(args.add_template, 'r', encoding='utf-8') as f:
            content = f.read()
        save_custom_template(name, content)
    elif args.delete_template:
        delete_template(args.delete_template)
    elif args.interactive or len(sys.argv) == 1:
        interactive_mode()
    elif args.csv and args.template:
        run_batch_csv(args.template, args.csv)
    elif args.json and args.template:
        data = json.loads(args.json)
        run_single(args.template, data, args.output)
    else:
        parser.print_help()
