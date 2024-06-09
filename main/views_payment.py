import requests
import xmltodict
import json
import urllib3
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

CERT_FILE = os.path.join(BASE_DIR, 'certificates', 'testmerchant_06.crt')
KEY_FILE = os.path.join(BASE_DIR, 'certificates', 'merchant_name.key')

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Kapitalbank:
    def __init__(self, environment='test'):
        self.url = "https://tstpg.kapitalbank.az:5443/Exec" if environment == 'test' else "https://3dsrv.kapitalbank.az:5443/Exec"
        self.cert_file = CERT_FILE
        self.key_file = KEY_FILE
        self.headers = {"Content-Type": "application/xml; charset=utf-8"}

    def send_request(self, amount, language, approve_url, cancel_url, decline_url):
        data = f'''<?xml version="1.0" encoding="UTF-8"?>
                    <TKKPG>
                        <Request>
                            <Operation>CreateOrder</Operation>
                            <Language>{language}</Language>
                            <Order>
                                <OrderType>Purchase</OrderType>
                                <Merchant>E1000010</Merchant>
                                <Amount>{int(float(amount) * 100)}</Amount>
                                <Currency>944</Currency>
                                <Description>xxxxxxxx</Description>
                                <ApproveURL>{approve_url}</ApproveURL>
                                <CancelURL>{cancel_url}</CancelURL>
                                <DeclineURL>{decline_url}</DeclineURL>
                            </Order>
                        </Request>
                    </TKKPG>'''
        response = requests.post(
            self.url,
            data=data,
            headers=self.headers,
            cert=(self.cert_file, self.key_file),
            verify=False  # Disable SSL verification; replace with proper SSL handling for production
        )

        response.raise_for_status()  # Raise an exception for HTTP errors

        if response.status_code == 200:
            return self.xml_to_json(response.text)
        else:
            return {"error": f"HTTP Error {response.status_code}"}

    @staticmethod
    def xml_to_json(xml_string):
        try:
            xml_dict = xmltodict.parse(xml_string)
            return json.loads(json.dumps(xml_dict, indent=2))  # Convert XML to JSON format
        except Exception as e:
            return {"error": str(e)}

    def get_order_url(self, amount, language, approve_url, cancel_url, decline_url):
        response = self.send_request(amount, language, approve_url, cancel_url, decline_url)

        if isinstance(response, dict):
            order = response.get("TKKPG", {}).get("Response", {}).get("Order", {})
            OrderID = response.get("TKKPG", {}).get("Response", {}).get("Order", {}).get("OrderID", {})
            SessionID = response.get("TKKPG", {}).get("Response", {}).get("Order", {}).get("SessionID", {})

            if "URL" in order:
                return order["URL"] + '?' + 'ORDERID=' + OrderID + '&SESSIONID=' + SessionID
            else:
                return {"error": "URL not found in response"}
        else:
            return {"error": "Invalid response format"}


    # ____________ SEHV ISLEYIR ______________
    
    # def get_order_id(self, amount, language, approve_url, cancel_url, decline_url):
    #     response = self.send_request(amount, language, approve_url, cancel_url, decline_url)
    #     if isinstance(response, dict):
    #         OrderID = response.get("TKKPG", {}).get("Response", {}).get("Order", {}).get("OrderID", {})
    #         return OrderID
        
    # def get_session_id(self, amount, language, approve_url, cancel_url, decline_url):
    #     response = self.send_request(amount, language, approve_url, cancel_url, decline_url)
    #     if isinstance(response, dict):
    #         SessionID = response.get("TKKPG", {}).get("Response", {}).get("Order", {}).get("SessionID", {})
    #         return SessionID

    # def get_order_status(self, order_id, session_id, language='AZ'):
        
    #     xml_request = f'''<?xml version="1.0" encoding="UTF-8"?>
    #     <TKKPG>
    #         <Request>
    #             <Operation>GetOrderStatus</Operation>
    #             <Language>{language}</Language>
    #             <Order>
    #                 <Merchant>E1000010</Merchant>
    #                 <OrderID>{order_id}</OrderID>
    #             </Order>
    #             <SessionID>{session_id}</SessionID>
    #         </Request>
    #     </TKKPG>'''

    #     response = requests.post(
    #         self.url,
    #         data=xml_request,
    #         headers=self.headers,
    #         cert=(self.cert_file, self.key_file),
    #         verify=False  # Disable SSL verification; replace with proper SSL handling for production
    #     )

    #     response.raise_for_status()  # Raise an exception for HTTP errors

    #     if response.status_code == 200:
    #         response_data = self.xml_to_json(response.text)
    #         print(response_data)
    #         order_status = response_data.get("TKKPG", {}).get("Response", {}).get("Order", {}).get("OrderStatus", {})
    #         return order_status
    #     else:
    #         return {"error": f"HTTP Error {response.status_code}"}















