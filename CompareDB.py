#DOCUMENTATION: The script below retrieves contact email addresses from two different sources, ServiceNow and Okta, and then compares the two lists to find the difference. The script posts the difference to SeviceNow.
# Import modules
import re
import requests
import csv
import json

# Define a list of strings to remove from the email lists
remove_strings = ["XXXX@", "YYYYY@", "ZZZZZ@"]

# Get all ServiceNow contact email addresses
auth = ('user', 'pwt')
ServiceNow_contacts = requests.get('https://api..net/rest/contacts/',
                                   auth=auth)
ServiceNow_contacts_dict = json.loads(ServiceNow_contacts.text)
ServiceNow_Emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.(?:[Gg][Oo][Vv]|[Oo][Rr][Gg])\b',
                               str(ServiceNow_contacts_dict))
# Remove email addresses starting with specified strings
ServiceNow_Emails = [email for email in ServiceNow_Emails if not any(email.startswith(s) for s in remove_strings)]
with open("ServiceNow_Emails", "a") as f:
    for email in ServiceNow_Emails:
        print(email, file=f)

# Get all Okta contact email addresses
headers = dict(Authorization='SSWS00eDV26rp1Q-zU807BJZJtrjv9kojHCLoi8UvtrAE-')
Okta_contacts = requests.get('https://SampleT-admin.okta.com/api/v1/groups/users?',
                             headers=headers)
Okta_contacts_dict = json.loads(Okta_contacts.text)
Okta_Emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.(?:[Gg][Oo][Vv]|[Oo][Rr][Gg])\b',
                         str(Okta_contacts_dict))
# Remove email addresses starting with specified strings
Okta_Emails = [email for email in Okta_Emails if not any(email.startswith(s) for s in remove_strings)]
with open("Okta_Emails", "a") as f:
    for email in Okta_Emails:
        print(email, file=f)

# Get the difference between the Okta_Emails and ServiceNow_Emails
difference = list(set(Okta_Emails) - set(ServiceNow_Emails))
with open("Okta_ServiceNow_email_differences.txt", "w") as f:
    for email in difference:
        print(email, file=f)
with open("Okta_ServiceNow_email_differences.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["firstName", "lastName", "externalId", "recordTypeId", "ssoUserId"])
    for email in difference:
        firstName, *lastName = email.split('@')[0].split('.')
        lastName = ' '.join(lastName)
        if not lastName:
            continue  # skip email addresses with lastName = 'Unknown'
        externalId = email
        recordTypeId = '{:.0f}'.format(3289880524226574)
        ssoUserId = email
        writer.writerow([firstName, lastName, externalId, recordTypeId, ssoUserId])
url = 'https://api.ServiceNow.net/rest/contacts/2624538550468614?pageSize=3000'
headers = {'Content-Type': 'application/json'}
with open("Okta_ServiceNow_email_differences.csv", "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        data = dict(firstName=row["firstName"], lastName=row["lastName"], externalId=row["externalId"],
                    recordTypeId=row["recordTypeId"], ssoUserId=row["ssoUserId"])
url = 'https://api.ServiceNow.net/rest/contacts/2624538550468614?pageSize=3000'
headers = {'Content-Type': 'application/json'}
with open("Okta_ServiceNow_email_differences.csv", "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        data = dict(firstName=row["firstName"], lastName=row["lastName"], externalId=row["externalId"],
                    recordTypeId=row["recordTypeId"], ssoUserId=row["ssoUserId"])
        # Post the difference between the Okta_Emails and ServiceNow_Emails to ServiceNow
        response = requests.post(url, auth=auth, json=data)
        # Check whether the post was successful
        if response.status_code in [200, 201]:
            print("Data posted successfully:", data)
        else:
            print("An error occurred while posting data:", data)
            print("Status code:", response.status_code)
            print("Response content:", response.text)
