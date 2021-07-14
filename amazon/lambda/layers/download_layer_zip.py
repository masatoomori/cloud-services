import argparse
import re

import boto3
import requests

LAYER_LIST_URL = 'https://github.com/keithrozario/Klayers/blob/master/deployments/python3.8/arns/ap-northeast-1.csv'
ARN_EXAMPLE = 'arn:aws:lambda:ap-northeast-1:770693421928:layer:Klayers-python38-pandas:35'


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('-a', '--arn', default=None)
	args = parser.parse_args()

	if not args.arn:
		print('Specify Lambda Layer to download by ARN')
		print('Layer list is available at {}'.format(LAYER_LIST_URL))
		exit()

	arn = args.arn

	client = boto3.client('lambda')
	response = client.get_layer_version_by_arn(Arn=arn)
	location_url = response['Content']['Location']
	print(location_url)

	data = requests.get(location_url).content

	zip_file_name = re.split(':', arn)[-2] + '.zip'
	print(zip_file_name)

	with open(zip_file_name, 'wb') as f:
		f.write(data)


if __name__ == '__main__':
	main()
