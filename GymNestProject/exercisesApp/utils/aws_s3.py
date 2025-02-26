import boto3
from .db_connection import get_db_connection
from urllib.parse import quote

# docker exec -it django-GymNest-container bash
# python -m exercisesApp.utils.aws_s3


region_name = 'eu-central-1'
bucket_name = 'gymnest'
folder_name = 'image_outputs/'
cloudfront_domain = "d16bmxr9qjek07.cloudfront.net"

session = boto3.Session()
credentials = session.get_credentials()

if credentials:
    print("AWS Credentials Loaded Successfully")
else:
    print("Failed to load AWS credentials")
s3 = session.client('s3')
db_connection = get_db_connection('aws_s3')

cursor = db_connection.cursor()

response = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_name)

if 'Contents' in response:
    for obj in response['Contents']:
        image_name = obj['Key']
        if image_name.endswith(('jpg', 'jpeg', 'png', 'gif')):
            # raw_image_url = f"https://{bucket_name}.s3.{region_name}.amazonaws.com/{image_name}"
            raw_image_url = f"https://{cloudfront_domain}/{image_name}"
            image_url = quote(raw_image_url, safe=':/')  # Encode spaces in URL Encode spaces as %20 in URLs.
            extracted_name = image_name.split('/')[-1].split('.')[0]  # Remove folder path and extension
            extracted_name = extracted_name.replace('_', ' ').title()



            # Update the Exercise table where name_of_exercise matches the extracted name
            update_query = """
                UPDATE Exercise
                SET linkForImage = %s
                WHERE name_of_exercise = %s
            """
            cursor.execute(update_query, (image_url, extracted_name))

            # print(f"Updated linkForImage for exercise: {extracted_name} - {image_url}")
    print('Finshed Import Images From AWS')
db_connection.commit()

cursor.close()
db_connection.close()
