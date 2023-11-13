import argparse
import sys
import os
import subprocess
import platform
import json

from azure.identity import DefaultAzureCredential
from azure.mgmt.web import WebSiteManagementClient


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
    AZURE_CLIENT_ID = os.environ.get("AZURE_CLIENT_ID", "")
    AZURE_CLIENT_SECRET = os.environ.get("AZURE_CLIENT_SECRET", "")
    AZURE_TENANT_ID = os.environ.get("AZURE_TENANT_ID", "")
    AZURE_SUBSCRIPTION_ID = os.environ.get("AZURE_SUBSCRIPTION_ID", "")
    INTERACTIVE_MODE = False

    def __init__(self) -> None:
        pass


def terminal_parse_arguments():
    try:
        parser = argparse.ArgumentParser(description="")

        parser.add_argument(
            "--storage-account",
            required=False,
            help="Azure Storage Account Name. Build files (.zip) will be stored in [sotrageaccoutname]/builds/[service]/[date]",
        )
        parser.add_argument(
            "--deploy", action="store_true",required=True, help="Deploy to specified Azure Service"
        )
        parser.add_argument("--service", required=True, choices=["func", "app"])
        parser.add_argument(
            "--resource-group",
            required=True,
            help="Resource Group for Service being deployed [Function, App Service]",
        )
        parser.add_argument(
            "--azure-service-name",
            required=True,
            help="Name of the azure function/app service being deployed",
        )
        parser.add_argument(
            "--path",
            required=True,
            help="Full path to source code or publishing directory",
        )

        return parser.parse_args()

    except Exception as e:
        print(str(e))
        sys.exit()


def azure_parse_command(command):
    command = str(command)
    sections = command.split()
    return sections


def azure_login_sp():
    
    if SecureEnvironmentVars.INTERACTIVE_MODE == True:
        # windows sometimes forces third party scripts to use az.cmd when executing processes
        # if running on a windows vm or local machine, thenscript uses 'az.cmd' otherwise
        # uses 'az'
        az_command = "az.cmd" if platform.system().lower() == "windows" else "az"
        login_command = f"{az_command} login --output json"

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
        azure_login_info = None

        if len(login_data_object) > 1:
            for subscription in login_data_object:
                if subscription.get("id") == SecureEnvironmentVars.AZURE_SUBSCRIPTION_ID:
                    target_subscription = subscription
                    break

            if not target_subscription:
                raise Exception(
                    f"No entry found with subscription_id: {SecureEnvironmentVars.AZURE_SUBSCRIPTION_ID}"
                )
        else:
            target_subscription = login_data_object[0]
            SecureEnvironmentVars.AZURE_SUBSCRIPTION_ID = target_subscription.get("id", "")

        azure_login_info = AzureCredentials(
            subscription_id=target_subscription.get("id", ""),
            name=target_subscription.get("name", ""),
            state=target_subscription.get("state", ""),
        )

        return azure_login_info
    else:
        error = ""
        if SecureEnvironmentVars.AZURE_CLIENT_ID == "":
            error += "AZURE_CLIENT_ID environment variable is required when using service principal. "
        
        if SecureEnvironmentVars.AZURE_CLIENT_SECRET == "":
            error += "AZURE_CLIENT_SECRET environment variable is required when using service principal. "
        
        if SecureEnvironmentVars.AZURE_TENANT_ID == "":
            error += "AZURE_TENANT_ID environment variable is required when using service principal. "
            
        if error:
            raise Exception(error)


def azure_webapp_deploy_app(resource_group_name, app_service_name, zip_path = ""):
    credential = DefaultAzureCredential()

    web_client = WebSiteManagementClient(
        credential, SecureEnvironmentVars.AZURE_SUBSCRIPTION_ID
    )

    app_service = web_client.web_apps.get(resource_group_name, app_service_name)
    
    # Todo: * check if available or not in running state
    # 
    
    # with open(zip_path, "rb") as package_file:
    #     result = web_client.web_apps.create_deployment(
    #         resource_group_name,
    #         app_service_name,
    #         {
    #             "packageUri": zip_path,
    #             "name": os.path.basename(zip_path),
    #             "command_id": "deploy",
    #             "is_temp": False,
    #         },
    #     )

    # deployment_id = result.id
    # deployment_status = web_client.deployments.get(resource_group_name, app_service_name, deployment_id)
    # print(f"Deployment Status: {deployment_status.status}")
    
    print(app_service)
    
def main():
    try:
        args = terminal_parse_arguments()
        ARGUMENTS = TerminalArgs(args=args)

        login = azure_login_sp()
        azure_webapp_deploy_app(ARGUMENTS.RESOURCE_GROUP, ARGUMENTS.AZURE_SERVICE_NAME)

    except Exception as e:
        print(str(e))
        sys.exit()


if __name__ == "__main__":
    main()
