# Python script for AWS Assume Operation
AWS_PYTHON_SCRIPT=set_aws_env.py

# Assume AWS role.  It tries to assume the aws role and on success creates new assume profile in ~/.aws/credentials and set AWS environment variables in current shell.
# If assumed role profile is already there then it checks if session for that is expried or not.
# And if it is not  expired then just read those varibles from file and set AWS env vars in current shell.
# It prints message on error.
# Parameters:
# <profile name> : Profile which will be used to assume. This should be present in ~/.aws/config and sshould have atleast below keys:
# [dev]
# source_profile = default
# role_arn = arn:aws:iam::<account>:role/<role-name>
# mfa_serial = arn:aws:iam::<mfa account>:mfa/<username>>
# region = us-east-2
# <assume-profile-name> : Temporary Name of a profile to store assumed crednetials. These will be store in ~/.aws/credentials file.
aws_assume () {
  unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN AWS_PROFILE
  status=$( python3 $AWS_PYTHON_SCRIPT expired $1 $2 $3 0)
  if [ "$status" == "True" ]
  then
    echo "MFA Token:"
    read mfa_token
    aws_assume_set $1 $2 $3 $mfa_token
  else
        aws_assume_set $1 $2 $3 0
fi

}

# Helper function for aws_assume.
aws_assume_set () {
  output=$( python3 $AWS_PYTHON_SCRIPT assume $1 $2 $3 $4 )
  $( echo "$output" | jq -r 'keys[] as $k | "export \($k)=\(.[$k])"' )
  echo "Environment Set"
}


