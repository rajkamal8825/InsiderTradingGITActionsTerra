import pandas as pd
import boto3
#import smtplib, ssl
#from email.mime.text import MIMEText
#from email.mime.multipart import MIMEMultipart
from botocore.exceptions import ClientError

#s3_client = boto3.client('s3')

def lambda_handler(event, context):
  try:
     #companies = ['PTON','AFRM','SNOW','DDOG']
     lstofcompdf =pd.read_csv('nasdaq_screener_largeandmedium.csv')
     lstofcompwithspch = lstofcompdf['Symbol'].to_list()
     companies = [s for s in lstofcompwithspch if s.isalnum()]
     recipients = ["gobikakanagu@gmail.com","rajkamal8825@gmail.com"]#,"nagarajan.83@gmail.com"]


     insider = pd.DataFrame()
     insidergroupedbuy1m = pd.DataFrame()
     insidergroupedsell1m = pd.DataFrame()
     insiderCEObuy = pd.DataFrame()
     #insiderCFObuy = pd.DataFrame()
     insiderCFOsell = pd.DataFrame()
     for company in companies:
       print('running for:',company)
       #insider1 = pd.read_html(f'http://openinsider.com/screener?s={company}&o=&pl=&ph=&ll=&lh=&fd=730&fdr=&td=0&tdr=&fdlyl=&fdlyh=&daysago=&xp=1&xs=1&vl=&vh=&ocl=&och=&sic1=-1&sicl=100&sich=9999&grp=0&nfl=&nfh=&nil=&nih=&nol=&noh=&v2l=&v2h=&oc2l=&oc2h=&sortcol=0&cnt=500&page=1')
       insider1 = pd.read_html(f'http://openinsider.com/screener?s={company}&o=&pl=&ph=&ll=&lh=&fd=3&fdr=&td=0&tdr=&fdlyl=&fdlyh=&daysago=&xp=1&xs=1&vl=&vh=&ocl=&och=&sic1=-1&sicl=100&sich=9999&grp=0&nfl=&nfh=&nil=&nih=&nol=&noh=&v2l=&v2h=&oc2l=&oc2h=&sortcol=0&cnt=100&page=1')
       insider1 = insider1[-3]
       if 'Ticker' in insider1.columns:
	   		  insider = pd.concat([insider,insider1])
	   #finishdata = time.time()
     insider['Value'] = insider['Value'].replace('[\$,]', '', regex=True).astype(int)
     insider['Price'] = insider['Price'].replace('[\$,]', '', regex=True).astype(float)
     insider = insider.sort_values(by=['Value','Ticker'], ascending=False)
     #insider.to_csv('insider.csv')
     insidergroupedbuy1m = insider.groupby(['Ticker']).agg({'Value':'sum', 'Price':'mean', 'Trade Date':'max','Filing Date':'max'}).rename(columns={'Value':'Total$Value', 'Price':'AvgPrice','Trade Date':'LatestTradeDate','Filing Date':'LatestFilingDate'})
     insidergroupedbuy1m = insidergroupedbuy1m.loc[insidergroupedbuy1m['Total$Value']>900000]
     insidergroupedbuy1m = insidergroupedbuy1m.sort_values(by=['Total$Value'], ascending=False)
     insidergroupedsell1m = insider.groupby(['Ticker']).agg({'Value':'sum', 'Price':'mean', 'Trade Date':'max','Filing Date':'max'}).rename(columns={'Value':'Total$Value', 'Price':'AvgPrice','Trade Date':'LatestTradeDate','Filing Date':'LatestFilingDate'})
     insidergroupedsell1m = insidergroupedsell1m.loc[insidergroupedsell1m['Total$Value']<-1000000]
     insidergroupedsell1m = insidergroupedsell1m.sort_values(by=['Total$Value'], ascending=True)
     insiderCEObuy = insider[insider['Title'].str.contains('CEO', regex=False, case=False, na=False) & insider['Trade Type'].str.contains('Purchase', regex=False, case=False, na=False)]
     #insiderCFObuy = insider[insider['Title'].str.contains('CFO', regex=False, case=False, na=False) & insider['Trade Type'].str.contains('Purchase', regex=False, case=False, na=False)]
     insiderCFOsell = insider[insider['Title'].str.contains('CFO', regex=False, case=False, na=False) & insider['Trade Type'].str.contains('Sale', regex=False, case=False, na=False)]
     #print(insidergroupedbuy1m)
     #print(insidergroupedsell1m)
     #print(insiderCEObuy)

     #Send the results in an email 
     sender_email = "rajtradebot8825@gmail.com"

     #message = MIMEMultipart("alternative")
     #message["Subject"] = "Insider Trade In Last 3 Days-Lambda"
     #message["From"] = sender_email
     #message["To"] = ""


     # Create the plain-text and HTML version of your message
     html = """\
     <html>
     <head>CEOBuy:</head>
     <body>
        """+insiderCEObuy.to_html()+"""
     </body>
     <head>CFOSell:</head>
     <body>
        """+insiderCFOsell.to_html()+"""
     </body>
     <head>Buy:</head>
     <body>
        """+insidergroupedbuy1m.to_html()+"""
     </body>
     <head>Sell:</head>
     <body>
        """+insidergroupedsell1m.to_html()+"""
     </body>  
     </html>
     """

     # Turn these into plain/html MIMEText objects
     #part1 = MIMEText(html, "html")


     # Add HTML/plain-text parts to MIMEMultipart message
     # The email client will try to render the last part first
     #message.attach(part1)

     # for person in recipients:
       # # Create secure connection with server and send email
       # context = ssl.create_default_context()
       # with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
         # server.login(sender_email, password)
         # server.sendmail(
                        # sender_email, person, message.as_string()
                # )
         # server.quit

     AWS_REGION = "us-east-1"
     Subject = "Insider Trade In Last 3 Days-Lambda"
     CHARSET="UTF-8"
     ses_client = boto3.client('ses',region_name=AWS_REGION)
     
     try:
        for person in recipients:
            response = ses_client.send_email(
                Destination={
                    'ToAddresses':[
                        person,
                        ],
                        },
                        Message={
                        'Body':{
                            'Html':{
                            'Charset': CHARSET,
                            'Data':html,
                            },
                            },
                            
                        'Subject':{
                            'Charset':CHARSET,
                            'Data': Subject,
                            },
                            },
                            Source=sender_email,
                            )
            print("Email Sent to:",person)
            print("Messageid:",response['MessageId'])
     except ClientError as e:
        print(e.response['Error']['Message'])

     
        

  except Exception as err:
    print(err)
