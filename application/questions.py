trackingQuestions = [
    {
        'key': 'order_number',
        'prompt': "Hi! I can help you track down your package. Please enter your order number:",
        'type': 'text',
        'validator': 'validateOrderNum'
    },
    {
        'key': 'email',
        'prompt': "Please enter the email address for this order:",
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
        "File a damage/missing claim"
    ],
    'delayed': [
        "Get updated delivery estimate",
        "Request priority shipping refund",
        "Reorder package (no recent updates)"
    ],
    'out_for_delivery': [
        "See estimated delivery window",
        "Update delivery instructions",
        "Arrange to pick up at facility instead"
    ],
    'not_shipped': [
        "View current location and tracking history",
        "Check estimated delivery date",
        "Cancel order (not yet shipped)"
    ],
    'not_found': [
        "Verify order number and email",
        "Check if order was placed under different email"
    ]
}