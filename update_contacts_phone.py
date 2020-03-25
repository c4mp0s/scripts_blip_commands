# encoding=utf-8
from blip_session import BlipSession
from datetime import datetime
import json
import re
import sys
import csv

class Commands:
    def __init__(self, key):
        self.bot_key = key
        self.commmad_get_all_contacts ={  
            "method": "get",
            "uri": "/contacts?$skip=0&$take=999999"
        }
        self.command_set_contact = {
            "method": "set",
            "uri": "/contacts",
            "type": "application/vnd.lime.contact+json",
            "resource":{}
        }

def is_number(value):
    try:
        float(value)
    except ValueError:
        return False
    return True

def remove(phone_number): 
    rmDigits = '\D'
    rmExtras = '(^550|^55|^0)'
    phone_number = re.sub(rmDigits, '', phone_number) 
    if(len(phone_number) > 11):
        phone_number = re.sub(rmExtras, '', phone_number) 
    return phone_number

def validate(phone_number):
    phone_number = remove(phone_number)
    valid = False
    if(phone_number):
        if(len(phone_number) >= 10 and len(phone_number) <= 11):
            valid = True
    return {
        "isValid": valid,
        "match": phone_number
    }
def output_file_updated_contacts(data_list):
    with open(datetime.now().strftime("%d-%m-%Y_%H-%M")+'changed_contacts.csv', 'w',encoding='utf8', newline='') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerows(data_list)

def get_all_contacts(commands, bs):
    all_contacts = bs.process_command(commands.commmad_get_all_contacts)
    if('code' in all_contacts and all_contacts['code'] == 31):
        print("key inválida")
        sys.exit()
    file_backup = open(datetime.now().strftime("%d-%m-%Y_%H-%M")+'backup.json', 'w', encoding='utf8')
    file_backup.write(str(all_contacts))
    file_backup.close()
    return all_contacts

def get_contacts_from_whatsapp(data):
    contacts = data['resource']['items']
    contacts_from_whatsapp = [contact for contact in contacts if 'source' in contact  if contact['source'] == 'WhatsApp' ]
    return contacts_from_whatsapp

def contacts_invalid_format(contacts_from_whatsapp):
    object_response = []
    for contact in contacts_from_whatsapp:
        if('phoneNumber' in contact and (len(contact["phoneNumber"]) < 10 or len(contact["phoneNumber"]) > 11)):
            print(contact["phoneNumber"])
            object_response.append(contact)
    return object_response

def update_contact(resource, bs, commands):    
    data_list = [["Nome", "Telefone", "Telefone Alterado","ID"]]

    for contact_resource in resource:
        if is_number(contact_resource['phoneNumber']):
            phoneNumber = validate(contact_resource['phoneNumber'])
        else:
            phoneNumber = validate(contact_resource['identity'])
        
        if('name' in contact_resource):
            data_list.append([contact_resource['name'], contact_resource['phoneNumber'],phoneNumber['match'], contact_resource['identity']])
        else:
            data_list.append(["Nome não informado", contact_resource['phoneNumber'],phoneNumber['match'], contact_resource['identity']])
        
        contact_resource['phoneNumber'] = phoneNumber['match']
        commands.command_set_contact['resource'] = contact_resource
        updated_contact = bs.process_command(commands.command_set_contact)
        output_file_updated_contacts(data_list)


def main():
    
    key = input("Insira a Key do seu BOT: ")
    commands =  Commands(key)
    bs = BlipSession(commands.bot_key)
    authorization = ''
    while(authorization.lower() !='sim' and authorization.lower()!='não'):
        authorization = input("\nEste script atualizará todos os números de telefone de seus contatos para o formato DDXXXXXXXX. Deseja continuar (sim ou não)? : ")
        if(authorization.lower()=='sim'):
            all_contacts = get_all_contacts(commands,bs)
            contacts_from_whatsapp = get_contacts_from_whatsapp(all_contacts)
            invalid_contacts = contacts_invalid_format(contacts_from_whatsapp)
            if(invalid_contacts):
                update_contact(invalid_contacts, bs, commands)
            else:
                print("\nNenhum contato está no formato inválido")
        elif(authorization.lower()=='não'):
            sys.exit()

if __name__ == "__main__":
    main()

