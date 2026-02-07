from questions import trackingQuestions, packageStatus

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
                return None
        
        question = self.questions[self.currQuestionIDX]
        print(f"\n{question['prompt']}")
        
        if question['type'] == 'choice':
            for i, option in enumerate(question['options'], 1):
                print(f"  {i}. {option}")
            print(f"  5. Speak to a representative")
        elif question['type'] == 'text':
            print("  (or enter 0 to speak to a representative)")
        
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
        print(f"\nWhat would you like to do?")
        
        for i, option in enumerate(options, 1):
            print(f"  {i}. {option}")
        print(f"  {len(options) + 1}. Speak to a representative")
        
        return {'type': 'choice', 'options': options, 'key': 'action'}
    
    def handle_response(self, question, userInput):
        # Check for 'representative' request
        if (question['type'] == 'choice' and userInput == '5') or \
           (question['type'] == 'text' and userInput == '0'):
            return True, "Transferring you to a representative..."
        
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
        if len(value) < 4:
            return False, "Order numbers must be at least 4 characters. Please try again."
        if not value.isalnum():
            return False, "Order numbers contain only letters and numbers. Please try again."
        return True, None
    
    def validateEmail(self, value):
        value = value.strip()
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
                'trackingEvents': [
                    {'date': '2026-02-05', 'location': 'Origin Facility', 'event': 'Picked up'},
                    {'date': '2026-02-06', 'location': 'Chicago, IL', 'event': 'In transit'}
                ]
            },
            'D456': {
                'status': 'delayed',
                'lastLocation': 'Memphis, TN Hub',
                'estDelivery': '2026-02-10',
                'trackingEvents': [
                    {'date': '2026-02-04', 'location': 'Origin Facility', 'event': 'Picked up'},
                    {'date': '2026-02-05', 'location': 'Memphis, TN', 'event': 'Delayed - Weather'},
                ]
            },
            'D789': {
                'status': 'delivered',
                'lastLocation': 'Customer Address',
                'estDelivery': '2026-02-05',
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
                'trackingEvents': [
                    {'date': '2026-02-04', 'location': 'Origin Facility', 'event': 'Picked up'},
                    {'date': '2026-02-05', 'location': 'Regional Hub', 'event': 'Arrived at hub'},
                    {'date': '2026-02-06', 'location': 'Local Facility', 'event': 'Out for delivery'}
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
        
        elif action == "View reason for delay":
            return self.show_delay_reason()
        
        elif action == "Get updated delivery estimate":
            return self.get_updated_estimate()
        
        elif action == "Report as lost (if past expected date by 3+ days)":
            return self.file_lost_package_claim()
        
        elif action == "See estimated delivery window":
            return self.show_delivery_window()
        
        elif action == "Arrange to pick up at facility instead":
            return self.arrange_pickup()
        
        return "Action completed."
    
    def show_tracking_history(self):
        # Error handling 
        if self.packageInfo is None:
            return "Unable to retrieve tracking history."
        
        result = f"\n{'='*50}\n"
        result += f"Current Status: {self.packageInfo['status'].replace('_', ' ').title()}\n"
        result += f"Last Known Location: {self.packageInfo.get('lastLocation', 'Unknown')}\n"
        result += f"Estimated Delivery: {self.packageInfo.get('estDelivery', 'Unknown')}\n\n"
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
    
    def show_delay_reason(self):
        return "\nDelay Reason: Weather conditions in transit region\nUpdated estimate: 2-3 days beyond original date"
    
    def get_updated_estimate(self):
        return "\nUpdated delivery estimate: February 10, 2026\nWe apologize for the delay."
    
    def file_lost_package_claim(self):
        # Calculate days since expected delivery based on packageInfo in database
        days_since_expected = 5 # Seed data for testing 
        if days_since_expected >= 3:
            return "\nLost package claim filed.\nReference: LP123456\n\nWe'll issue a refund or send a replacement.\nYou'll receive an email within 24 hours."
        else:
            return f"\nPackage is only {days_since_expected} days past expected delivery.\nWe recommend waiting 3 days before filing a lost claim.\n\nWould you like to speak with a representative?"
    
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

def run_chatbot():
    print("\n" + "="*60)
    print("PACKAGE TRACKING DEMO CHATBOT")
    print("="*60)
    print("\nDemo tracking numbers you can use:")
    print("  • D123 - In transit package")
    print("  • D456 - Delayed package")
    print("  • D789 - Delivered package")
    print("  • D999 - Out for delivery")
    print("  • Any other order number - Generic in-transit package")
    print("\nEmail can be anything valid (e.g., test@email.com)")
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
                else:
                    print("Invalid choice. Please enter 1 or 2.")
        
        userInput = input("\nYour response: ").strip()
        
        is_transfer, message = bot.handle_response(question, userInput)
        
        if message:
            print(message)
        
        if is_transfer:
            return
    
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
            else:
                print("Invalid choice. Please enter 1 or 2.")
    
    # Main action menu loop
    while True:
        userInput = input("\nYour choice: ").strip()
        
        try:
            choice = int(userInput)
            if choice == len(action_question['options']) + 1:
                print("Transferring to representative...")
                break
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

if __name__ == "__main__":
    run_chatbot()