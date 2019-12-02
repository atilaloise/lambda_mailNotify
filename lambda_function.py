import boto3
from botocore.exceptions import ClientError
import gzip
import json
import xmltodict
import base64


def lambda_handler(event, context):
   #print(f'Logging Event: {event}') 
   #print(f"Awslog: {event['awslogs']}")
   cw_data = event['awslogs']['data']
   #print(f'data: {cw_data}')
   #print(f'type: {type(cw_data)}')
   compressed_payload = base64.b64decode(cw_data)
   uncompressed_payload = gzip.decompress(compressed_payload)
   payload = json.loads(uncompressed_payload)
   log_events = payload['logEvents']
   message = []
   for log_event in log_events:
      doc = xmltodict.parse(log_event['message'])
      message.append(json.dumps(doc))
   
   #filtro = [ ]
   filtro = ["EntryId", "Sql_Text", "DB_User", "OS_User"]
   

   strTable = "<table>"

   for event in message:
      a = json.loads(event)
      strRW = ''
      
      if not filtro:
         for chave in a['AuditRecord']:
            header = "<th>"+chave+"</th>"
            strTable = strTable+header

            rows = "<td>"+a['AuditRecord'][chave]
            strRW = strRW+rows
                  
      else:
         for chave in filtro:
            for x in a['AuditRecord']:
               if x == chave:
                  
                  header = "<th>"+chave+"</th>"
                  strTable = strTable+header

                  rows = "<td>"+a['AuditRecord'][chave]
                  strRW = strRW+rows
         
      strRW = "<tr>"+strRW+"</tr>"
      strTable = strTable+strRW
      strTable = strTable+"</table>"

   SENDER = "MONITORAMENTO <monitoramento@yourcompany.com>"
   RECIPIENT = "monitoramento@yourcompany.com"
   AWS_REGION = "us-east-1"
   SUBJECT = "Cloud Watch Events"

               
   BODY_HTML = """<html>
   <head>
   <style>
   table {{
   font-family: "Trebuchet MS", Arial, Helvetica, sans-serif;
   border-collapse: collapse;
   width: 100%;
   }}

   td, th {{
   border: 1px solid #ddd;
   padding: 8px;
   }}

   th {{
   padding-top: 12px;
   padding-bottom: 12px;
   text-align: left;
   background-color: #4CAF50;
   color: white;
   }}
   </style>
   </head>
   <body>
   <h1>Eventos Reportados por CLOUDWATCH</h1>
   {}
   </body>
   </html>
               """.format(strTable)          

   CHARSET = "UTF-8"

   client = boto3.client('ses',region_name=AWS_REGION)

   try:
      response = client.send_email(
         Destination={
               'ToAddresses': [
                  RECIPIENT,
               ],
         },
         Message={
               'Body': {
                  'Html': {
                     'Charset': CHARSET,
                     'Data': BODY_HTML,
                  },
                  'Text': {
                     'Charset': CHARSET,
                     'Data': BODY_HTML,
                  },
               },
               'Subject': {
                  'Charset': CHARSET,
                  'Data': SUBJECT,
               },
         },
         Source=SENDER,
         
      )
   except ClientError as e:
      print(e.response['Error']['Message'])
   else:
      print("Email sent! Message ID:"),
      print(response['MessageId'])