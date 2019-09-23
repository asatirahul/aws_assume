import configparser
import os
import calendar
import time
import boto3
import sys
import json

class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self

def get_aws_file(filename):
    aws_dir = os.path.join(os.environ["HOME"], ".aws")
    config_path = os.path.join(aws_dir, filename)
    return config_path

def get_config_obj(filename):
    config = configparser.ConfigParser(dict_type=AttrDict)
    config.optionxform = str
    config.read(get_aws_file(filename))
    return config

def is_profile_present(profile):
    config = get_config_obj("config")
    return profile in config._sections

def get_role_arn(profile):
    config = get_config_obj("config")
    return config._sections[profile]["role_arn"]

def get_role_mfa(profile):
    config = get_config_obj("config")
    return config._sections[profile]["mfa_serial"]

def get_profile_aws_region(profile_name):
    config = get_config_obj("config")
    return config._sections[profile_name]['region']

def get_assume_role_expiry(assume_profile_name):
    config = get_config_obj("credentials")
    if assume_profile_name not in config._sections:
        return 0
    return int(config._sections[assume_profile_name]["EXPIRY"])

def get_credentials_from_file(assume_profile_name):
    config = get_config_obj("credentials")
    out = config._sections[assume_profile_name]
    out['AWS_PROFILE'] = assume_profile_name
    return json.dumps(out)

def is_session_expired(assume_profile_name):
    current_time = calendar.timegm(time.gmtime())
    return current_time > get_assume_role_expiry(assume_profile_name)

def assume_role(profile_name, aws_username, duration, mfa_token):
    role_arn = get_role_arn(profile_name)
    mfa = get_role_mfa(profile_name)
    role_session_name = aws_username + str(time.time())
    sts_client = boto3.client("sts")
    resp = sts_client.assume_role(
        RoleArn=role_arn,
        RoleSessionName=role_session_name,
        DurationSeconds=duration,
        SerialNumber=mfa,
        TokenCode=mfa_token,
    )
    return resp["Credentials"]


def update_credentials_file(assume_profile_name, credentials, aws_region, duration):
    credentials_path = get_aws_file("credentials")
    config = get_config_obj("credentials")

    if assume_profile_name not in config.sections():
        config.add_section(assume_profile_name)

    assert assume_profile_name in config.sections()

    config[assume_profile_name]["AWS_ACCESS_KEY_ID"] = credentials["AccessKeyId"]
    config[assume_profile_name]["AWS_SECRET_ACCESS_KEY"] = credentials["SecretAccessKey"]
    config[assume_profile_name]["AWS_SESSION_TOKEN"] = credentials["SessionToken"]
    config[assume_profile_name]["region"] = aws_region
    config[assume_profile_name]["EXPIRY"] = str(calendar.timegm(time.gmtime()) + duration)

    config.write(open(credentials_path, "w"), space_around_delimiters=False)


def save_assumed_role_credentials(profile_name, assume_profile_name, aws_username, duration, mfa_token):
    if is_session_expired(assume_profile_name):
        credentials = assume_role(profile_name, aws_username, duration, mfa_token)
        aws_region = get_profile_aws_region(profile_name)
        update_credentials_file(assume_profile_name, credentials, aws_region, duration)
    return get_credentials_from_file(assume_profile_name)

if __name__ == "__main__":
    action = sys.argv[1]
    profile_name = "profile " + sys.argv[2]
    assume_profile_name = sys.argv[3]
    duration = int(sys.argv[4])
    mfa_token = sys.argv[5]
    username = "aws_session"
    try:
        if action == "expired":
            print(is_session_expired(assume_profile_name))
        elif action == "assume":
            print(save_assumed_role_credentials(profile_name, assume_profile_name, username, duration, mfa_token))
        else:
            print("Unsupported action")
    except Exception as e:
        print("Error in processing profile:")
        print(e)