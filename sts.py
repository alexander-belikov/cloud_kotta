#!/usr/bin/env python

import time
import boto3

# The calls to AWS STS AssumeRole must be signed with the access key ID
# and secret access key of an existing IAM user or using existing temporary 
# credentials. (You cannot call AssumeRole with the access key for the root 
# account.) The credentials can be in environment variables or in a 
# configuration file and will be discovered automatically by the 
# boto3.client() function. For more information, see the Python SDK 
# documentation: http://boto3.readthedocs.org/en/latest/guide/sqs.html


def get_temp_creds(role_arn):
    # create an STS client object that represents a live connection to the 
    # STS service
    sts_client = boto3.client('sts')

    session_name = "Temp_session_{0}".format(int(time.time()))
    
    # Call the assume_role method of the STSConnection object and pass the role
    # ARN and a role session name.
    assumedRoleObject = sts_client.assume_role(RoleArn=role_arn,
                                               RoleSessionName=session_name)
                                           

    credentials = assumedRoleObject['Credentials']
    return credentials

def print_creds(creds):
    print "Expiration : ", creds["Expiration"]
    print "Key Id     : ", creds["AccessKeyId"]
    print "Secret Key : ", creds["SecretAccessKey"]
    print "Token      : ", creds["SessionToken"]


if __name__ == "__main__" :

    print "Running STS tests:"
    # From the response that contains the assumed role, get the temporary 
    # credentials that can be used to make subsequent API calls

    role_pfx = "arn:aws:iam::968994658855:role/"
    roles    = ["klab_public", "wos_read_access", "jstor_access", "god_mode"]
    
    for role in roles:
        credentials = get_temp_creds(role_pfx+role)
        print_creds(credentials)


        # Use the temporary credentials that AssumeRole returns to make a 
        # connection to Amazon S3  
        s3_resource = boto3.resource(
            's3',
            aws_access_key_id = credentials['AccessKeyId'],
            aws_secret_access_key = credentials['SecretAccessKey'],
            aws_session_token = credentials['SessionToken'],
        )

        # Use the Amazon S3 resource object that is now configured with the 
        # credentials to access your S3 buckets. 
        try :
            for bucket in s3_resource.buckets.all():
                print(bucket.name)

        except Exception, e:
            print "Failed to do : list_buckets"

        try :
            
            s3_client = boto3.client(
                's3',
                aws_access_key_id = credentials['AccessKeyId'],
                aws_secret_access_key = credentials['SecretAccessKey'],
                aws_session_token = credentials['SessionToken'],
            )
            print s3_client.list_objects(Bucket='klab-jobs',
                                   MaxKeys=10)

        except Exception, e:
            print "Failed to do : list klab-jobs"
