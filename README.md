Uitlity to assume AWS role and share that role across multiple open terminals. 

When called the first time, it will assume the AWS role and set AWS variables in the current terminal. After that, if this is executed on another terminal, it will first check if session for that role is already present and if it is and session for that is not expired then it reads the details of that session from local AWS credentials file and set AWS variables in current terminal.

## Program Flow

1. Check if role is already assumed before by checking ~/.aws/credentials file.
2. Ask user to input MFA.
3. Assume role.
4. Update ~/.aws/crednetinals file.
5. Set AWS variables in current session. 
6. Exit.
7. Check if session is already expired. If yes then go to step 2. If session is not expired then go to step 8.
8. Read details of assumed role from ~/.aws/credentials file.
9. Set AWS variables in current session. 
10. Exit.

## Setup
Clone the repository and run:
```sh
source aws_login.sh
```
Then assume role using the commnad mentioned in [Command](command) section.

## Command
```bash
aws_assume <profile to assume> <profile name to store assumed credentials> <session duration in seconds>
```

**Example**
```bash
aws_assume dev assume-dev 1000
```

#### Parmaeters
- **profile_to_assume** : Name of profile to assume. This profile should be present in ~/.aws/config file and should have atleast below details:
```
[profile dev]
role_arn = <role_arn>
mfa_serial = <mfa_serial>
region = <aws_region>
```

- **assumed_profile_name** : Profile name to store crednetials of assumed role. This profile will be stored in ~/.aws/credentials file.

- **session_duraion** : Duration of session in seconds.
