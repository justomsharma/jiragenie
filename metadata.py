def extract_required_fields(meta_response):
    data = meta_response.json()
    fields = {}

    try:
        issue_type = data["projects"][0]["issuetypes"][0]
        for field_key, field_info in issue_type["fields"].items():
            if field_info.get("required"):
                fields[field_key] = field_info
    except Exception:
        pass

    return fields