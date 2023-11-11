import argparse
import sys

# central config for easy config update
# help: represents the help text shown when executing script `python3 pz_zip_store_deploy.py -h`
# code: represents the terminal parameter when executing script `python3 pz_zip_store_deploy.py -s [service_principal_id]`
# arugument_name: represents the name attached to the code `python3 pz_zip_store_deploy.py --principal [service_principal_id]`
PARSER_CONFIG = {
    "s": {
        "help": "Azure Service Principal ID",
        "code": "-s",
        "arugment_name": "--principal",
    },
}

# get help text associated with a specific key
def get_help_msg(key, inner_key="help"):
    body = PARSER_CONFIG[key]
    return body[inner_key]

# get code text associated with a specific key
def get_argument_id(key, inner_key="code"):
    body = PARSER_CONFIG[key]
    return body[inner_key]

# get arument name text associated with a specific key
def get_argument_name(key, inner_key="arugment_name"):
    body = PARSER_CONFIG[key]
    return body[inner_key]

# configure argparse library
def terminal_argument_parse():
    try:
        parser = argparse.ArgumentParser(description="")

        parser.add_argument(
            get_argument_id("s"),
            get_argument_name("s"),
            type=str,
            help=get_help_msg("s"),
        )
        parser.add_argument(
            "-p",
            "--password",
            type=str,
            help="Password associated with Service Principal",
        )
        parser.add_argument("-t", "--tenant", type=str, help="Tenant ID")
        parser.add_argument("-x", "--subscription", type=str, help="Subscription ID")
        parser.add_argument(
            "-d",
            "--directory",
            type=str,
            help="Full path to the folder to be deployed.",
        )

        args = parser.parse_args()

        return args
    except Exception as e:
        print(str(e))
        sys.exit()


def main():
    try:
        args = terminal_argument_parse()
        CONFIG = {
            "principal": args.principal,
            "password": args.password,
            "tenant": args.tenant,
            "subscription": args.subscription,
            "directory": args.directory,
        }

        print(CONFIG["principal"])
    except Exception as e:
        print(str(e))
        sys.exit()


if __name__ == "__main__":
    main()
