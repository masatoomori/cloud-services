#!/bin/zsh

# assume profile profile_name is defined at ~/.aws/credentials with appropriate grants
# ```text
# [profile_name]
# aws_access_key_id = xxx
# aws_secret_access_key = xxx
# ```

CONFIG_FILE="config.json"
AWS_PROFILE=$(cat $CONFIG_FILE | jq '.profile' | sed 's/"//g')
LMABDA_REGION=$(cat $CONFIG_FILE | jq '.region' | sed 's/"//g')
FUNCTION_NAME=$(cat $CONFIG_FILE | jq '.function' | sed 's/"//g')

echo "aws profile: "$AWS_PROFILE
echo "lambda region: "$LMABDA_REGION
echo "function name: "$FUNCTION_NAME

/usr/local/bin/aws lambda invoke \
  --cli-binary-format raw-in-base64-out \
  --profile $AWS_PROFILE \
  --invocation-type RequestResponse \
  --function-name $FUNCTION_NAME \
  --region $LMABDA_REGION \
  --payload file://input_for_invocation.json output.txt
