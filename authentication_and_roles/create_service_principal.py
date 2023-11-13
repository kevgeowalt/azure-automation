import subprocess
import argparse
import json


def parse_aruguments():
    parser = argparse.ArgumentParser(description="Create new service principal")

    parser.add_argument(
        "--name", type=str, required=True, help="Name of the Service Principal"
    )
    parser.add_argument(
        "--scope",
        type=str,
        choices=["group", "sub"],
        required=True,
        help="Currently supports subscription/resourcegroup scope assignment",
    )
    parser.add_argument(
        "--subscription", type=str, required=True, help="Azure Subscription ID"
    )
    parser.add_argument("--role", type=str, required=True, help="Azure RBAC role name")
    parser.add_argument(
        "--group",
        type=str,
        required=False,
        help="Azure Resource Group. Required if the scope is set to group",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        required=False,
        help="Add flag to save credentials to a file. Otherwise credentials will be displayed in console",
    )

    return parser.parse_args()


def main():
    args = parse_aruguments()

    service_principal_name = args.name
    scope = args.scope
    subscription = args.subscription
    save = args.save
    role = args.role
    group = args.group

    full_scope_path = f"/subscriptions/{subscription}"
    if scope == "group":
        if group is None:
            raise Exception(
                "[--group resourceGroupName] is required if scope is set to group"
            )

        full_scope_path = f"{full_scope_path}/resourceGroups/{group}"

    command = f"az.cmd ad sp create-for-rbac --name {service_principal_name} --role {role} --scope {full_scope_path}"

    commands_to_be_processed = command.split()
    process_result = subprocess.run(commands_to_be_processed, stdout=subprocess.PIPE)

    if process_result.returncode == 0:
        output_json = process_result.stdout.decode("utf-8")
        data = json.loads(output_json)

        if save == True:
            filepath = f"credentials.{service_principal_name}.{subscription[0:6]}.json"
            with open(filepath, "w") as file:
                file.write(output_json)
        else:
            print(data)


if __name__ == "__main__":
    main()
