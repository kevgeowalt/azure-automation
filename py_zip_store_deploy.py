import argparse
import sys
import os
import subprocess
import platform
import json


class AzureCredentials:
    def __init__(self, subscription_id, name, state):
        self.subscription_id = subscription_id
        self.name = name
        self.state = state


class TerminalArgs:
    def __init__(self, args):
        self.STORAGE_ACCOUNT = args.storage_account
        self.DEPLOY = args.deploy
        self.SERVICE = args.service
        self.RESOURCE_GROUP = args.resource_group
        self.AZURE_SERVICE_NAME = args.azure_service_name


class SecureEnvironmentVars:
    SERVICE_PRINCIPAL_ID = os.environ.get("AZURE_SERVICE_PRINCIPAL_ID", "")
    SERVICE_PRINCIPAL_SECRET = os.environ.get("AZURE_SERVICE_PRINCIPAL_SECRET", "")
    TENANT_ID = os.environ.get("AZURE_TENANT_ID", "")
    SUBSCRIPTION_ID = os.environ.get("AZURE_SUBSCRIPTION_ID", "")

    def __init__(self) -> None:
        pass


def terminal_parse_arguments():
    try:
        parser = argparse.ArgumentParser(description="")

        parser.add_argument(
            "--storage-account",
            required=True,
            help="Azure Storage Account Name. Build files (.zip) will be stored in [sotrageaccoutname]/builds/[service]/[date]",
        )
        parser.add_argument(
            "--deploy", action="store_true", help="Deploy to specified Azure Service"
        )
        parser.add_argument("--service", required=True, choices=["func", "app"])
        parser.add_argument(
            "--resource-group",
            required=False,
            help="Resource Group for Service being deployed [Function, App Service]",
        )
        parser.add_argument(
            "--azure-service-name",
            required=False,
            help="Name of the azure function/app service being deployed",
        )

        return parser.parse_args()

    except Exception as e:
        print(str(e))
        sys.exit()


def azure_parse_command(command):
    command = str(command)
    sections = command.split()
    return sections


def azure_login_sp(useInteractive=True):
    # windows sometimes forces third party scripts to use az.cmd when executing processes
    # if running on a windows vm or local machine, thenscript uses 'az.cmd' otherwise
    # uses 'az'
    az_command = "az.cmd" if platform.system().lower() == "windows" else "az"
    login_command = ""

    if useInteractive:
        # opens a browser
        login_command = f"{az_command} login --output json"
    else:
        # uses service principal for non-interactive login
        login_data = ""

    secure_login = subprocess.Popen(
        azure_parse_command(login_command),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    output, error = secure_login.communicate()

    if secure_login.returncode != 0:
        raise Exception(f"Azure Login Process Failed: {error.decode()}")

    login_data = output.decode()
    login_data_object = json.loads(login_data)

    target_subscription = None
    azure_login_info   = None
    
    if len(login_data_object) > 1:      
        for subscription in login_data_object:
            if subscription.get("id") == SecureEnvironmentVars.SUBSCRIPTION_ID:
                target_subscription = subscription
                break

        if not target_subscription:
            raise Exception(
                f"No entry found with subscription_id: {SecureEnvironmentVars.SUBSCRIPTION_ID}"
            )
    else:
        target_subscription = login_data_object[0]
        
    azure_login_info = AzureCredentials(
            subscription_id=target_subscription.get("id", ""),
            name=target_subscription.get("name", ""),
            state=target_subscription.get("state", ""),
        )
    
    return azure_login_info


def main():
    try:
        args = terminal_parse_arguments()
        ARGUMENTS = TerminalArgs(args=args)

        login = azure_login_sp()
        
    except Exception as e:
        print(str(e))
        sys.exit()


if __name__ == "__main__":
    main()
