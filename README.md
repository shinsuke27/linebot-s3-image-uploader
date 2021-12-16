This is a Lambda function that converts the images sent to the LINE BOT into thumbnail images and stores them in AWS S3 along with the original images.

# Deploy steps

- Create LINE provider and messaging API channel for your linebot.
- Build the container image and push it to the ECR with the following command.

```
$ PROJECT_NAME=linebot-s3-image-uploader
$ IMAGE_NAME=linebot-s3-image-uploader
$ AWS_ACCOUNT_ID=123456789012
$ AWS_REGION=ap-northeast-1
$ docker build -t ${IMAGE_NAME}
$ aws ecr get-login-password | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com
$ aws ecr create-repository --repository-name ${PROJECT_NAME} --image-scanning-configuration scanOnPush=true --image-tag-mutability MUTABLE
$ docker tag ${IMAGE_NAME}:latest ${AWS_ACCOUNT_ID}.dkr.ecr.<AWS REGION>.amazonaws.com/${IMAGE_NAME}:latest
$ docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${IMAGE_NAME}:latest
```

- Create an Amazon API Gateway and a container image-based AWS Lambda function and integrate them together, specifying the ECR URI created above as the Lambda container image URI.
- In the Lambda configuration screen, specify the following environment variables.
  - `CHANNEL_ACCESS_TOKEN`: YOUR LINE CHANNEL ACCESS TOKEN
  - `CHANNEL_SECRET`: YOUR LINE SECRET
  - `S3_BUCKET_NAME`: Name of the s3 bucket where the image will be stored
  - `thumbnail_max_size`: Maximum size of thumbnail images created by the bot
  - `reply_message`: The content of the message that the bot responds to when the user sends an image
- Specify the API Gateway endpoint that you created in the Webhook URL in the LINE developer administration screen.
