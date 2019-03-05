## For CLI (local machine or EC2) users

**NOTE:** Before you run below command, **make sure you have enough privileges.** (such as `AdministratorAccess` policy).

* You may have `AdministratorAccess` privileged **AWS CLI environment** such as your LOCAL MACHINE or your EC2.

  * Download `generate_instance_profile.sh`.

```console
wget https://raw.githubusercontent.com/aws-kr-tnc/moving-to-serverless-workshop-1d/master/resources/generate_instance_profile.sh
```
* If you want, **review** the `generate_instance_profile.sh` file.
```console
wget https://raw.githubusercontent.com/aws-kr-tnc/moving-to-serverless-workshop-1d/master/resources/workshop-cloud9-instance-profile-role-trust.json
wget https://raw.githubusercontent.com/aws-kr-tnc/moving-to-serverless-workshop-1d/master/resources/workshop-cloud9-policy.json

PARN=$(aws iam create-policy --policy-name workshop-cloud9-policy --policy-document file://workshop-cloud9-policy.json --query "Policy.Arn" --output text)
aws iam create-role --role-name workshop-cloud9-instance-profile-role --assume-role-policy-document file://workshop-cloud9-instance-profile-role-trust.json
aws iam attach-role-policy --role-name workshop-cloud9-instance-profile-role --policy-arn $PARN
aws iam create-instance-profile --instance-profile-name workshop-cloud9-instance-profile
aws iam add-role-to-instance-profile --role-name workshop-cloud9-instance-profile-role --instance-profile-name workshop-cloud9-instance-profile
```

 * Add `execute` permission
```console
chmod +x generate_instance_profile.sh
```

 * **Run** script with enough privileges, such as `AdministratorAccess` policy. (**Currently, you can not run this command in Cloud9 terminal.**):
```console
./generate_instance_profile.sh
```

* If you want, **review** the `workshop-cloud9-policy.json` policy.
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "apigateway:*",
                "s3:*",
                "ec2:*",
                "cloudwatch:*",
                "logs:*",
                "iam:*",
                "ssm:*",
                "lambda:*",
                "cloud9:*",
                "dynamodb:*",
                "cognito-idp:*",
                "xray:*"
            ],
            "Resource": "*"
        }
    ]
}

```


#### [1-4] Attach an Instance Profile to Cloud9 Instance with the AWS CLI

* Get instance-id of Cloud9 environment, For this we need **Cloud9 environment name**. We defined it LAB 01. (**workshop-\<INITIAL\>**). 

* Attach an **Instance Profile** which made previous step to Cloud9 Instance.

* Replace **workshop-\<INITIAL\>** to real value.
```console
INSTANCE_ID=$(aws ec2 describe-instances --query "Reservations[*].Instances[*].InstanceId" --filter "Name=tag:Name, Values=aws-cloud9-workshop-<INITIAL>*" --region ap-southeast-1 --output=text)

echo $INSTANCE_ID

aws ec2 associate-iam-instance-profile --iam-instance-profile  Name=workshop-cloud9-instance-profile --region ap-southeast-1 --instance-id $INSTANCE_ID
```
* Run the following command to check the result: 

```console
aws ec2 describe-instances --query "Reservations[].Instances[].IamInstanceProfile" --instance-id $INSTANCE_ID --region ap-southeast-1
```
* output: 
```
[
    {
        "Arn": "arn:aws:iam::123456789012:instance-profile/workshop-cloud9-instance-profile",
        "Id": "AIPAIFQCLU7KO6ML343DDD"
    }
]
```
* Now `workshop-cloud9-instance-profile` is attached our Cloud9 instance.
