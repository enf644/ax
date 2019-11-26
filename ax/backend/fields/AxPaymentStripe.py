"""AxPaymentStripe

For AxPaymentStripe to work you need to create intent in AxAction python
code like so  (stripe1)-

    ax.row.stripe1['intent'] = ax.stripe.PaymentIntent.create(
        amount=500,
        currency='usd',
    )



"""
import os


async def before_insert(db_session, field, before_form, tobe_form, action,
                        current_user):
    """ Create default value of field.  """
    del db_session, before_form, tobe_form, action, current_user
    field.value = {
        "pubKey": os.getenv('STRIPE_PUBLISHABLE_KEY'),
        "intent": None
    }

    return field.value
