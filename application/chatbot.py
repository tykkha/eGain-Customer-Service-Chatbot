from questions import trackingQuestions, packageStatus
from datetime import datetime, timedelta
import random

class PackageTracker:
    def __init__(self):
        self.questions = trackingQuestions
        self.currQuestionIDX = 0
        self.collectedData = {}
        self.packageInfo = None
    
    def display_question(self):
        if self.currQuestionIDX >= len(self.questions):
            # All initial questions answered, look up package
            self.packageInfo = self.lookup_package_status()
            if self.packageInfo:
                return self.display_action_menu()
            else:
                print("\nPackage not found. Please verify your order number and email.")
                print("Would you like to:")
                print("  1. Try again")
                print("  2. Speak to a representative")
                print("  3. Track another package")
                return None
        
        question = self.questions[self.currQuestionIDX]
        print(f"\n{question['prompt']}")
        
        if question['type'] == 'choice':
            for i, option in enumerate(question['options'], 1):
                print(f"  {i}. {option}")
            print(f"  5. Speak to a representative")
            print(f"  6. Track another package")
        
        return question
    
    def display_action_menu(self):
        # Check if packageInfo exists
        if self.packageInfo is None:
            print("\nUnable to retrieve package information.")
            print("Please speak to a representative for assistance.")
            return None
        
        status = self.packageInfo['status']
        
        # Get options for this status, default to empty list if status not found
        if status in packageStatus:
            options = packageStatus[status]
        else:
            options = []
        
        if not options:
            print(f"\nPackage Status: {status.replace('_', ' ').title()}")
            print("Please speak to a representative for assistance.")
            return None
        
        print(f"\nPackage Status: {status.replace('_', ' ').title()}")
        
        lastLocation = self.packageInfo.get('lastLocation', 'Unknown')
        print(f"Last Location: {lastLocation}")
        
        # Show shipping type if available
        shippingType = self.packageInfo.get('shippingType', 'standard')
        print(f"Shipping Type: {shippingType.replace('_', ' ').title()}")
        
        print(f"\nWhat would you like to do?")
        
        for i, option in enumerate(options, 1):
            print(f"  {i}. {option}")
        print(f"  {len(options) + 1}. Speak to a representative")
        print(f"  {len(options) + 2}. Track another package")
        
        return {'type': 'choice', 'options': options, 'key': 'action'}
    
    def handle_response(self, question, userInput):
        # Check for 'representative' request
        if (question['type'] == 'choice' and userInput == '5') or \
           (question['type'] == 'text' and userInput == '0'):
            return True, "Transferring you to a representative..."
        
        # Check for 'track another package' request
        if (question['type'] == 'choice' and userInput == '6') or \
           (question['type'] == 'text' and userInput == '9'):
            return 'TRACK_ANOTHER', "Switching to track another package..."
        
        if question['type'] == 'choice':
            try:
                choice = int(userInput)
                if 1 <= choice <= len(question['options']):
                    selected_option = question['options'][choice - 1]
                    self.collectedData[question['key']] = selected_option
                    self.currQuestionIDX += 1
                    return False, None
                else:
                    return False, "Invalid choice. Please select a valid number."
            except ValueError:
                return False, "Please enter a number."
        
        elif question['type'] == 'text':
            if 'validator' in question:
                isValid, errorMessage = getattr(self, question['validator'])(userInput)
                if not isValid:
                    return False, errorMessage
            
            self.collectedData[question['key']] = userInput.strip()
            self.currQuestionIDX += 1
            return False, None
        
        return False, "Unknown question type."
    
    def validateOrderNum(self, value):
        value = value.strip()
        if len(value) > 50:  # Add maximum length
            return False, "Order number is too long. Please enter a valid order number."
        if len(value) < 4:
            return False, "Order numbers must be at least 4 characters. Please try again."
        if not value.isalnum():
            return False, "Order numbers contain only letters and numbers. Please try again."
        return True, None

    def validateEmail(self, value):
        value = value.strip()
        if len(value) > 254:  # RFC 5321 maximum email length
            return False, "Email address is too long. Please try again."
        if '@' not in value or '.' not in value:
            return False, "Please enter a valid email address."
        return True, None
    
    def lookup_package_status(self):
        # This is where a database lookup would occur in production
        order_num = self.collectedData.get('order_number', '')
        email = self.collectedData.get('email', '')
        
        # Demo package data for testing purposes
        demo_packages = {
            'D123': {
                'status': 'in_transit',
                'lastLocation': 'Distribution Center - Chicago, IL',
                'estDelivery': '2026-02-08',
                'originalEstDelivery': '2026-02-08',
                'shippingType': 'standard',
                'lastUpdate': '2026-02-06',
                'trackingEvents': [
                    {'date': '2026-02-05', 'location': 'Origin Facility', 'event': 'Picked up'},
                    {'date': '2026-02-06', 'location': 'Chicago, IL', 'event': 'In transit'}
                ]
            },
            'D456': {
                'status': 'delayed',
                'lastLocation': 'Memphis, TN Hub',
                'estDelivery': '2026-02-10',
                'originalEstDelivery': '2026-02-07',
                'shippingType': 'priority',
                'lastUpdate': '2026-02-05',
                'trackingEvents': [
                    {'date': '2026-02-04', 'location': 'Origin Facility', 'event': 'Picked up'},
                    {'date': '2026-02-05', 'location': 'Memphis, TN', 'event': 'Delayed - Weather'},
                ]
            },
            'D789': {
                'status': 'delivered',
                'lastLocation': 'Customer Address',
                'estDelivery': '2026-02-05',
                'originalEstDelivery': '2026-02-05',
                'shippingType': 'standard',
                'lastUpdate': '2026-02-05',
                'trackingEvents': [
                    {'date': '2026-02-03', 'location': 'Origin Facility', 'event': 'Picked up'},
                    {'date': '2026-02-04', 'location': 'Local Facility', 'event': 'Out for delivery'},
                    {'date': '2026-02-05', 'location': 'Customer Address', 'event': 'Delivered - Left at front door'}
                ]
            },
            'D999': {
                'status': 'out_for_delivery',
                'lastLocation': 'Local Delivery Facility',
                'estDelivery': '2026-02-06',
                'originalEstDelivery': '2026-02-06',
                'shippingType': 'standard',
                'lastUpdate': '2026-02-06',
                'trackingEvents': [
                    {'date': '2026-02-04', 'location': 'Origin Facility', 'event': 'Picked up'},
                    {'date': '2026-02-05', 'location': 'Regional Hub', 'event': 'Arrived at hub'},
                    {'date': '2026-02-06', 'location': 'Local Facility', 'event': 'Out for delivery'}
                ]
            },
            'D111': {
                'status': 'not_shipped',
                'lastLocation': 'Warehouse - Processing',
                'estDelivery': '2026-02-10',
                'originalEstDelivery': '2026-02-10',
                'shippingType': 'standard',
                'lastUpdate': '2026-02-07',
                'trackingEvents': [
                    {'date': '2026-02-07', 'location': 'Warehouse', 'event': 'Order received'},
                    {'date': '2026-02-07', 'location': 'Warehouse', 'event': 'Processing'}
                ]
            },
            'D222': {
                'status': 'not_shipped',
                'lastLocation': 'Warehouse - Ready to ship',
                'estDelivery': '2026-02-09',
                'originalEstDelivery': '2026-02-09',
                'shippingType': 'priority',
                'lastUpdate': '2026-02-07',
                'trackingEvents': [
                    {'date': '2026-02-06', 'location': 'Warehouse', 'event': 'Order received'},
                    {'date': '2026-02-07', 'location': 'Warehouse', 'event': 'Ready to ship'}
                ]
            },
            'D555': {
                'status': 'delayed',
                'lastLocation': 'Distribution Center - Atlanta, GA',
                'estDelivery': '2026-02-08',
                'originalEstDelivery': '2026-02-08',
                'shippingType': 'standard',
                'lastUpdate': '2026-02-01',  # No updates in 6 days
                'trackingEvents': [
                    {'date': '2026-01-30', 'location': 'Origin Facility', 'event': 'Picked up'},
                    {'date': '2026-02-01', 'location': 'Atlanta, GA', 'event': 'In transit'}
                ]
            }
        }
        
        order_upper = order_num.strip().upper()
        
        if order_upper in demo_packages:
            return demo_packages[order_upper]
        
        # In production, you'd query your database here and return None if not found
        return {
            'status': 'in_transit',
            'lastLocation': 'Distribution Center - Chicago, IL',
            'estDelivery': '2026-02-08',
            'originalEstDelivery': '2026-02-08',
            'shippingType': 'standard',
            'lastUpdate': '2026-02-06',
            'trackingEvents': [
                {'date': '2026-02-05', 'location': 'Origin Facility', 'event': 'Picked up'},
                {'date': '2026-02-06', 'location': 'Chicago, IL', 'event': 'In transit'}
            ]
        }
    
    def handle_action(self, action):
        if self.packageInfo is None:
            return "Unable to process action. Package information not available."
        
        if action == "View current location and tracking history":
            return self.show_tracking_history()
        
        elif action == "Check estimated delivery date":
            estDelivery = self.packageInfo.get('estDelivery', 'Unknown')
            return f"\nEstimated delivery: {estDelivery}"
        
        elif action == "Update delivery instructions":
            return self.update_delivery_instructions()
        
        elif action == "Redirect to different address (if available)":
            return self.redirect_package()
        
        elif action == "Check where package was left":
            return self.check_delivery_location()
        
        elif action == "Report package as not received":
            return self.report_not_received()
        
        elif action == "File a damage claim":
            return self.file_damage_claim()
        
        elif action == "Get updated delivery estimate":
            return self.get_updated_estimate()
        
        elif action == "See estimated delivery window":
            return self.show_delivery_window()
        
        elif action == "Arrange to pick up at facility instead":
            return self.arrange_pickup()
        
        elif action == "Cancel order (not yet shipped)":
            return self.cancel_order_not_shipped()
        
        elif action == "Request priority shipping refund":
            return self.refund_priority_shipping()
        
        elif action == "Reorder package (no recent updates)":
            return self.reorder_stalled_package()
        
        return "Action completed."
    
    def show_tracking_history(self):
        # Error handling 
        if self.packageInfo is None:
            return "Unable to retrieve tracking history."
        
        result = f"\n{'='*50}\n"
        result += f"Current Status: {self.packageInfo['status'].replace('_', ' ').title()}\n"
        result += f"Last Known Location: {self.packageInfo.get('lastLocation', 'Unknown')}\n"
        result += f"Shipping Type: {self.packageInfo.get('shippingType', 'standard').replace('_', ' ').title()}\n"
        result += f"Estimated Delivery: {self.packageInfo.get('estDelivery', 'Unknown')}\n"
        result += f"Last Update: {self.packageInfo.get('lastUpdate', 'Unknown')}\n\n"
        result += "Tracking History:\n"
        result += f"{'-'*50}\n"
        
        trackingEvents = self.packageInfo.get('trackingEvents', [])
        for event in trackingEvents:
            result += f"{event['date']} | {event['location']}\n"
            result += f"  → {event['event']}\n"
        result += f"{'='*50}\n"
        return result
    
    def update_delivery_instructions(self):
        while True:
            print("\nDelivery Instructions:")
            print("  1. Leave at front door")
            print("  2. Leave at back door")
            print("  3. Require signature")
            print("  4. Leave with neighbor")
            print("  5. Hold at facility for pickup")
            
            choice = input("\nSelect option (or 0 for representative): ").strip()
            if choice == '0':
                return "Transferring to representative..."
            
            instructions = {
                '1': 'front door',
                '2': 'back door',
                '3': 'signature required',
                '4': 'neighbor',
                '5': 'facility pickup'
            }
            
            if choice in instructions:
                return f"\nDelivery instructions updated to: {instructions[choice]}\nConfirmation sent to your email!"
            else:
                print("Invalid option. Please try again.")
    
    def redirect_package(self):
        while True:
            print("\nEnter new delivery address:")
            new_address = input("Address: ").strip()
            if new_address:
                return f"\nPackage redirected to: {new_address}\nYou'll receive a confirmation email shortly."
            else:
                print("Address cannot be empty. Please try again.")
    
    def report_not_received(self):
        print("\nLet's check a few things first:")
        print("  - Have you checked with neighbors?")
        print("  - Checked all entrances to your home?")
        print("  - Verified the delivery address on your order?")
        
        while True:
            confirm = input("\nStill haven't found it? (yes/no): ").strip().lower()
            if confirm == 'yes':
                return "\nClaim filed. We'll investigate and email you within 24-48 hours.\nReference: NR123456"
            elif confirm == 'no':
                return "\nGlad we could help! Let us know if you need anything else."
            else:
                print("Invalid input. Please enter 'yes' or 'no'.")
    
    def file_damage_claim(self):
        return "\nDamage claim initiated.\nReference: DC123456\n\nNext steps:\n  1. Keep all packaging materials\n  2. Take photos of damage\n  3. Reply to confirmation email with photos\n\nYou'll hear back within 2 business days."
    
    def get_updated_estimate(self):
        return "\nUpdated delivery estimate: February 10, 2026\nWe apologize for the delay."
    
    def check_delivery_location(self):
        return "\nPackage was delivered to: Front door\nDelivered on: 2026-02-05 at 3:42 PM"
    
    def show_delivery_window(self):
        return "\nEstimated delivery window today: 1:00 PM - 5:00 PM\nYou'll receive a notification when the driver is nearby."
    
    def arrange_pickup(self):
        while True:
            print("\nNearest pickup locations:")
            print("  1. Main Distribution Center - 123 Main St (5 miles)")
            print("  2. Local Post Office - 456 Oak Ave (2 miles)")
            
            choice = input("\nSelect location (or 0 to cancel): ").strip()
            if choice == '1':
                return "\nPickup arranged at Main Distribution Center.\nAvailable for pickup after 5:00 PM today.\nBring photo ID."
            elif choice == '2':
                return "\nPickup arranged at Local Post Office.\nAvailable for pickup after 4:00 PM today.\nBring photo ID."
            elif choice == '0':
                return "\nPickup arrangement cancelled."
            else:
                print("Invalid choice. Please enter 1, 2, or 0.")
    
    def cancel_order_not_shipped(self):
        # Safety check
        if self.packageInfo is None:
            return "Unable to process cancellation. Package information not available."
        
        print("\n" + "="*50)
        print("CANCEL ORDER")
        print("="*50)
        print("\nYour order has not shipped yet and can be cancelled.")
        print(f"Order Number: {self.collectedData.get('order_number', 'Unknown')}")
        print(f"Current Status: {self.packageInfo['status'].replace('_', ' ').title()}")
        
        while True:
            confirm = input("\nAre you sure you want to cancel this order? (yes/no): ").strip().lower()
            if confirm == 'yes':
                # Generate cancellation reference
                cancel_ref = f"CN{random.randint(100000, 999999)}"
                result = "\n" + "="*50 + "\n"
                result += "ORDER CANCELLED SUCCESSFULLY\n"
                result += "="*50 + "\n"
                result += f"Cancellation Reference: {cancel_ref}\n"
                result += "Refund will be processed within 3-5 business days.\n"
                result += "You will receive a confirmation email shortly.\n"
                result += "="*50
                return result
            elif confirm == 'no':
                return "\nCancellation aborted. Your order will continue processing."
            else:
                print("Invalid input. Please enter 'yes' or 'no'.")
    
    def refund_priority_shipping(self):
        # Safety check
        if self.packageInfo is None:
            return "Unable to process refund. Package information not available."
        
        print("\n" + "="*50)
        print("PRIORITY SHIPPING REFUND REQUEST")
        print("="*50)
        
        # Check if this is priority shipping
        shipping_type = self.packageInfo.get('shippingType', 'standard')
        if shipping_type != 'priority':
            return "\nThis order does not have priority shipping.\nNo refund is applicable."
        
        # Calculate delay
        original_est = self.packageInfo.get('originalEstDelivery', '')
        current_est = self.packageInfo.get('estDelivery', '')
        
        print(f"\nShipping Type: Priority")
        print(f"Original Estimated Delivery: {original_est}")
        print(f"Current Estimated Delivery: {current_est}")
        
        # Parse dates to calculate delay (simplified for demo)
        try:
            orig_date = datetime.strptime(original_est, '%Y-%m-%d')
            curr_date = datetime.strptime(current_est, '%Y-%m-%d')
            delay_days = (curr_date - orig_date).days
            
            print(f"Delay: {delay_days} days")
            
            if delay_days >= 3:
                refund_ref = f"RF{random.randint(100000, 999999)}"
                result = "\n" + "="*50 + "\n"
                result += "PRIORITY SHIPPING REFUND APPROVED\n"
                result += "="*50 + "\n"
                result += f"Refund Reference: {refund_ref}\n"
                result += f"Refund Amount: $15.99 (Priority Shipping Cost)\n"
                result += "Refund will be processed within 3-5 business days.\n"
                result += "You will receive a confirmation email shortly.\n"
                result += "="*50
                return result
            else:
                return f"\nDelay is only {delay_days} days. Priority shipping refund requires a delay of 3 or more days.\nPlease check back if the delay exceeds 3 days."
        except:
            return "\nUnable to calculate delay. Please contact customer service."
    
    def reorder_stalled_package(self):
        # Safety check
        if self.packageInfo is None:
            return "Unable to process reorder. Package information not available."
        
        print("\n" + "="*50)
        print("REORDER STALLED PACKAGE")
        print("="*50)
        
        # Check days since last update
        last_update = self.packageInfo.get('lastUpdate', '')
        print(f"\nLast Tracking Update: {last_update}")
        
        # Calculate days since last update (simplified for demo)
        try:
            last_update_date = datetime.strptime(last_update, '%Y-%m-%d')
            current_date = datetime.strptime('2026-02-07', '%Y-%m-%d')  # Demo current date
            days_stalled = (current_date - last_update_date).days
            
            print(f"Days Without Update: {days_stalled}")
            
            if days_stalled >= 5:
                print("\nYour package appears to be stalled in transit.")
                print("We can cancel the current order and create a new one.")
                
                while True:
                    confirm = input("\nWould you like to reorder? (yes/no): ").strip().lower()
                    if confirm == 'yes':
                        # Generate new order details
                        new_order_num = f"D{random.randint(100, 999)}"
                        new_delivery_date = (current_date + timedelta(days=random.randint(3, 7))).strftime('%Y-%m-%d')
                        cancel_ref = f"CN{random.randint(100000, 999999)}"
                        
                        result = "\n" + "="*50 + "\n"
                        result += "REORDER SUCCESSFUL\n"
                        result += "="*50 + "\n"
                        result += f"Original Order Cancelled: {self.collectedData.get('order_number', 'Unknown')}\n"
                        result += f"Cancellation Reference: {cancel_ref}\n\n"
                        result += f"New Order Number: {new_order_num}\n"
                        result += f"New Estimated Delivery: {new_delivery_date}\n"
                        result += f"Shipping Type: {self.packageInfo.get('shippingType', 'standard').title()}\n\n"
                        result += "Your new order is being processed and will ship soon.\n"
                        result += "You will receive tracking updates via email.\n"
                        result += "="*50
                        return result
                    elif confirm == 'no':
                        return "\nReorder cancelled. Your original order remains active."
                    else:
                        print("Invalid input. Please enter 'yes' or 'no'.")
            else:
                return f"\nPackage last updated {days_stalled} days ago.\nReorder option is available after 5 days without updates.\nPlease check back later if no updates occur."
        except:
            return "\nUnable to determine update history. Please contact customer service."

