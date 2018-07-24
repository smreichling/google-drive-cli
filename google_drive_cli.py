'''
Usage:
	google_drive_cli.py <directory>
'''

from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import sys
import json
from docopt import docopt

TOKEN_FILE = '/tmp/google_drive_cli_token.json'
SCOPES = 'https://www.googleapis.com/auth/drive'


def fatal(msg):
	sys.stderr.write('ERROR: {msg}\n'.format(msg=msg))
	sys.exit(1)

def get_service():
	store = file.Storage(TOKEN_FILE)
	creds = store.get()
	if not creds or creds.invalid:
	    flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
	    creds = tools.run_flow(flow, store)
	service = build('drive', 'v3', http=creds.authorize(Http()))
	return service

def print_file_tree(service, file_object, indent=''):
	print(indent + file_object['name'])
	if file_object['mimeType'] != 'application/vnd.google-apps.folder':
		return

	query = '\'{file_id}\' in parents'.format(file_id=file_object['id'])

	response = service.files().list(q=query, fields='*').execute()
	while True:
		for child_file in response['files']:
			print_file_tree(service, child_file, indent + '  ')
		if 'nextPageToken' not in response:
			break
		response = service.files().list(q=query, pageToken=response['nextPageToken'], fields='*').execute()


def main(args):
	dir_name = args['<directory>']
	service = get_service()

	response = service.files().list(q='name = \'{dir_name}\''.format(dir_name=dir_name), fields="*").execute()
	if not response['files']:
		fatal('No file found with name {dir_name}'.format(dir_name=dir_name))

	found_file = response['files'][0]
	print_file_tree(service, found_file)


if __name__ == '__main__':
	main(docopt(__doc__))
