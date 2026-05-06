from apps.courses.models import Technology


def get_technologies_by_category():
    """
    Returns technologies grouped by category in the format:
    [
        {
            "label": "Frontend",
            "options": [
                {"label": "React", "value": "react"},
                {"label": "Vue", "value": "vue"}
            ]
        },
        {
            "label": "Backend",
            "options": [
                {"label": "Node.js", "value": "node"},
                {"label": "Django", "value": "django"}
            ]
        }
    ]
    """
    technologies = Technology.objects.all().order_by('category', 'label')
    
    # Group by category
    categories = {}
    for tech in technologies:
        category_display = tech.get_category_display()
        if category_display not in categories:
            categories[category_display] = []
        
        categories[category_display].append({
            "label": tech.label,
            "value": tech.value
        })
    
    # Convert to the requested format
    result = []
    for category_label, options in categories.items():
        result.append({
            "label": category_label,
            "options": options
        })
    
    return result