"""import requests
import xmltodict
import json
import urllib3
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

CERT_FILE = os.path.join(BASE_DIR, 'certificates', 'testmerchant_06.crt')
KEY_FILE = os.path.join(BASE_DIR, 'certificates', 'merchant_name.key')

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Kapitalbank:
    def __init__(self, environment='test'):
        self.url = "https://tstpg.kapitalbank.az:5443/Exec" if environment == 'test' else "https://3dsrv.kapitalbank.az:5443/Exec"
        self.cert_file = CERT_FILE
        self.key_file = KEY_FILE
        self.headers = {"Content-Type": "text/html; charset=utf-8"}
        

    def send_request(self, amount, language,url):
        response = requests.post(
            self.url,
                data=f'''<?xml version="1.0" encoding="UTF-8"?>
                            <TKKPG>
                                <Request>
                                    <Operation>CreateOrder</Operation>
                                    <Language>{language}</Language>
                                    <Order>
                                        <OrderType>Purchase</OrderType>
                                        <Merchant>E1000010</Merchant>
                                        <Amount>{int(float(amount) * 100)}</Amount>
                                        <Currency>944</Currency>
                                        <Description>xxxxxxxx</Description>
                                        <ApproveURL>{url}</ApproveURL>
                                        <CancelURL>/testshopPageReturn.jsp</CancelURL>
                                        <DeclineURL>/testshopPageReturn.jsp</DeclineURL>
                                    </Order>
                                </Request>
                            </TKKPG>''',
            headers=self.headers,
            cert=(self.cert_file, self.key_file),
            verify=False  # Disable SSL verification; replace with proper SSL handling for production
        )

        response.raise_for_status()  # Raise an exception for HTTP errors

        if response.status_code == 200:
            return self.xml_to_json(response.text)
        else:
            return {"error": f"HTTP Error {response.status_code}"}
        
 
        
    def save_card(self,amount,language):
        response = requests.post(
            self.url,
            data=f'''<?xml version="1.0" encoding="utf-8"?>
                    <TKKPG>
                    <Request>
                        <Operation>CreateOrder</Operation>
                        <Language>{language}</Language>
                        <Order>
                        <OrderType>Purchase</OrderType>
                        <Merchant>E1000010</Merchant>
                        <Amount>{int(float(amount) * 100)}</Amount>
                        <Currency>944</Currency>
                        <Description>x</Description>
                        <ApproveURL>app.com</ApproveURL>
                        <CancelURL>can.com</CancelURL>
                        <DeclineURL>dec.com</DeclineURL>
                        <CardRegistration>
                            <RegisterCardOnSuccess>true</RegisterCardOnSuccess>
                            <CheckRegisterCardOn>true</CheckRegisterCardOn>
                            <SaveCardUIDToOrder>true</SaveCardUIDToOrder>
                        </CardRegistration>
                        <AddParams>
                            <CustomFields>
                            <Param name="Attention" title="By clicking Register card I agree to save the token of my bank card for further convenience of payments." />
                        </CustomFields>
                        </AddParams>
                        </Order>
                    </Request>
                    </TKKPG>''',
            headers=self.headers,
            cert=(self.cert_file, self.key_file),
            verify=False  # Disable SSL verification; replace with proper SSL handling for production
        )

        response.raise_for_status()  # Raise an exception for HTTP errors

        if response.status_code == 200:
            return self.xml_to_json(response.text)
        else:
            return {"error": f"HTTP Error {response.status_code}"}
        
    def pay_with_saved_card(self,amount,language):
        response = requests.post(
            self.url,
            data=f'''<?xml version="1.0" encoding="utf-8"?>
                          <TKKPG>
                        <Request>
                            <Operation>CreateOrder</Operation>
                            <Language>{language}</Language>
                            <Order>
                            <OrderType>Purchase</OrderType>
                            <Merchant>E1000010</Merchant>
                            <Amount>{int(float(amount) * 100)}</Amount>
                            <Currency>944</Currency>
                            <Description>xxxxxxxx</Description>
                            <ApproveURL>app.com</ApproveURL>
                            <CancelURL>can.com</CancelURL>
                            <DeclineURL>dec.com</DeclineURL>
                            <AddParams> 
                                <SenderCardUID></SenderCardUID>
                            </AddParams>
                            </Order>
                        </Request>
                        </TKKPG>''',
            headers=self.headers,
            cert=(self.cert_file, self.key_file),
            verify=False  # Disable SSL verification; replace with proper SSL handling for production
        )

        response.raise_for_status()  # Raise an exception for HTTP errors

        if response.status_code == 200:
            return self.xml_to_json(response.text)
        else:
            return {"error": f"HTTP Error {response.status_code}"}

    @staticmethod
    def xml_to_json(xml_string):
        try:
            xml_dict = xmltodict.parse(xml_string)
            return json.loads(json.dumps(xml_dict,indent=2))  # Convert XML to JSON format
        except Exception as e:
            return {"error": str(e)}

    def get_order_url(self, amount, language,url):
        response = self.send_request(amount, language,url)
        

        if isinstance(response, dict):
            order = response.get("TKKPG", {}).get("Response", {}).get("Order", {})
            OrderID = response.get("TKKPG", {}).get("Response", {}).get("Order", {}).get("OrderID", {})
            SessionID = response.get("TKKPG", {}).get("Response", {}).get("Order", {}).get("SessionID", {})

            if "URL" in order:
                return order["URL"] + '?' + 'ORDERID=' + OrderID + '&SESSIONID=' + SessionID
            else:
                return {"error": "URL not found in response"}
        else:
            return {"error": "Invalid response format"}
        
    def get_order_url_saved_card(self, amount, language):
        response = self.save_card(amount, language)
       

        if isinstance(response, dict):
            order = response.get("TKKPG", {}).get("Response", {}).get("Order", {})
            OrderID = response.get("TKKPG", {}).get("Response", {}).get("Order", {}).get("OrderID", {})
            SessionID = response.get("TKKPG", {}).get("Response", {}).get("Order", {}).get("SessionID", {})

            if "URL" in order:
                return order["URL"] + '?' + 'ORDERID=' + OrderID + '&SESSIONID=' + SessionID
            else:
                return {"error": "URL not found in response"}
        else:
            return {"error": "Invalid response format"}
        
    def get_order_url_pay_with_saved_card(self, amount, language):
        response = self.pay_with_saved_card(amount, language)
       

        if isinstance(response, dict):
            order = response.get("TKKPG", {}).get("Response", {}).get("Order", {})
            OrderID = response.get("TKKPG", {}).get("Response", {}).get("Order", {}).get("OrderID", {})
            SessionID = response.get("TKKPG", {}).get("Response", {}).get("Order", {}).get("SessionID", {})

            if "URL" in order:
                return order["URL"] + '?' + 'ORDERID=' + OrderID + '&SESSIONID=' + SessionID
            else:
                return {"error": "URL not found in response"}
        else:
            return {"error": "Invalid response format"}
        
    def get_order_id(self,amount,language,url):
        response = self.send_request(amount,language,url)
        if isinstance(response, dict):

            OrderID = response.get("TKKPG", {}).get("Response", {}).get("Order", {}).get("OrderID", {})

            return OrderID
    
        """
        
        
        
