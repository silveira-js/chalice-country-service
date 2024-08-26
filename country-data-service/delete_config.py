import json

def create_delete_config():
    config = {
        "version": "2.0",
        "app_name": "country-data-service",
        "stages": {
            "dev": {
                "api_gateway_stage": "api",
                "manage_iam_role": True,
                "subnet_ids": [],
                "security_group_ids": []
            }
        }
    }

    with open('.chalice/config.json', 'w') as f:
        json.dump(config, f, indent=2)

if __name__ == "__main__":
    create_delete_config()
