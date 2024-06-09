from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated ,AllowAny
from rest_framework import status
from .models import Order
from .serializers import OrderSerializer, OrderCreateSerializer , PaymentSerializer
from .views_payment import Kapitalbank
from rest_framework.generics import CreateAPIView , ListAPIView
from rest_framework.authentication import SessionAuthentication
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import xmltodict
from urllib.parse import unquote
from urllib.parse import urlparse, parse_qs
from xml.etree import ElementTree as ET
import urllib.parse

class CreateOrderAndInitiatePaymentView(APIView):
    
    def post(self, request, *args, **kwargs):
        serializer = OrderCreateSerializer(data=request.data)
        if serializer.is_valid():
            order = serializer.save(user=request.user)
            ngrok_url = "https://14fc-188-253-216-12.ngrok-free.app"
            approve_url = f'{ngrok_url}/payment-result/?status=Approved'
            cancel_url =  f'{ngrok_url}/payment-result/?status=Cancelled'
            decline_url =  f'{ngrok_url}/payment-result/?status=Declined'

            # Initiate payment with Kapitalbank and get OrderID
            transaction = Kapitalbank(environment='test')
            # order_id = transaction.get_order_id(amount=order.amount * order.quantity, language='EN', approve_url=approve_url, cancel_url=cancel_url, decline_url=decline_url)
            # session_id = transaction.get_session_id(amount=order.amount * order.quantity, language='EN', approve_url=approve_url, cancel_url=cancel_url, decline_url=decline_url)

            # Initiate payment with Kapitalbank and get order URL
            order_url = transaction.get_order_url(amount=order.amount * order.quantity, language='AZ', approve_url=approve_url, cancel_url=cancel_url, decline_url=decline_url)
            print('Order URL',order_url)
            parsed_url = urlparse(order_url)
            query_params = parse_qs(parsed_url.query)

            order_id = query_params.get('ORDERID', [])[0]
            session_id = query_params.get('SESSIONID', [])[0]
            
            # Update the order instance with OrderID
            order.order_id = order_id
            order.session_id = session_id
            order.save()

            print("Order ID:", order_id)
            print("Session ID:", session_id)
            
            if isinstance(order_url, dict) and "error" in order_url:
                return Response(order_url, status=status.HTTP_400_BAD_REQUEST)

            # order_status = transaction.get_order_status(order_id="789619",session_id="5C414D78B8FCC1A4779E7CEFF07DC7F9")
            
            # print("Order status", order_status)

            # Return the order URL and order ID to the client
            return Response({"order_url": order_url, "order_id": order_id}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@method_decorator(csrf_exempt, name='dispatch')
class PaymentCallbackView(APIView):
    def post(self, request, *args, **kwargs):
        try:

            encoded_data = request.POST.get('xmlmsg', '')
            xml_data = urllib.parse.unquote(encoded_data)
            
            # Print the decoded XML data
            print("Decoded XML:", xml_data)

            # Parse the XML
            root = ET.fromstring(xml_data)

            # Extract specific elements
            order_status_scr = root.findtext('.//OrderStatus')
            session_id = root.findtext('.//SessionID')
            order_id = root.findtext('.//OrderID')

            # Example: Print or process extracted data
            print(f"OrderStatusScr: {order_status_scr}")
            print(f"SessionID: {session_id}")
            print(f"OrderID: {order_id}")
            # Find the order and update its status
            order = Order.objects.get(order_id=order_id)
            order.status = order_status_scr
            order.save()
            # Return a success response if needed
            return Response({"message": "Callback processed successfully"}, status=status.HTTP_200_OK)
            
           
            
        
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)



# class CreateOrderAndInitiatePaymentView(APIView):
#     permission_classes = [IsAuthenticated]
#     authentication_classes = [SessionAuthentication]

#     def post(self, request, *args, **kwargs):
#         serializer = OrderCreateSerializer(data=request.data)
#         if serializer.is_valid():
#             order = serializer.save(user=request.user)

#             approve_url = self.request.build_absolute_uri(reverse('payment_success')) + '?status=Approved'
#             cancel_url =  self.request.build_absolute_uri(reverse('payment_success')) + '?status=Cancelled'
#             decline_url = self.request.build_absolute_uri(reverse('payment_success')) + '?status=Declined'

#             # Initiate payment with Kapitalbank and get OrderID and SessionID
#             transaction = Kapitalbank(environment='test')
#             global order_id
#             global session_id
#             order_id = transaction.get_order_id(amount=order.amount * order.quantity, language='EN', approve_url=approve_url, cancel_url=cancel_url, decline_url=decline_url)
#             session_id = transaction.get_session_id(amount=order.amount * order.quantity, language='EN', approve_url=approve_url, cancel_url=cancel_url, decline_url=decline_url)

#             # Save OrderID and SessionID to the order instance
#             if isinstance(order_id, dict) and "error" in order_id:
#                 return Response(order_id, status=status.HTTP_400_BAD_REQUEST)
            
#             order.order_id = order_id
#             order.session_id = session_id
#             order.save()

#             # Initiate payment with Kapitalbank and get order URL
#             order_url = transaction.get_order_url(amount=order.amount * order.quantity, language='AZ', approve_url=approve_url, cancel_url=cancel_url, decline_url=decline_url)
            
