trackingQuestions = [
    {
        'key': 'order_number',
        'prompt': "Please enter your order number:",
        'type': 'text',
        'validator': 'validateOrderNum'
    },
    {
        'key': 'email',
        'prompt': "Please enter the email address for this package:",
        'type': 'text',
        'validator': 'validateEmail'
    }
]

packageStatus = {
    'in_transit': [
        "View current location and tracking history",
        "Check estimated delivery date",
        "Update delivery instructions",
        "Redirect to different address (if available)"
    ],
    'delivered': [
        "Check where package was left",
        "Report package as not received",
        "File a damage claim"
    ],
    'delayed': [
        "View reason for delay",
        "Get updated delivery estimate",
        "Report as lost (if past expected date by 3+ days)"
    ],
    'out_for_delivery': [
        "Update delivery instructions",
        "See estimated delivery window",
        "Arrange to pick up at facility instead"
    ],
    'not_found': [
        "Verify order number and email",
        "Check if order was placed under different email"
    ]
}