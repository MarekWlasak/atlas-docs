#!/usr/bin/env python3
#
# Script that uploads the docs to  https://sites.ecmwf.int/docs/atlas/
#
# To install sites-toolkit:
#
#     pip install sites-toolkit --upgrade -index-url https://${user}:${password}@nexus.ecmwf.int/repository/pypi-all/simple

from sites.toolkit.file_manager import Authenticator, FileManager, Site

import argparse
from pathlib import Path

scripts = Path(__file__).parent.resolve()
atlas_docs = scripts.parent.resolve()

parser = argparse.ArgumentParser(description='Generate Doxyfile')
parser.add_argument('--token', type=str, default="")
parser.add_argument('--user', type=str, default="")
parser.add_argument('--password', type=str, default="")
parser.add_argument('--html', type=str, default=atlas_docs/'build/html')

args = parser.parse_args()

if args.user and args.password :
    print( "Authentication via user/password" )
    my_authenticator = Authenticator.from_credentials(username=args.user,password=args.password)
elif args.token :
    print( "Authentication via token",args.token )
    my_authenticator = Authenticator.from_token(token=args.token)
else :
    print( "ERROR: no token, or user/password was provided" )
    from sys import exit
    exit(1)
    
# Create a Site instance
my_site = Site(space='docs', name='atlas', authenticator=my_authenticator)

# Create a FileManager instance
my_site_manager = FileManager(site=my_site)

# Upload all the contents of a directory inside the content directory
my_site_manager.upload(local_path=args.html)