#             if isinstance(order_url, dict) and "error" in order_url:
#                 return Response(order_url, status=status.HTTP_400_BAD_REQUEST)

#             # Return the order URL and order ID to the client
#             return Response({"order_url": order_url, "order_id": order_id}, status=status.HTTP_201_CREATED)
        
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def get(self, request, *args, **kwargs):
#         # Assume you have order_id and session_id from your database or request parameters
       
        
#         # Initialize Kapitalbank integration class
#         transaction = Kapitalbank(environment='test')

#         # Get order status
#         try:
#             order_status = transaction.get_order_status(order_id=order_id, session_id=session_id)
#             return Response({"order_status": order_status})
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
    

# class PaymentResultView(APIView):
#     permission_classes = [AllowAny]  # Allow payment gateway to access this endpoint

    
#     def get(self, request, *args, **kwargs):
      
#         print("-------------------------")
#         print(request.user)
#         result_status = request.query_params.get('OrderStatus')  # Expecting 'Approved', 'Cancelled', or 'Declined'
#         order_id = request.query_params.get('OrderID')
#         print(result_status)
#         order = get_object_or_404(Order, order_id=order_id)
#         print("'''''''''''''''")
#         print(order)
        
#         if result_status == 'Approved':
#             order.status = 'Approved'
#             order.save()
#             return redirect('create_order_and_initiate_payment')  # Replace with your success page
#         elif result_status == 'Cancelled':
#             order.status = 'Cancelled'
#             order.save()
#             return redirect('cancel_page')  # Replace with your cancellation page
#         elif result_status == 'Declined':
#             order.status = 'Declined'
#             order.save()
#             return redirect('decline_page')  # Replace with your decline page
#         else:
#             return Response({'error': 'Invalid status'}, status=400)
        
        
        
        
# @method_decorator(csrf_exempt, name='dispatch')
# class PaymentSuccessView(APIView):
#     permission_classes = []  # Remove authentication

#     def post(self, request, *args, **kwargs):
#         return self.handle_payment_result(request)

#     def handle_payment_result(self, request):
#         result_status = request.GET.get('status') or request.POST.get('status')
#         callback_token = request.GET.get('token') or request.POST.get('token')

#         order = get_object_or_404(Order, callback_token=callback_token)

#         if result_status == 'Approved':
#             order.status = 'Approved'
#             order.save()
#             return redirect('create_order_and_initiate_payment')  # Replace with your success page
#         elif result_status == 'Cancelled':
#             order.status = 'Cancelled'
#             order.save()
#             return redirect('cancel_page')  # Replace with your cancellation page
#         elif result_status == 'Declined':
#             order.status = 'Declined'
#             order.save()
#             return redirect('decline_page')  # Replace with your decline page
#         else:
#             return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

# class PaymentCancelView(APIView):
#     def get(self, request, *args, **kwargs):
#         order_id = request.GET.get('ORDERID')
#         order = get_object_or_404(Order, id=order_id)
#         order.status = 'Cancelled'
#         order.save()
#         return redirect('cancel_page')  # Replace with your cancellation page

# class PaymentDeclineView(APIView):
#     def get(self, request, *args, **kwargs):
#         order_id = request.GET.get('ORDERID')
#         order = get_object_or_404(Order, id=order_id)
#         order.status = 'Declined'
#         order.save()
#         return redirect('decline_page')  # Replace with your decline page
    
    
    
class SaveCardView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = OrderCreateSerializer(data=request.data)
        if serializer.is_valid():
            order = serializer.save(user=request.user)

            # Initiate payment with Kapitalbank and get OrderID
            xml_requester = Kapitalbank(environment='test')
            order_id = xml_requester.get_order_id(amount=order.amount * order.quantity, language='EN')
            
            # Save OrderID to the order instance
            if isinstance(order_id, dict) and "error" in order_id:
                return Response(order_id, status=status.HTTP_400_BAD_REQUEST)
            
            # Update the order instance with OrderID
            order.order_id = order_id
            order.save()

            # Initiate payment with Kapitalbank and get order URL
            order_url = xml_requester.get_order_url_saved_card(amount=order.amount * order.quantity, language='EN')

            if isinstance(order_url, dict) and "error" in order_url:
                return Response(order_url, status=status.HTTP_400_BAD_REQUEST)

            # Return the order URL and order ID to the client
            return Response({"order_url": order_url, "order_id": order.id}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PayWithSavedCardView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = OrderCreateSerializer(data=request.data)
        if serializer.is_valid():
            order = serializer.save(user=request.user)

            # Initiate payment with Kapitalbank and get OrderID
            xml_requester = Kapitalbank(environment='test')
            order_id = xml_requester.get_order_id(amount=order.amount * order.quantity, language='EN')
            
            # Save OrderID to the order instance
            if isinstance(order_id, dict) and "error" in order_id:
                return Response(order_id, status=status.HTTP_400_BAD_REQUEST)
            
            # Update the order instance with OrderID
            order.order_id = order_id
            order.save()

            # Initiate payment with Kapitalbank and get order URL
            order_url = xml_requester.get_order_url_pay_with_saved_card(amount=order.amount * order.quantity, language='EN')

            if isinstance(order_url, dict) and "error" in order_url:
                return Response(order_url, status=status.HTTP_400_BAD_REQUEST)

            # Return the order URL and order ID to the client
            return Response({"order_url": order_url, "order_id": order.id}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)