def run_chatbot():
    try: 
        print("\n" + "="*60)
        print("PACKAGE TRACKING DEMO CHATBOT")
        print("="*60)
        print("\nDemo tracking numbers you can use:")
        print("  • D123 - In transit package")
        print("  • D456 - Delayed package (priority shipping)")
        print("  • D789 - Delivered package")
        print("  • D999 - Out for delivery")
        print("  • D111 - Not shipped (processing)")
        print("  • D222 - Not shipped (ready to ship, priority)")
        print("  • D555 - Stalled package (no updates in 6 days)")
        print("  • Any other - Generic in-transit package")
        print("\nEmail can be anything valid (e.g., test@email.com)")
        print("(Enter 0 to speak to a representative)")
        print("(Enter 9 to track another package)")
        print("="*60)
        
        bot = PackageTracker()
        
        # Initial questions loop
        while bot.currQuestionIDX < len(bot.questions):
            question = bot.display_question()
            
            if question is None:
                # Package not found case
                while True:
                    choice = input("\nYour choice: ").strip()
                    if choice == '1':
                        bot = PackageTracker()
                        break
                    elif choice == '2':
                        print("Transferring to representative...")
                        return
                    elif choice == '3':
                        # Confirm before tracking another package
                        while True:
                            confirm = input("\nAre you sure you want to track another package? This will cancel the current chat. (yes/no): ").strip().lower()
                            if confirm == 'yes':
                                run_chatbot()
                                return
                            elif confirm == 'no':
                                break
                            else:
                                print("Invalid input. Please enter 'yes' or 'no'.")
                    else:
                        print("Invalid choice. Please enter 1, 2, or 3.")
            
            userInput = input("\nYour response: ").strip()
            
            is_transfer, message = bot.handle_response(question, userInput)
            
            if message:
                print(message)
            
            if is_transfer == True:
                return
            elif is_transfer == 'TRACK_ANOTHER':
                # Confirm before tracking another package
                while True:
                    confirm = input("\nAre you sure you want to track another package? This will cancel the current chat. (yes/no): ").strip().lower()
                    if confirm == 'yes':
                        run_chatbot()
                        return
                    elif confirm == 'no':
                        break
                    else:
                        print("Invalid input. Please enter 'yes' or 'no'.")
        
        # All questions answered - now look up package and show action menu
        action_question = bot.display_question()
        
        if action_question is None:
            # No actions available or package not found
            while True:
                choice = input("\nYour choice: ").strip()
                if choice == '1':
                    run_chatbot()
                    return
                elif choice == '2':
                    print("Transferring to representative...")
                    return
                elif choice == '3':
                    # Confirm before tracking another package
                    while True:
                        confirm = input("\nAre you sure you want to track another package? This will cancel the current chat. (yes/no): ").strip().lower()
                        if confirm == 'yes':
                            run_chatbot()
                            return
                        elif confirm == 'no':
                            break
                        else:
                            print("Invalid input. Please enter 'yes' or 'no'.")
                else:
                    print("Invalid choice. Please enter 1, 2, or 3.")
        
        # Main action menu loop
        while True:
            userInput = input("\nYour choice: ").strip()
            
            try:
                choice = int(userInput)
                
                # Check for "Speak to representative" option
                if choice == len(action_question['options']) + 1:
                    print("Transferring to representative...")
                    break
                
                # Check for "Track another package" option
                elif choice == len(action_question['options']) + 2:
                    while True:
                        confirm = input("\nAre you sure you want to track another package? This will cancel the current chat. (yes/no): ").strip().lower()
                        if confirm == 'yes':
                            run_chatbot()
                            return
                        elif confirm == 'no':
                            bot.display_action_menu()
                            break
                        else:
                            print("Invalid input. Please enter 'yes' or 'no'.")
                
                # Valid action choice
                elif 1 <= choice <= len(action_question['options']):
                    selected_action = action_question['options'][choice - 1]
                    result = bot.handle_action(selected_action)
                    print(result)
                    
                    # Ask if they need anything else with validation loop
                    while True:
                        another = input("\nNeed help with anything else? (yes/no): ").strip().lower()
                        if another == 'yes':
                            bot.display_action_menu()
                            break
                        elif another == 'no':
                            print("\nThank you for using our package tracking service!")
                            return
                        else:
                            print("Invalid input. Please enter 'yes' or 'no'.")
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Please enter a number.")
    except KeyboardInterrupt:
        print("\n\nSession interrupted. Thank you for using our package tracking service!")
        return
    except Exception as e:
        print("\n\nAn unexpected error occurred. Please try again or contact customer support.")
        print("If the problem persists, please speak to a representative.")
        return

if __name__ == "__main__":
    try:
        run_chatbot()
    except KeyboardInterrupt:
        print("\n\nGoodbye!")