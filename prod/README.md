# Deploy to AWS

Note that this is not necessarily production ready. Just sane defaults for development. 

## Create an S3 bucket

## Create an EC2 Instance

1. Go to AWS console and create the EC2 instance.
    1. `Ubuntu`, `x86`, `t3.medium`, `us-east-1`, `128GB SSD`
1. Security Group:
    1. Port `22` from entire internet `0.0.0.0/0`.
    1. Port `80` from entire internet `0.0.0.0/0`. We will change it later on.
1. Create an IAM group for the EC2. `IAM` -> `Roles` -> `Create Role`
    1. `Trusted Entity Type`: `AWS Service`
    1. `Use case`: `EC2`
    1. Don't add a permission policy (unless already exists), instead click next.
    1. Add a descriptive role name and description and create the role.
    1. Choose the role from the existing roles and click on it.
    1. Click on `Add permissions` and in the dropdown menu `Create inline policy`. Do this twice, the first time, copy the contents from `prod/aws/policies/read-s3-bucket-rag.json` and the 2nd - copy from `prod/aws/policies/RAG-Bedrock-Invoke-access.json`.
1. Attach the policy to the EC2 instance. In `EC2 Instances`, choose the instance we've just created, click on the `Actions` dropdown menu at the top of the screen -> `Security` -> `Modify IAM role`. Choose the role we've just created and save.
1. Follow `server-setup.sh` in order to set up everything in the server. Note that some of the instructions in the file are for manual operations. You can't just run it from beginning to end and expect it to work.
1. Run `server-setup-complimentary.sh` from your local machine.
1. Make sure that everything works by going to your EC2's public domain and making sure that you can interact with the server.

## Protect your instance behind HTTPS

1. Create a CloudFront Distribution
    1. `Origin Domain`: Your EC2's public domain.
    1. `Protocol`: `HTTP only` because your EC2 supports only HTTP.
    1. `Viewer protocol policy`: `Redirect HTTP to HTTPS`
    1. `Web Application Firewall (WAF)`: `Enable` - Choose whatever you prefer.
    1. `Custom SSL certificate`: Skip. We'll use CloudFront's domain.
    1. `Cache policy`: `UseOriginCacheControlHeaders` (should be marked as `Recommended for EC2`)
    1. `Origin rquest policy`: `AllViewer` (should be marked as `Recommended for EC2`)
1. Wait for distribution to deploy, may take a few minutes.
1. Test your CloudFront redirect in the browser.
1. Update EC2's `Security Group`:
    1. Delete the existing rule for port `80`.
    1. Create a new rule for port `80` and set the `source` to `com.amazonaws.global.cloudfront.origin-facing` (under `Prefix lists` section).
1. Test that everything works.
