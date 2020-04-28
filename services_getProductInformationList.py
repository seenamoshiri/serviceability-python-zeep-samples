"""Serviceability Control Center Services <getProductInformationList> sample script

Performs a <getProductInformationList> request using the Zeep SOAP library, and 
parses/prints the <Product> results in a simple table output.

Dependency Installation:

    $ pip3 install -r requirements.txt

Copyright (c) 2018 Cisco and/or its affiliates.
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from lxml import etree
from requests import Session
from requests.auth import HTTPBasicAuth

from zeep import Client, Settings, Plugin
from zeep.transports import Transport
from zeep.exceptions import Fault

# Edit .env file to specify your Webex site/user details
import os
from dotenv import load_dotenv
load_dotenv()

# Change to true to enable output of request/response headers and XML
DEBUG = False

# The WSDL is a local file in the working directory, see README
WSDL_FILE = 'schema/ControlCenterServices.wsdl'

# This class lets you view the incoming and outgoing HTTP headers and XML

class MyLoggingPlugin( Plugin ):

    def egress( self, envelope, http_headers, operation, binding_options ):

        # Format the request body as pretty printed XML
        xml = etree.tostring( envelope, pretty_print = True, encoding = 'unicode')

        print( f'\nRequest\n-------\nHeaders:\n{http_headers}\n\nBody:\n{xml}' )

    def ingress( self, envelope, http_headers, operation ):

        # Format the response body as pretty printed XML
        xml = etree.tostring( envelope, pretty_print = True, encoding = 'unicode')

        print( f'\nResponse\n-------\nHeaders:\n{http_headers}\n\nBody:\n{xml}' )

# The first step is to create a SOAP client session

session = Session()

# We disable certificate verification by default

session.verify = False

# To enabled SSL cert checking (recommended for production)
# place the CUCM Tomcat cert .pem file in the root of the project
# and uncomment the two lines below

# CERT = 'changeme.pem'
# session.verify = CERT

session.auth = HTTPBasicAuth( os.getenv( 'USERNAME' ), os.getenv( 'PASSWORD' ) )

transport = Transport( session = session, timeout = 10 )

# strict=False is not always necessary, but it allows zeep to parse imperfect XML
settings = Settings( strict = False, xml_huge_tree = True )

# If debug output is requested, add the MyLoggingPlugin class
plugin = [ MyLoggingPlugin() ] if DEBUG else [ ]

# Create the Zeep client with the specified settings
client = Client( WSDL_FILE, settings = settings, transport = transport, plugins = plugin )

# Create the Zeep service binding to the Perfmon SOAP service at the specified CUCM
service = client.create_service(
    '{http://schemas.cisco.com/ast/soap}ControlCenterServicesBinding',
    f'https://{ os.getenv( "CUCM_ADDRESS" ) }:8443/controlcenterservice2/services/ControlCenterServices' 
    )

# Execute the request
try:
	resp = service.getProductInformationList( '' )
except Fault as err:
	print( f'Zeep error: getProductInformationList: {err}' )
else:
	print( "\ngetProductInformationList response:\n" )
	print( resp,"\n" )

input( 'Press Enter to continue...' )

# Create a simple report of the XML response
print( '\nInstalled Products' )
print( ( '=' * 65 ) + '\n' )

# Loop through the top-level of the response object
for item in resp.Products.item:

    # Extract the Product name/version values
    productName = item.ProductName
    productVersion = item.ProductVersion

    # Print the name and version, padding/truncating the name to 49 characters
    print( '{:49.49}'.format( productName ) + 'v' + productVersion )



